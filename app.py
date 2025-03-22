import streamlit as st

# Простий список для збереження повідомлень локально
chat_history = []

# Заголовок чату
st.title("Локальний онлайн-чат")

# Інтерфейс користувача
user = st.text_input("Ваше ім'я")
message = st.text_input("Введіть повідомлення")

# Надсилання повідомлення
if st.button("Надіслати"):
    if user and message:
        chat_history.append(f"**{user}:** {message}")
        st.success("Повідомлення надіслано!")
    else:
        st.warning("Заповніть усі поля!")

# Відображення історії чату
st.write("### Повідомлення:")
for msg in chat_history:
    st.write(msg)
