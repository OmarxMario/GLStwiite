import streamlit as st
import time
from fire_base import db

def login_user(username_input, password_input):
    clean_username = username_input.strip().lower()
    if not clean_username or not password_input:
        return False, "Please enter both your username and password."
        
    try:
        user_doc = db.collection("users").document(clean_username).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            if user_data.get("password") == password_input:
                return True, clean_username
            else:
                return False, "Incorrect password. Please try again."
        else:
            return False, f"The username '{clean_username}' does not exist at GLStwite."
    except Exception as e:
        return False, f"Database connection error: {e}"

def show_sign_in_page():
    st.title("🔑 Sign In to GLStwite",anchor=False)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Login", type="primary"):
            success, message = login_user(username, password)
            if success:
                st.session_state.username = message
                st.query_params["user"] = message
                
                st.components.v1.html(
                    f"""
                    <script>
                    window.parent.localStorage.setItem("glstwite_user", "{message}");
                    </script>
                    """,
                    height=0, width=0
                )
                
                st.success(f"Welcome back, @{message}!", icon="👋")
                time.sleep(0.5)
                st.session_state.page = "feed"
                st.rerun()
            else:
                st.error(message)
    with col2:
        if st.button("Back"):
            st.session_state.page = "landing"
            st.rerun()