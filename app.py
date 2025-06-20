import streamlit as st
from google.cloud import storage, vision, firestore
from PIL import Image
import uuid
import datetime
import io
import platform

from streamlit_js_eval import get_geolocation

from streamlit_js_eval import get_geolocation

st.subheader("📍 Auto-Detect Your Location (Optional)")
loc = get_geolocation()

latitude = None
longitude = None

if loc and loc.get("coords"):
    coords = loc["coords"]
    latitude = coords.get("latitude")
    longitude = coords.get("longitude")
    if latitude is not None and longitude is not None:
        st.success(f"Detected location: {latitude:.5f}, {longitude:.5f}")
else:
    latitude_input = st.text_input("Latitude (if not auto-filled)")
    longitude_input = st.text_input("Longitude (if not auto-filled)")
    try:
        latitude = float(latitude_input) if latitude_input else None
        longitude = float(longitude_input) if longitude_input else None
    except ValueError:
        st.warning("Please enter valid latitude and longitude numbers.")
# Upload UI
uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

from streamlit_geolocation import st_geolocation

st.subheader("📍 Your Location (Optional)")
location = st_geolocation()

if location:
    latitude = location["latitude"]
    longitude = location["longitude"]
else:
    latitude = None
    longitude = None
    
if uploaded_file:
    st.image(uploaded_file, caption="Preview", use_column_width=True)

    if st.button("🚀 Upload & Analyse"):
        with st.spinner("Uploading to Cloud & Analyzing..."):

            # Prep image data
            image_bytes = uploaded_file.read()
            file_type = uploaded_file.type
            device_info = platform.platform()
            unique_id = str(uuid.uuid4())
            filename = f"uploads/{unique_id}.{uploaded_file.name.split('.')[-1]}"
            timestamp = datetime.datetime.utcnow().isoformat()

            # Upload to GCS
            client = storage.Client()
            bucket = client.bucket(st.secrets["gcp"]["bucket"])
            blob = bucket.blob(filename)
            blob.upload_from_string(image_bytes, content_type=file_type)

            # ML Analysis using Cloud Vision
            vision_client = vision.ImageAnnotatorClient()
            image = vision.Image(content=image_bytes)
            response = vision_client.label_detection(image=image)
            labels = response.label_annotations
            top_label = labels[0].description if labels else "Unclassified"

            # Firestore Logging
            db = firestore.Client()
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
                    "lat": float(latitude) if latitude else None,
                    "lng": float(longitude) if longitude else None
                }
            })

            st.success(f"✅ Uploaded & analysed as: **{top_label}**")
