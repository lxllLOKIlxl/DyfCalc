import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp
from firebase_admin import credentials, db, initialize_app

# Firebase налаштування
if not st.session_state.get("firebase_initialized"):
    cred = credentials.Certificate("firebase_credentials.json")  # Замініть на шлях до вашого ключа Firebase
    initialize_app(cred, {"databaseURL": "https://your-database-name.firebaseio.com/"})
    st.session_state["firebase_initialized"] = True

# Доступ до чату в базі даних
chat_ref = db.reference("chat_messages")

# Лічильник кількості користувачів онлайн
if 'user_count' not in st.session_state:
    st.session_state['user_count'] = 1  # Ініціалізація
st.session_state['user_count'] += 1

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
    messages = chat_ref.get() or {}
    for msg in messages.values():
        st.write(msg)

    # Поле для введення повідомлення
    user_input = st.text_input("Напишіть повідомлення:", key="chat_input")
    if st.button("Відправити", key="send"):
        if user_input.strip():  # Перевірка на порожнє значення
            chat_ref.push(f"Користувач: {user_input}")
            user_input = ""  # Очищення поля після відправлення

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

# Основний функціонал
st.markdown(
    """
    <div style="border: 1px solid #ccc; padding: 10px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
    <h4>🧮 Введіть функцію для обчислення:</h4>
    </div>
    """,
    unsafe_allow_html=True
)
user_function = st.text_input("Наприклад, x**2 - 4*x + y + z", placeholder="x**2 - 4*x + y + z")

# Побудова графіка функції
if user_function:
    try:
        function = sp.sympify(user_function)

        # Перевірка ділення на нуль
        if sp.simplify(function).has(sp.zoo) or sp.simplify(function).has(sp.oo):
            raise ZeroDivisionError("Ділення на нуль не допускається!")

        # Підстановка значень для змінних y і z
        substitutions = {var: 1 for var in [y, z] if var in function.free_symbols}
        function = function.subs(substitutions)

        # Генерування числових даних
        func_np = sp.lambdify(sp.symbols('x'), function, 'numpy')
        x_vals = np.linspace(-10, 10, 500)
        y_vals = func_np(x_vals)

        # Відображення графіка
        if st.checkbox("📊 Показати графік функції"):
            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label=f"f(x) = {user_function}", color="blue")
            ax.set_title("Графік функції")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

    except ZeroDivisionError as zde:
        st.error(f"Виникла помилка: {zde}")
    except Exception as e:
        st.error(f"Сталася помилка: {e}")

# Додатковий стиль
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #007BFF; /* Синій колір кнопки */
        color: white;
        font-size: 14px;
        padding: 6px 12px;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
