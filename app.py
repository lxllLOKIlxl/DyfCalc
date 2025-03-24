import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp
import firebase_admin
from firebase_admin import credentials, db
import json
import threading  # Для роботи з потоками
import time

# Функція для завантаження перекладів
def load_translations(lang):
    try:
        with open(f"translations/{lang}.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"Помилка завантаження перекладу: файл '{lang}.json' не знайдено в директорії 'translations'.")
        return {}
    except Exception as e:
        st.error(f"Сталася помилка під час завантаження перекладу: {e}")
        return {}

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
            "text": text,
            "timestamp": int(time.time())  # Додаємо часову мітку для очищення
        }
        ref.push(new_message)
        st.success(translations["update_successful"])
    except Exception as e:
        st.error(f"{translations['error_firebase']}: {e}")

# Функція для отримання повідомлень
def get_messages():
    try:
        ref = db.reference('messages')
        messages = ref.get()
        if messages:
            return [(msg["user"], msg["text"]) for msg in messages.values()]
        return []
    except Exception as e:
        st.error(translations["error_generic"])
        return []

# Функція для автоматичного очищення чату
def auto_clear_chat():
    while True:
        try:
            current_time = int(time.time())
            cutoff_time = current_time - 50  # Повідомлення старше 50 секунд будуть видалені
            ref = db.reference('messages')

            # Видалення повідомлень старше 50 секунд
            old_messages = ref.order_by_child('timestamp').end_at(cutoff_time).get()
            if old_messages:
                for key in old_messages:
                    ref.child(key).delete()

            time.sleep(50)  # Зачекати 50 секунд до наступного очищення
        except Exception as e:
            st.error(f"Помилка очищення чату: {e}")
            break

# Запуск автоматичного очищення чату
if not st.session_state.get("auto_clear_initialized", False):
    threading.Thread(target=auto_clear_chat, daemon=True).start()
    st.session_state["auto_clear_initialized"] = True

# Вибір мови
with st.sidebar:
    st.markdown(
        """
        <style>
            .language-container {
                padding: 10px 0;
                font-family: 'Arial', sans-serif;
                text-align: center;
                font-weight: bold;
                border-bottom: 2px solid #ccc; /* Нижня рисочка */
            }
            .stRadio > div {
                display: flex;
                justify-content: center;
            }
        </style>
        <div class="language-container">
            🌍 Вибір мови / Language:
        </div>
        """,
        unsafe_allow_html=True
    )
    lang = st.radio(
        " ",
        ["uk", "en"],
        index=0,
        horizontal=True
    )
    translations = load_translations(lang)

# Заголовок програми
st.markdown(
    f"""
    <div style='background-color: rgba(255, 255, 255, 0.2); padding: 15px; border-radius: 10px;'>
        <h1 style='text-align: center; color: blue; font-family: Arial, sans-serif; font-weight: bold;'>
            {translations.get('greeting_dyfcalc', 'Вітаємо DyfCalc')}
        </h1>
        <h3 style='text-align: center; color: gray; font-family: Arial, sans-serif;'>
            {translations.get('calculation_prompt_dyfcalc', 'Введіть функцію для обчислення')}
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Бокова панель із параметрами та чатом
with st.sidebar:
    # Секція налаштувань
    st.markdown(
        f"""
        <div style="border: 2px solid #FF9800; border-radius: 10px; padding: 10px; background-color: rgba(255, 152, 0, 0.1);">
            <h4 style="color: #FF9800; text-align: center; font-weight: bold;">
                {translations["settings_title"]}
            </h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    operation = st.radio(translations["operation_prompt"], [translations["integration"], translations["differentiation"]], horizontal=True)
    st.markdown("---")

    # Теми
    st.markdown(
        f"""
        <div style="border: 2px solid #673AB7; border-radius: 10px; padding: 10px; background-color: rgba(103, 58, 183, 0.1);">
            <h4 style="color: #673AB7; text-align: center; font-weight: bold;">
                {translations["theme_prompt"]}
            </h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    theme = st.radio(translations["theme_prompt"], [translations["theme_light"], translations["theme_dark"]], horizontal=True)
    st.markdown("---")

with st.sidebar:
    # Вставте ваш код тут з правильними відступами

    # Секція "Користувачі онлайн"
    st.markdown(
        f"""
        <div style="
            border: 1px solid #D3D3D3; 
            border-radius: 10px; 
            padding: 10px; 
            background: linear-gradient(135deg, rgba(240, 240, 240, 0.9), rgba(255, 255, 255, 0.6));">
            <h5 style="
                color: #333; 
                text-align: center; 
                font-weight: bold; 
                font-family: Arial, sans-serif; 
                font-size: 16px;">
                {translations['online_users']}
            </h5>
            <div style="
                display: flex; 
                align-items: center; 
                justify-content: center; 
                gap: 10px;">
                <img src="https://img.icons8.com/emoji/48/null/bust-in-silhouette.png" alt="User Icon" width="30">
                <span style="
                    font-size: 18px; 
                    color: #555; 
                    font-weight: 600; 
                    font-family: 'Verdana', sans-serif;">
                    {st.session_state.get('user_count', 1)} {translations['online_count']}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Секція чату 
    st.markdown(
        f"""
        <div style="border: 2px solid #2196F3; border-radius: 10px; padding: 10px; background-color: rgba(33, 150, 243, 0.1);">
            <h4 style="color: #2196F3; text-align: center; font-weight: bold;">
                {translations["online_chat"]}
            </h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    user = st.text_input(translations["name_prompt"], key="chat_user_name", placeholder="Ваше ім'я")
    message = st.text_input(translations["message_prompt"], key="chat_user_message", placeholder="Введіть повідомлення")
    if st.button(translations["send_button_chat"], key="chat_send_button"):
        if user.strip() and message.strip():
            send_message(user, message)
        else:
            st.warning(translations["message_warning"])

    st.markdown(f"<h6 style='color: black; font-weight: bold;'>{translations['welcome_chat']}</h6>", unsafe_allow_html=True)
    chat_messages = get_messages()
    if chat_messages:
        for user, text in chat_messages:
            st.markdown(
                f"<div style='margin-bottom: 8px; font-size: 16px; color: black;'><strong>{user}:</strong> {text}</div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(f"<p style='color: gray;'>{translations['no_results']}</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Нижня частина (автор)
    st.markdown(
        f"""
        <div style="text-align: center; color: gray; margin-top: 20px; padding: 10px; border-top: 1px solid #ddd;">
        {translations['project_by']}<br>
        <strong style="font-size: 16px;">Шаблінський С.І.</strong><br>
        <img src="https://img.icons8.com/color/96/null/code.png" alt="Code Icon" width="50">
        </div>
        """,
        unsafe_allow_html=True
    )

# Основна функціональність калькулятора
st.markdown(
    f"<h4>{translations['calculation_prompt']}</h4>",
    unsafe_allow_html=True
)
user_function = st.text_input(translations["input_example"], placeholder=translations["input_example"])

# Побудова графіка функції з перевіркою
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
                ax.scatter(root, 0, color="red", s=50, label=f"Точка перетину: {root:.2f}")
                ax.annotate(
                    f"{root:.2f}",
                    (root, 0),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", edgecolor="red", facecolor="lightyellow")
                )
            ax.set_title("Графік функції", fontsize=16)
            ax.set_xlabel("x", fontsize=14)
            ax.set_ylabel("f(x)", fontsize=14)
            ax.legend(loc="upper left")
            ax.grid(True)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Сталася помилка: {e}")

if st.button(translations["calculate_button"]):
    try:
        if operation == translations["integration"]:
            result = sp.integrate(function, x)
            st.success(f"{translations['integral_result']}: {result}")
        elif operation == translations["differentiation"]:
            result = sp.diff(function, x)
            st.success(f"{translations['derivative_result']}: {result}")
    except Exception as e:
        st.error(f"{translations['error_generic']}: {e}")

# Додатковий стиль
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to bottom, #f0f2f6, #e6ecf3);
    }
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border: none;
        padding: 6px 12px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        border-radius: 8px;
        transition-duration: 0.4s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)
