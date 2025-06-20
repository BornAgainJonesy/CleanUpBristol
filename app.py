import streamlit as st
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials, firestore
from PIL import Image
import uuid
from datetime import datetime
import io
import os

# 🔐 Load secrets
bucket_name = st.secrets["gcp"]["bucket"]
firebase_key_path = st.secrets["firebase"]["credentials"]

# 🧠 Initialize Firebase Admin
if not firebase_admin._apps:
import json
if not firebase_admin._apps:
    cred_dict = json.loads(st.secrets["firebase"]["credentials"])
    cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)db = firestore.client()

# 🌐 App UI
st.set_page_config(page_title="CleanUpBristol", layout="centered")
st.title("📸 Upload a Street Image")
st.write("Upload an image of a dirty street and help us clean up Bristol!")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Preview", use_column_width=True)

    if st.button("Upload to Cloud"):
        try:
            # 📸 Read file
            image_bytes = uploaded_file.read()
            file_type = uploaded_file.type
            filename = uploaded_file.name

            # 🧠 Generate metadata
            unique_id = str(uuid.uuid4())
            upload_time = datetime.utcnow().isoformat()
            gcs_path = f"uploads/{unique_id}_{filename}"

            # ☁️ Upload to GCS
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(gcs_path)
            blob.upload_from_string(image_bytes, content_type=file_type)

            # 📝 Prepare metadata
            metadata = {
                "uuid": unique_id,
                "upload_time": upload_time,
                "image_gcs_url": f"gs://{bucket_name}/{gcs_path}",
                "file_type": file_type,
                "device_info": st.session_state.get("user_agent", "unknown"),
                "location": None,
                "user_id": None,
                "labels": [],
                "status": "uploaded"
            }

            # 🔥 Write to Firestore
            db.collection("uploads").document(unique_id).set(metadata)

            st.success("✅ Uploaded and metadata logged!")
            st.write(f"GCS Path: `{gcs_path}`")

        except Exception as e:
            st.error(f"⚠️ Upload failed: {e}")
