import streamlit as st
import datetime as dt
from fire_base import db

def register_user(name, password):
    clean_username = name.strip().lower()
    try:
        user_doc = db.collection("users").document(clean_username).get()
        if user_doc.exists:
            return False, "This username is already taken by another student!"
        else:
            db.collection("users").document(clean_username).set({
                "username": clean_username,
                "password": password, 
                "created_at": dt.datetime.utcnow(),
                "verified": False,
                "pfp": "https://cdn-icons-png.flaticon.com/512/149/149071.png",
                "bio": f"Hello, I'm {clean_username} and I'm new to GLStwite!",
                "liked_twites": []
            })
            return True, f"Account created successfully for @{clean_username}!"
            
    except Exception as e:
        return False, f"Database communication failed: {e}"

def show_sign_up_page():
    st.title("📝 Create your GLStwite Account",anchor=False)
    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")
    
    col1, col2 = st.columns([2, 5])
    reg_success = False
    reg_msg = ""

    with col1:
        if st.button("Register Account", type="primary"):
            if new_username and new_password:
                success, message = register_user(new_username, new_password)
                if success:
                    reg_success = True
                    reg_msg = message
                else:
                    st.error(message)
            else:
                st.warning("Please fill out both username and password fields.")
    with col2:
        if st.button("Back"):
            st.session_state.page = "landing"
            st.rerun()
    
    if reg_success:
        st.success(reg_msg, icon="🎉")