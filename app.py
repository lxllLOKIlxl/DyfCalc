import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp
import firebase_admin
from firebase_admin import credentials, db
import json
import time

# Функція для завантаження файлів перекладу
def load_language(lang):
    with open(f"translations/{lang}.json", "r", encoding="utf-8") as file:
        return json.load(file)

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

# Функція для відправки повідомлення в Firebase
def send_message():
    try:
        user = st.session_state["user_name"]
        text = st.session_state["user_message"]
        if not user.strip() or not text.strip():
            return  # Якщо поле порожнє, повідомлення не надсилається

        ref = db.reference('messages')
        new_message = {
            "user": user,
            "text": text,
            "timestamp": int(time.time())
        }
        ref.push(new_message)
        st.session_state["user_message"] = ""  # Очищення поля після відправки
        st.success("Повідомлення надіслано!")
    except Exception as e:
        st.error(f"Помилка надсилання повідомлення: {e}")

# Функція для отримання повідомлень із Firebase
def get_messages():
    try:
        current_time = int(time.time())
        cutoff_time = current_time - 40
        ref = db.reference('messages')

        old_messages = ref.order_by_child('timestamp').end_at(cutoff_time).get()
        if old_messages:
            for key in old_messages:
                ref.child(key).delete()

        messages = ref.order_by_child('timestamp').start_at(cutoff_time).get()
        return [(msg["user"], msg["text"]) for msg in messages.values()] if messages else []
    except Exception as e:
        st.error(f"Помилка отримання даних: {e}")
        return []

# Лічильник користувачів
if 'user_count' not in st.session_state:
    st.session_state['user_count'] = 1
st.session_state['user_count'] += 1

# Вибір мови
with st.sidebar:
    lang_choice = st.radio("", ["uk", "en"], key="language_radio")
    translations = load_language(lang_choice)

    st.markdown(
        f"""
        <div style="text-align: center; color: gray;">
        <h4>🌍 {translations['interface_language']}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

# Заголовок
st.title(f"🔢 {translations['greeting']} DyfCalc")
st.subheader(translations['calculation_prompt'])

# Чат у боковій панелі
with st.sidebar:
    st.header("💬 Онлайн-чат")
    messages = get_messages()
    if messages:
        for user, text in messages:
            st.write(f"**{user}:** {text}")
    else:
        st.write("Наразі немає повідомлень.")

    user_name = st.text_input(translations["name_prompt"], key="user_name")
    user_message = st.text_input(translations["message_prompt"], key="user_message", value="")
    if st.button(translations["send_button_chat"]):
        send_message()

# Блок калькулятора функцій
user_function = st.text_input(translations["input_example"], placeholder="x**2 - 4*x + y + z")
if user_function:
    try:
        x, y, z = sp.symbols('x y z')
        function = sp.sympify(user_function)
        substitutions = {var: 1 for var in [y, z] if var in function.free_symbols}
        function = function.subs(substitutions)

        func_np = sp.lambdify(x, function, "numpy")
        x_vals = np.linspace(-10, 10, 500)
        y_vals = func_np(x_vals)

        roots = sp.solve(function, x)
        roots_np = [float(root.evalf()) for root in roots if sp.im(root) == 0]

        if st.checkbox(translations["plot_function"]):
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(x_vals, y_vals, label=f"f(x) = {user_function}", color="blue")
            for root in roots_np:
                ax.scatter(root, 0, color="red", s=50)
                ax.annotate(
                    f"{root:.2f}",
                    (root, 0),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", edgecolor="red", facecolor="lightyellow")
                )
            ax.set_title("Графік функції")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Помилка: {e}")

if st.button("🔍 Обчислити"):
    try:
        if "operation_radio" in st.session_state and st.session_state["operation_radio"] == "Інтегрування":
            result = sp.integrate(function, x)
            st.success(f"Інтеграл: {result}")
        elif "operation_radio" in st.session_state and st.session_state["operation_radio"] == "Диференціювання":
            result = sp.diff(function, x)
            st.success(f"Похідна: {result}")
    except Exception as e:
        st.error(f"Помилка обчислення: {e}")

# Додатковий стиль
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to bottom, #f0f2f6, #e6ecf3);
    }
    .stButton>button {
        background-color: #007BFF; /* Синій колір кнопки */
        color: white;
        border: none;
        padding: 6px 12px; /* Розмір кнопки */
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px; /* Розмір тексту */
        margin: 4px 2px;
        border-radius: 8px;
        transition-duration: 0.4s;
    }
    .stButton>button:hover {
        background-color: #0056b3; /* Темніше синій при наведенні */
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)
