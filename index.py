import streamlit as st
import datetime as dt
from sign_in import show_sign_in_page
from sign_up import show_sign_up_page
from fire_base import db

st.set_page_config(page_title="GLStwite", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "username" not in st.session_state:
    st.session_state.username = None

user_data = None
@st.dialog("📝 Edit Your Bio")
def edit_bio_dialog(current_bio):
    new_bio = st.text_area("Write something about yourself...", value=current_bio, max_chars=160)
    if st.button("Save Bio", type="primary"):
        if st.session_state.username:
            db.collection("users").document(st.session_state.username).update({"bio": new_bio})
            st.toast("Bio updated successfully! 🎉")
            st.rerun()

@st.dialog("🖼️ Change Profile Picture")
def change_pfp_dialog(current_pfp):
    new_pfp = st.text_input("Paste image URL:", value=current_pfp)
    if st.button("Update Picture", type="primary"):
        if st.session_state.username and new_pfp.startswith(("http://", "https://")):
            db.collection("users").document(st.session_state.username).update({"pfp": new_pfp})
            st.toast("Profile picture updated! 📸")
            st.rerun()
        else:
            st.error("Please enter a valid image URL starting with https://")

@st.dialog("🚀 Post a new GLStwite")
def upload_twite_dialog():
    twite_content = st.text_area("What do you wanna share?", max_chars=280)
    if st.button("Post it!", type="primary"):
        if twite_content.strip() == "":
            st.warning("Your post cannot be empty.")
        elif st.session_state.username:
            n=""
            if user_data and user_data.get("verified", False):
                n = f"{st.session_state.username} ✅"
            else:
                n = st.session_state.username
            db.collection("twites").add({
                "author": n,
                "content": twite_content,
                "created_at": dt.datetime.utcnow(),
                "likes": 0
            })
            st.toast("Posted to the feed successfully! 🍦")
            st.rerun()

def show_landing_page():
    st.title("GLStwite", anchor=False)
    st.write(
        "A local social media app created for the students of Golf Language School "
        "to post and share their experiences and thoughts."
    )
    
    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        if st.button("Sign In", key="sign_in"):
            st.session_state.page = "sign_in"
            st.rerun()
    with col2:
        if st.button("Sign Up", key="sign_up"):
            st.session_state.page = "sign_up"
            st.rerun()

def show_feed_page():
    st.title("GLStwite", anchor=False)
    st.write(f"Logged in securely as: **@{st.session_state.username}**")
    
    tab1, tab2, tab3 = st.tabs(["🏠 Home", "👤 Profile", "⚙️ Settings"])
    
    with tab1:
        st.subheader("🏠 Home Feed",anchor=False)
        try:
            twites_ref = db.collection("twites").order_by("created_at", direction="DESCENDING").limit(20).stream()
            twite_list = [t.to_dict() for t in twites_ref]
            
            if not twite_list:
                st.info("No GLStwites posted yet. Be the first to post on the profile tab!")
            else:
                for twite in twite_list:
                    with st.container(border=True):
                        st.markdown(f"**@{twite.get('author')}**")
                        st.write(twite.get("content"))
                        st.caption(f"Posted on {twite.get('created_at').strftime('%Y-%m-%d %H:%M') if twite.get('created_at') else 'Just Now'}")
        except Exception:
            st.info("The feed is currently quiet. Start posting to build up the school board!")

    with tab2:
        col1, col2 = st.columns([1, 4])
        with col1:
            pfp_url = user_data.get("pfp", "https://cdn-icons-png.flaticon.com/512/149/149071.png") if user_data else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
            st.image(pfp_url, width=110)
        with col2:
            name_col, verify_col = st.columns([len(st.session_state.username) + 2, 10], vertical_alignment="center")
            with name_col:
                st.subheader(f"@{st.session_state.username}", anchor=False)
            with verify_col:
                if user_data and user_data.get("verified", False):
                    st.markdown("<h3>✅</h3>", unsafe_allow_html=True)
            
            st.write(f"*{user_data.get('bio', 'No bio available.') if user_data else 'No bio available.'}*")
        
        st.write("")
        col3, col4, col5 = st.columns([1, 1, 1.5])
        with col3:
            if st.button("📝 Edit Bio", use_container_width=True):
                edit_bio_dialog(user_data.get("bio", "") if user_data else "")
        with col4:
            if st.button("🖼️ Change PFP", use_container_width=True):
                change_pfp_dialog(user_data.get("pfp", "") if user_data else "")
        with col5:
            if st.button("🚀 Post a GLStwite", type="primary", use_container_width=True):
                upload_twite_dialog()
        
        st.divider()
        st.subheader("📋 My Posts",anchor=False)
        try:
            all_posts_ref = db.collection("twites").stream()
            
            my_posts_list = []
            for post in all_posts_ref:
                p_data = post.to_dict()
                
                if user_data and user_data.get("verified", False):
                    if str(p_data.get("author"))[:-2] == st.session_state.username:
                        p_data["id"] = post.id
                        my_posts_list.append(p_data)
                else:
                    if str(p_data.get("author")) == st.session_state.username:
                        p_data["id"] = post.id
                        my_posts_list.append(p_data)
            my_posts_list.sort(key=lambda x: x.get("created_at") if x.get("created_at") else 0, reverse=True)
            
            if not my_posts_list:
                st.info("You haven't uploaded any GLStwites yet!")
            else:
                for data in my_posts_list:
                    with st.container(border=True):
                        post_txt_col, delete_btn_col = st.columns([5, 1])
                        
                        with post_txt_col:
                            st.write(data.get("content"))
                            try:
                                st.caption(f"🕒 {data.get('created_at').strftime('%Y-%m-%d %H:%M')}")
                            except:
                                st.caption("🕒 Recent")
                                
                        with delete_btn_col:
                            if st.button("🗑️", key=f"del_prof_{data['id']}", help="Delete this post"):
                                db.collection("twites").document(data["id"]).delete()
                                st.toast("Post deleted successfully! 💥")
                                import time
                                time.sleep(0.5)
                                st.rerun()
        except Exception as e:
            st.error(f"Error loading your profile posts: {e}")

    with tab3:
        st.subheader("⚙️ Account Settings",anchor=False)
        st.write("Manage your local school application authentication data layers.")
        
        if st.button("Log Out", type="secondary"):
            st.session_state.username = None
            st.session_state.page = "landing"
            st.query_params.clear()

            st.components.v1.html(
                """
                <script>
                window.parent.localStorage.removeItem("glstwite_user");
                window.parent.location.reload();
                </script>
                """,
                height=0, width=0
            )
            st.rerun()

def main():
    global user_data
    st.components.v1.html(
        """
        <script>
        const user = window.parent.localStorage.getItem("glstwite_user");
        const urlParams = new URLSearchParams(window.parent.location.search);
        if (user && !urlParams.has("user")) {
            urlParams.set("user", user);
            window.parent.location.search = urlParams.toString();
        }
        </script>
        """,
        height=0, width=0
    )

    param_user = st.query_params.get("user")
    if param_user and st.session_state.username is None:
        st.session_state.username = param_user
        st.session_state.page = "feed"

    if st.session_state.username:
        try:
            user_doc = db.collection("users").document(st.session_state.username).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
        except Exception as e:
            st.error(f"Database connection error: {e}")
            user_data = None

    if st.session_state.page == "landing":
        show_landing_page()
    elif st.session_state.page == "sign_in":
        show_sign_in_page()
    elif st.session_state.page == "sign_up":
        show_sign_up_page()
    elif st.session_state.page == "feed":
        show_feed_page()

if __name__ == "__main__":
    main()