import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp
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

# Лічильник кількості користувачів онлайн
if 'user_count' not in st.session_state:
    st.session_state['user_count'] = 1
st.session_state['user_count'] += 1

# Вибір мови
with st.sidebar:
    lang = st.radio("🌍 Вибір мови / Language:", ["uk", "en"], index=0, horizontal=True)
    translations = load_translations(lang)

# Заголовок із стилем
st.markdown("<h1 style='text-align: center; color: blue;'>🔢 DyfCalc</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Інтегрування та Диференціювання Функцій</h3>", unsafe_allow_html=True)
st.markdown("---")

# Бокова панель із параметрами і чатом
with st.sidebar:
    # Лічильник користувачів
    st.header("👥 Користувачі онлайн")
    st.markdown(f"![Людина](https://img.icons8.com/emoji/48/null/bust-in-silhouette.png) **{st.session_state['user_count']} користувач(і/ів)**")
    st.markdown("---")

    # Чат
    st.header("💬 Онлайн-чат")
    user = st.text_input("Ваше ім'я", key="user_name_chat")
    message = st.text_input("Ваше повідомлення", key="user_message_chat")
    if st.button("Відправити", key="send_button_chat"):
        if user.strip() and message.strip():
            send_message(user, message)
        else:
            st.warning("Будь ласка, заповніть усі поля!")

    st.write("### Повідомлення:")
    chat_messages = get_messages()
    if chat_messages:
        for user, text in chat_messages:
            st.write(f"**{user}:** {text}")
    else:
        st.write("Наразі немає повідомлень.")
    st.markdown("---")

    # Налаштування
    st.header("🔧 Налаштування")
    operation = st.radio("Оберіть операцію:", ["Інтегрування", "Диференціювання"])
    st.markdown("---")
    st.header("🎨 Оформлення")
    theme = st.radio("Оберіть тему:", ["Світла", "Темна"])
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: gray;">
        Програма ver 1.0 • Запатентовано розробником Sm
        </div>
        """, unsafe_allow_html=True
    )

# Введення функції
st.markdown(
    """
    <div style="border: 1px solid #ccc; padding: 10px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
    <h4>🧮 Введіть функцію для обчислення:</h4>
    </div>
    """,
    unsafe_allow_html=True
)
user_function = st.text_input("Наприклад, x**2 - 4*x + y + z", placeholder="x**2 - 4*x + y + z")

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

        if st.checkbox("📊 Показати графік функції"):
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

# Кнопка для обчислення
if st.button("🔍 Обчислити"):
    try:
        if operation == "Інтегрування":
            result = sp.integrate(function, x)
            st.success(f"Інтеграл: {result}")
        elif operation == "Диференціювання":
            result = sp.diff(function, x)
            st.success(f"Похідна: {result}")
    except Exception as e:
        st.error(f"Сталася помилка обчислення: {e}")

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
