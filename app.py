import streamlit as st
from PIL import Image

st.set_page_config(page_title="CleanUpBristol (Offline)", layout="centered")

st.title("📸 Upload a Street Image")
st.write("Running locally on your network. Upload a photo of a street scene.")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="✅ Uploaded Image", use_column_width=True)
