import streamlit as st
from google.cloud import storage
from PIL import Image
import io
import uuid

st.set_page_config(page_title="CleanUpBristol", layout="centered")
st.title("📸 Upload a Street Image")
st.write("This prototype uploads an image to Google Cloud Storage for ML processing.")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    if st.button("Upload to Cloud"):
        try:
            image_bytes = uploaded_file.read()

            # Load GCS client
            client = storage.Client()
            bucket_name = st.secrets["gcp"]["bucket"]
            bucket = client.bucket(bucket_name)

            # Create a unique filename
            file_ext = uploaded_file.name.split('.')[-1]
            unique_name = f"uploads/{uuid.uuid4()}.{file_ext}"

            # Upload
            blob = bucket.blob(unique_name)
            blob.upload_from_string(image_bytes, content_type=uploaded_file.type)

            st.success(f"✅ Uploaded to GCS: {unique_name}")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
