import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Ініціалізація Firebase з перевіркою
if not firebase_admin._apps:
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
        'databaseURL': st.secrets["firebase"]["databaseURL"]
    })

# Функція для надсилання повідомлень
def send_message(user, text):
    try:
        ref = db.reference('messages')
        new_message = {
            "user": user,
            "text": text
        }
        ref.push(new_message)
        st.success("Повідомлення надіслано!")
    except Exception as e:
        st.error(f"Помилка надсилання повідомлення: {e}")

# Функція для отримання повідомлень
def get_messages():
    try:
        ref = db.reference('messages')
        messages = ref.get()
        if messages:
            return [(msg["user"], msg["text"]) for msg in messages.values()]
        return []
    except Exception as e:
        st.error(f"Помилка отримання даних: {e}")
        return []

# Інтерфейс чату
st.title("Чат з Firebase")

user = st.text_input("Ваше ім'я")
message = st.text_input("Введіть повідомлення")

if st.button("Надіслати"):
    if user and message:
        send_message(user, message)
    else:
        st.warning("Будь ласка, заповніть усі поля!")

st.write("### Повідомлення:")
messages = get_messages()
for user, text in messages:
    st.write(f"**{user}:** {text}")
