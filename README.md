# CleanUpBristol

A community-driven web app to help identify and report street litter and refuse across Bristol using image uploads and machine learning.

## 🚀 Purpose

This prototype app allows users to upload street images, which are stored in a Google Cloud Storage bucket. These images will later be analysed using ML models to detect types of litter, overflowing bins, and other urban hygiene issues.

The long-term goal is to gamify participation and provide league tables, rewards, and potentially work with local authorities for automated reporting.

---

## 🌐 Live App

👉 [Click here to open CleanUpBristol](https://your-username-cleanupbristol.streamlit.app)

---

## ✅ Features (v1.0)

- Upload `.jpg`, `.jpeg`, or `.png` images via browser or mobile
- Securely stores images in GCS (`street-cleanup-images` bucket)
- Unique filename generation using UUID
- Friendly UI using [Streamlit](https://streamlit.io/)

---

## 🏗 Project Structure
