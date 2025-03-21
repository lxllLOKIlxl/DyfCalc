import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp
import firebase_admin
from firebase_admin import credentials, db
import os
import json

# Створення локального файлу для Firebase ключа
firebase_key_raw = os.getenv("FIREBASE_KEY")
if not firebase_key_raw:
    st.error("FIREBASE_KEY не знайдено у секретах Streamlit Cloud!")
else:
    try:
        firebase_key = json.loads(firebase_key_raw)
        with open("serviceAccountKey.json", "w") as f:
            json.dump(firebase_key, f)
        st.write("Ключ Firebase збережено у файл!")
    except json.JSONDecodeError as e:
        st.error(f"Помилка JSONDecodeError: {e}")

# Ініціалізація Firebase із локального файлу
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")  # Локальний файл
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://dyfcalc-chat-default-rtdb.firebaseio.com/'
        })
        st.write("Firebase успішно ініціалізовано через локальний файл!")
    except ValueError as e:
        st.error(f"Помилка ініціалізації Firebase: {e}")

# Лічильник кількості користувачів онлайн
if 'user_count' not in st.session_state:
    st.session_state['user_count'] = 1
st.session_state['user_count'] += 1

# Чат-функції
def save_message_to_db(user, message):
    ref = db.reference('messages')
    ref.push({'user': user, 'message': message})

def fetch_messages():
    ref = db.reference('messages')
    return ref.get()

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
    user_input = st.text_input("Ваше повідомлення:", key="user_message")
    if st.button("Відправити"):
        if user_input.strip():
            save_message_to_db("Користувач", user_input.strip())  # Збереження у Firebase

    # Отримання повідомлень із Firebase
    messages = fetch_messages()
    if messages:
        for msg_id, msg_data in messages.items():
            st.write(f"{msg_data['user']}: {msg_data['message']}")

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

# Видалення тимчасового файлу
if os.path.exists("serviceAccountKey.json"):
    os.remove("serviceAccountKey.json")
    st.write("Тимчасовий файл із ключем успішно видалено.")

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
