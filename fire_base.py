import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

@st.cache_resource
def init_firebase():
    try:
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass
    return firestore.client()

db = init_firebase()