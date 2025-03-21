import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp

# Лічильник кількості користувачів онлайн (локальний підрахунок у сесії)
if 'user_count' not in st.session_state:
    st.session_state['user_count'] = 1
st.session_state['user_count'] += 1

# Історія повідомлень у чаті
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Ініціалізуємо поле для введення
if 'chat_input' not in st.session_state:
    st.session_state['chat_input'] = ""

# Заголовок із стилем
st.markdown("<h1 style='text-align: center; color: blue;'>🔢 DyfCalc</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Інтегрування та Диференціювання Функцій</h3>", unsafe_allow_html=True)
st.markdown("---")

# Бокова панель
with st.sidebar:
    # Лічильник
    st.header("👥 Користувачі")
    st.markdown(f"Кількість онлайн: **{st.session_state['user_count']}**")
    st.markdown("---")

    # Чат
    st.header("💬 Онлайн-чат")
    for msg in st.session_state['chat_history']:
        st.write(msg)

    # Поле для введення повідомлення
    user_input = st.text_input("Ваше повідомлення:", value=st.session_state['chat_input'], key="chat_input")
    if st.button("Відправити"):
        if user_input.strip():  # Перевірка на непорожнє введення
            st.session_state['chat_history'].append(f"Користувач: {user_input.strip()}")
            st.session_state['chat_input'] = ""  # Скидання поля введення

# Введення функції
st.markdown("### Введіть функцію для обчислення:")
user_function = st.text_input("Наприклад: x**2 - 4*x + y + z")

# Графік
if user_function:
    try:
        x, y, z = sp.symbols('x y z')
        function = sp.sympify(user_function)

        # Перевірка коректності функції
        if sp.simplify(function).has(sp.zoo) or sp.simplify(function).has(sp.oo):
            raise ValueError("Некоректна функція - має нескінченні значення!")

        # Заміна символів
        function = function.subs({y: 1, z: 1})

        # Генерація графіка
        func_np = sp.lambdify(x, function, "numpy")
        x_vals = np.linspace(-10, 10, 500)
        y_vals = func_np(x_vals)

        if st.checkbox("Показати графік"):
            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label=f"f(x) = {user_function}", color="blue")
            ax.axhline(0, color="black", linewidth=0.8, linestyle="--")  # Горизонтальна вісь
            ax.axvline(0, color="black", linewidth=0.8, linestyle="--")  # Вертикальна вісь
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Помилка: {e}")

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
