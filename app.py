import streamlit as st
from google.cloud import storage, vision, firestore
from streamlit_geolocation import geolocation
location = geolocation()
from PIL import Image
import uuid
import datetime
import io
import platform

st.set_page_config(page_title="CleanUpBristol v1.3", layout="centered")
st.title("📸 CleanUpBristol — v1.3 (Geo + ML)")
st.write("Upload a street image to help detect and track urban waste.")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

# Get geolocation from browser
location = geolocation()

if uploaded_file:
    st.image(uploaded_file, caption="Preview", use_column_width=True)

    if st.button("🚀 Upload & Analyse"):
        with st.spinner("Uploading to Cloud & Analyzing..."):

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

            # Log to Firestore
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
                    "lat": location["latitude"] if location else None,
                    "lng": location["longitude"] if location else None
                }
            })

            st.success(f"✅ Uploaded & analysed as: **{top_label}**")
