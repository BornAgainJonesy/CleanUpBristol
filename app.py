import streamlit as st
from google.cloud import storage
from PIL import Image
import uuid
import datetime
import platform
import json
from google.oauth2 import service_account

creds_dict = json.loads(st.secrets["gcp"]["credentials"])
creds = service_account.Credentials.from_service_account_info(creds_dict)

# App setup
st.set_page_config(page_title="CleanUpBristol v1.2", layout="centered")
st.title("📸 CleanUpBristol — v1.2")
st.write("Upload a street image to help identify urban waste.")

# Upload UI
uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Preview", use_column_width=True)

    if st.button("🚀 Upload to Cloud"):
        with st.spinner("Uploading..."):
            try:
                # Prepare metadata
                image_bytes = uploaded_file.read()
                file_type = uploaded_file.type
                device_info = platform.platform()
                unique_id = str(uuid.uuid4())
                filename = f"uploads/{unique_id}.{uploaded_file.name.split('.')[-1]}"
                timestamp = datetime.datetime.utcnow().isoformat()

                # Upload to GCS
                client = storage.Client(project=st.secrets["gcp"]["project"])
                bucket = client.bucket(st.secrets["gcp"]["bucket"])
                blob = bucket.blob(filename)
                blob.upload_from_string(image_bytes, content_type=file_type)

                st.success(f"✅ Uploaded to GCS: {filename}")
            except Exception as e:
                st.error(f"❌ Error uploading: {e}")
                
