import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp

# Дизайн заголовка
st.markdown("<h1 style='text-align: center; color: blue;'>DyfCalc</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Інтегрування та Диференціювання Функцій</h3>", unsafe_allow_html=True)
st.markdown("---")

# Змінна для математичних обчислень
x = sp.symbols('x')

# Бокова панель для вибору операції
with st.sidebar:
    st.header("Налаштування")
    operation = st.selectbox("Оберіть операцію:", ["Інтегрування", "Диференціювання"])

# Введення функції
st.markdown("### 🧮 Введіть функцію:")
user_function = st.text_input("Наприклад, x**2 + 3*x + 1")

# Побудова графіка функції
if user_function:
    function = sp.sympify(user_function)
    if st.checkbox("Показати графік функції"):
        # Перетворення функції на NumPy
        func_np = sp.lambdify(x, function, 'numpy')
        x_vals = np.linspace(-10, 10, 500)  # Вісь X
        y_vals = func_np(x_vals)  # Значення Y

        # Побудова графіка
        fig, ax = plt.subplots()
        ax.plot(x_vals, y_vals, label=f"f(x) = {user_function}")
        ax.set_title("Графік функції")
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
        ax.legend()
        ax.grid()

        st.pyplot(fig)

# Кнопка для обчислень
if st.button("🔍 Обчислити"):
    if user_function:
        function = sp.sympify(user_function)
        if operation == "Інтегрування":
            result = sp.integrate(function, x)
            st.success(f"Інтеграл: {result}")
        elif operation == "Диференціювання":
            result = sp.diff(function, x)
            st.success(f"Похідна: {result}")
        else:
            st.error("Некоректна операція.")
    else:
        st.warning("Будь ласка, введіть функцію.")

# Додатковий стиль для фону
st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6;
    }
    </style>
    """,
    unsafe_allow_html=True
)
