import streamlit as st
import requests
from datetime import datetime

# Configuration de l'API (adresse locale FastAPI)
API_URL = "http://127.0.0.1:8000"

# Page d'authentification utilisateur
def login_user(email, password):
    response = requests.post(f"{API_URL}/auth/jwt/login", data={"username": email, "password": password})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Invalid login credentials.")
        return None

# Page d'enregistrement utilisateur
def register_user(email, password, full_name):
    response = requests.post(f"{API_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": full_name
    })
    if response.status_code == 201:
        st.success("User registered successfully!")
    else:
        st.error("Failed to register user.")

# Afficher les vidéos
def display_videos():
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_URL}/api/", headers=headers)
    if response.status_code == 200:
        videos = response.json()
        for video in videos:
            st.write(f"**Title**: {video['title']}")
            st.write(f"**Description**: {video['description']}")
            st.write(f"**Published at**: {video['published_at']}")
            st.write(f"**Transcript**: {video['transcript']}")
            st.markdown(f"[YouTube Link]({video['video_url']})")
            st.markdown("---")
    else:
        st.error("Failed to fetch videos.")

# Ajouter une nouvelle vidéo
def add_video():
    st.subheader("Add a new YouTube video")
    youtube_url = st.text_input("YouTube Video URL")
    title = st.text_input("Title")
    description = st.text_area("Description")
    published_at = st.date_input("Published At", datetime.now())

    if st.button("Add Video"):
        token = st.session_state.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        data = {
            "youtube_url": youtube_url,
            "title": title,
            "description": description,
            "published_at": published_at.isoformat()
        }
        
        response = requests.post(f"{API_URL}/api/", headers=headers, json=data)
        if response.status_code == 200:
            st.success("Video added successfully!")
        else:
            st.error("Failed to add video.")

# Gérer la page principale
def main():
    st.title("WhisperWatch Dashboard")

    # Authentification utilisateur
    if "token" not in st.session_state:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login_data = login_user(email, password)
            if login_data:
                st.session_state["token"] = login_data["access_token"]
    else:
        st.sidebar.title("Menu")
        option = st.sidebar.radio("Navigation", ["View Videos", "Add Video", "Logout"])

        if option == "View Videos":
            st.subheader("Videos")
            display_videos()
        elif option == "Add Video":
            add_video()
        elif option == "Logout":
            st.session_state.pop("token")
            st.success("Logged out successfully!")

if __name__ == "__main__":
    main()
