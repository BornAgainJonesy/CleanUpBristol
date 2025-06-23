import streamlit as st
from google.cloud import storage
from PIL import Image
import uuid
import io
import os

st.set_page_config(page_title="CleanUpBristol", layout="centered")

st.title("📸 Upload a Street Image")
st.write("Upload a street scene. It will be saved to your Google Cloud bucket.")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="✅ Uploaded Image", use_column_width=True)

    if st.button("Upload to Cloud"):
        try:
            # Load credentials from secrets.toml
            bucket_name = st.secrets["gcp"]["bucket"]

            # Create GCS client
            client = storage.Client()
            bucket = client.bucket(bucket_name)

            # Generate a unique name
            blob_name = f"uploads/{uuid.uuid4()}.jpg"
            blob = bucket.blob(blob_name)

            # Upload
            blob.upload_from_string(uploaded_file.read(), content_type=uploaded_file.type)

            st.success(f"✅ Uploaded to GCS as: {blob_name}")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
