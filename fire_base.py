import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    # 1. Check if the app is running on the cloud secrets manager
    if "firebase_credentials" in st.secrets:
        # Read the secrets directly out of Streamlit's hidden memory
        cred_dict = dict(st.secrets["firebase_credentials"])
        cred = credentials.Certificate(cred_dict)
    else:
        # 2. Fallback to your local file when developing on your laptop
        cred = credentials.Certificate("fire_base.json")
        
    firebase_admin.initialize_app(cred)

db = firestore.client()
