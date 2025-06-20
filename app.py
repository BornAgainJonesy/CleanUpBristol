import streamlit as st
from google.cloud import storage, vision, firestore
from streamlit_js_eval import get_geolocation
from google.oauth2 import service_account
from PIL import Image
import uuid
import datetime
import io
import platform

# App metadata
st.set_page_config(page_title="CleanUpBristol v1.3.1", layout="centered")
st.title("📸 CleanUpBristol — v1.3.1")
st.write("Upload a street image with optional location to help identify urban waste.")

# 🔍 Attempt to auto-detect location
st.subheader("📍 Auto-Detect Your Location (Optional)")
loc = get_geolocation()

latitude = None
longitude = None

if loc and loc.get("coords"):
    coords = loc["coords"]
    latitude = coords.get("latitude")
    longitude = coords.get("longitude")
    if latitude and longitude:
        st.success(f"📍 Detected location: {latitude:.5f}, {longitude:.5f}")
else:
    # 🧭 Fallback to manual input
    latitude_input = st.text_input("Latitude (optional)")
    longitude_input = st.text_input("Longitude (optional)")
    try:
        latitude = float(latitude_input) if latitude_input else None
        longitude = float(longitude_input) if longitude_input else None
    except ValueError:
        st.warning("⚠️ Please enter valid numeric latitude and longitude.")

# 📤 Image upload UI
uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Preview", use_column_width=True)

    if st.button("🚀 Upload & Analyse"):
        with st.spinner("Uploading to Cloud & Analyzing..."):

            try:
                # Prep image
                image_bytes = uploaded_file.read()
                file_type = uploaded_file.type
                device_info = platform.platform()
                unique_id = str(uuid.uuid4())
                filename = f"uploads/{unique_id}.{uploaded_file.name.split('.')[-1]}"
                timestamp = datetime.datetime.utcnow().isoformat()

                # Load service account credentials from secrets
                creds_dict = st.secrets["gcp"]["credentials"]
                creds = service_account.Credentials.from_service_account_info(creds_dict)
                
                # Upload to GCS
                client = storage.Client(project=st.secrets["gcp"]["project"])
                bucket = client.bucket(st.secrets["gcp"]["bucket"])
                blob = bucket.blob(filename)
                blob.upload_from_string(image_bytes, content_type=file_type)

                # Vision API analysis
                client = storage.Client(project=st.secrets["gcp"]["project"], credentials=creds)
                image = vision.Image(content=image_bytes)
                response = vision_client.label_detection(image=image)
                labels = response.label_annotations
                top_label = labels[0].description if labels else "Unclassified"

                # Log to Firestore
                db = firestore.Client(project=st.secrets["gcp"]["project"], credentials=creds)
                doc_ref = db.collection("uploads").document(unique_id)
                doc_ref.set({
                    "id": unique_id,
                    "timestamp": timestamp,
                    "file_type": file_type,
                    "device": device_info,
                    "gcs_path": filename,
                    "status": "uploaded",
                    "ml_label": top_label,
                    "location": {
                        "lat": latitude,
                        "lng": longitude
                    }
                })

                st.success(f"✅ Uploaded & analysed as: **{top_label}**")
            except Exception as e:
                st.error(f"❌ Something went wrong: {e}")
