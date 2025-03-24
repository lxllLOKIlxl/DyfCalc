import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp
import firebase_admin
from firebase_admin import credentials, db
import json

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
            "text": text
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

# Вибір мови
with st.sidebar:
    lang = st.radio("🌍 Вибір мови / Language:", ["uk", "en"], index=0, horizontal=True)
    translations = load_translations(lang)

# Заголовок
st.markdown(f"<h1 style='text-align: center; color: blue;'>{translations['greeting']} DyfCalc</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: gray;'>{translations['calculation_prompt']}</h3>", unsafe_allow_html=True)
st.markdown("---")

# Бокова панель із параметрами та чатом
with st.sidebar:
    st.header(f"{translations['online_users']}")
    st.markdown(f"![User Icon](https://img.icons8.com/emoji/48/null/bust-in-silhouette.png) **{st.session_state.get('user_count', 1)} {translations['online_count']}**")
    st.markdown("---")

    st.header(translations["online_chat"])
    user = st.text_input(translations["name_prompt"], key="chat_user_name")
    message = st.text_input(translations["message_prompt"], key="chat_user_message")
    if st.button(translations["send_button_chat"], key="chat_send_button"):
        if user.strip() and message.strip():
            send_message(user, message)
        else:
            st.warning(translations["message_warning"])

    st.write(f"### {translations['welcome_chat']}")
    chat_messages = get_messages()
    if chat_messages:
        for user, text in chat_messages:
            st.write(f"**{user}:** {text}")
    else:
        st.write(translations["no_results"])
    st.markdown("---")

    st.header(translations["settings_title"])
    operation = st.radio(translations["operation_prompt"], [translations["integration"], translations["differentiation"]])
    st.markdown("---")
    st.header(translations["theme_prompt"])
    theme = st.radio(translations["theme_prompt"], [translations["theme_light"], translations["theme_dark"]])
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: gray;">
        {translations['project_by']}<br>
        Програма ver 1.0
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
