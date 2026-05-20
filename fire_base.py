import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    # 1. Check if running on Streamlit Cloud Secrets
    if "firebase_credentials" in st.secrets:
        # Convert the Streamlit secrets object into a clean Python dictionary
        cred_dict = dict(st.secrets["firebase_credentials"])
        cred = credentials.Certificate(cred_dict)
    else:
        # 2. Fallback for your local computer
        cred = credentials.Certificate("fire_base.json")
        
    firebase_admin.initialize_app(cred)

db = firestore.client()
