import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Ініціалізація Firebase через секрети
cred = credentials.Certificate({
    "type": st.secrets["firebase"]["type"],
    "project_id": st.secrets["firebase"]["project_id"],
    "private_key_id": st.secrets["firebase"]["private_key_id"],
    "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
    "client_email": st.secrets["firebase"]["client_email"],
    "client_id": st.secrets["firebase"]["client_id"],
    "auth_uri": st.secrets["firebase"]["auth_uri"],
    "token_uri": st.secrets["firebase"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
})

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://chatproject-6722b-default-rtdb.firebaseio.com/'
})

# Функція для тестування бази даних
def test_connection():
    try:
        ref = db.reference('test')
        ref.set({"status": "connected"})
        st.success("Підключення до Firebase успішне!")
    except Exception as e:
        st.error(f"Помилка підключення: {e}")

test_connection()
