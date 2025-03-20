import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp

# Заголовок із оновленим стилем
st.markdown("<h1 style='text-align: center; color: blue;'>DyfCalc</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Інтегрування та Диференціювання Функцій</h3>", unsafe_allow_html=True)
st.markdown("---")

# Змінна для математичних обчислень
x = sp.symbols('x')

# Бокова панель для вибору операції
with st.sidebar:
    st.header("🔧 Налаштування")
    operation = st.radio("Оберіть операцію:", ["Інтегрування", "Диференціювання"])

# Введення функції
st.markdown("### 🧮 Введіть функцію для обчислення:")
user_function = st.text_input("Наприклад, x**2 + 3*x + 1", placeholder="x**2 + 3*x + 1")

# Побудова графіка функції
if user_function:
    try:
        function = sp.sympify(user_function)
        if st.checkbox("📊 Показати графік функції"):
            # Перетворення функції на NumPy
            func_np = sp.lambdify(x, function, 'numpy')
            x_vals = np.linspace(-10, 10, 500)  # Вісь X
            y_vals = func_np(x_vals)  # Значення Y

            # Побудова графіка
            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label=f"f(x) = {user_function}", color="blue")
            ax.set_title("Графік функції", fontsize=14, color="black")
            ax.set_xlabel("x", fontsize=12)
            ax.set_ylabel("f(x)", fontsize=12)
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.7)

            st.pyplot(fig)
    except Exception as e:
        st.error(f"Помилка побудови графіка: {e}")

# Кнопка для обчислень
if user_function and st.button("🔍 Обчислити"):
    try:
        function = sp.sympify(user_function)
        if operation == "Інтегрування":
            result = sp.integrate(function, x)
            st.success(f"Інтеграл: {result}")
        elif operation == "Диференціювання":
            result = sp.diff(function, x)
            st.success(f"Похідна: {result}")
        else:
            st.error("Некоректна операція.")
    except Exception as e:
        st.error(f"Помилка обчислення: {e}")

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
