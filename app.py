from firebase_admin import db
import streamlit as st

# Функція для надсилання повідомлення
def send_message(user, text):
    ref = db.reference('messages')
    new_message = {
        "user": user,
        "text": text
    }
    ref.push(new_message)
    st.success("Повідомлення надіслано!")
# Функція для отримання повідомлень
def get_messages():
    ref = db.reference('messages')
    messages = ref.get()
    if messages:
        return [(msg["user"], msg["text"]) for msg in messages.values()]
    return []
# Інтерфейс чату
st.title("Онлайн-чат")

user = st.text_input("Ваше ім'я")
message = st.text_input("Введіть повідомлення")

if st.button("Надіслати"):
    if user and message:
        send_message(user, message)
    else:
        st.warning("Заповніть усі поля!")

st.write("### Повідомлення:")
messages = get_messages()
for user, text in messages:
    st.write(f"**{user}:** {text}")
