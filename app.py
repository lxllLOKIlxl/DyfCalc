import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

# Тимчасове тестування завантаження секретів
st.write(st.secrets["firebase"])

# Підключення Firebase через Streamlit secrets
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

# Функції для роботи з Firebase
def save_message(user, message):
    ref = db.reference('messages')  # Посилання на базу даних
    ref.push({
        'user': user,
        'message': message
    })

def fetch_messages():
    ref = db.reference('messages')  # Посилання на базу даних
    return ref.get() or {}

# Лічильник кількості користувачів онлайн
if 'user_count' not in st.session_state:
    st.session_state['user_count'] = 1
st.session_state['user_count'] += 1

# Історія чату (оновлюється через Firebase)
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = fetch_messages()

# Функція для відправки повідомлення
def send_message():
    if "user_message" in st.session_state and st.session_state["user_message"].strip():
        save_message("Користувач", st.session_state["user_message"].strip())
        st.session_state['chat_history'] = fetch_messages()
        st.session_state["user_message"] = ""

# Заголовок із стилем
st.markdown("<h1 style='text-align: center; color: blue;'>🔢 DyfCalc</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Інтегрування та Диференціювання Функцій</h3>", unsafe_allow_html=True)
st.markdown("---")

# Бокова панель із параметрами
with st.sidebar:
    # Лічильник користувачів
    st.header("👥 Користувачі")
    st.markdown(f"![Людина](https://img.icons8.com/emoji/48/null/bust-in-silhouette.png) **{st.session_state['user_count']} користувач(і/ів) онлайн**")
    st.markdown("---")

    # Чат
    st.header("💬 Онлайн-чат")
    chat_history = st.session_state['chat_history']
    for msg_id, msg_data in chat_history.items():
        st.write(f"{msg_data['user']}: {msg_data['message']}")

    # Поле для введення повідомлення
    st.text_input("Ваше повідомлення:", value="", key="user_message")
    st.button("Відправити", on_click=send_message)

    st.markdown("---")
    st.header("🔧 Налаштування")
    operation = st.radio("Оберіть операцію:", ["Інтегрування", "Диференціювання"])
    st.markdown("---")
    st.header("🎨 Оформлення")
    theme = st.radio("Оберіть тему:", ["Світла", "Темна"])
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: gray;">
        Програма ver 1.0 • Студент 1 курсу Шаблінський С.І.
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

        # Перевірка ділення на нуль
        if sp.simplify(function).has(sp.zoo) or sp.simplify(function).has(sp.oo):
            raise ValueError("Функція має нескінченні значення!")

        # Підстановка значень для змінних y і z
        substitutions = {var: 1 for var in [y, z] if var in function.free_symbols}
        function = function.subs(substitutions)

        # Генерація числових даних
        func_np = sp.lambdify(x, function, "numpy")
        x_vals = np.linspace(-10, 10, 500)
        y_vals = func_np(x_vals)

        # Знаходження коренів функції
        roots = sp.solve(function, x)
        roots_np = [float(root.evalf()) for root in roots if sp.im(root) == 0]

        # Побудова графіка
        if st.checkbox("📊 Показати графік функції"):
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(x_vals, y_vals, label=f"f(x) = {user_function}", color="blue")

            # Додавання точок перетину
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

    except ValueError as ve:
        st.error(f"Помилка: {ve}")
    except Exception as e:
        st.error(f"Сталася помилка: {e}")

# Кнопка для обчислення
if st.button("🔍 Обчислити"):
    try:
        # Інтегрування або диференціювання
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
