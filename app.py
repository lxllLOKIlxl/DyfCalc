import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp

# Заголовок із іконкою та стилем
st.markdown("<h1 style='text-align: center; color: blue;'>🔢 DyfCalc</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Інтегрування та Диференціювання Функцій</h3>", unsafe_allow_html=True)
st.markdown("---")

# Бокова панель із секціями меню
with st.sidebar:
    st.header("🔧 Налаштування")
    operation = st.radio("Оберіть операцію:", ["🧮 Інтегрування", "✂️ Диференціювання"])
    st.markdown("---")
    st.header("🎨 Оформлення")
    theme = st.radio("Оберіть тему:", ["Світла", "Темна"])
    st.markdown("---")

# Введення функції з рамкою та тінями
st.markdown(
    """
    <div style="border: 1px solid #ccc; padding: 10px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
    <h4>🧮 Введіть функцію для обчислення:</h4>
    </div>
    """,
    unsafe_allow_html=True
)
user_function = st.text_input("Наприклад, x**2 - 4*x + 3", placeholder="x**2 - 4*x + 3")

# Побудова графіка функції з точками перетину та анімацією
if user_function:
    try:
        function = sp.sympify(user_function)
        if st.checkbox("📊 Показати графік функції"):
            func_np = sp.lambdify(x, function, 'numpy')
            x_vals = np.linspace(-10, 10, 500)
            y_vals = func_np(x_vals)

            # Знаходження точок перетину
            roots = sp.solve(function, x)
            roots_np = [float(root.evalf()) for root in roots if sp.im(root) == 0]

            # Побудова графіка
            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label=f"f(x) = {user_function}", color="blue")

            # Анімація точок перетину
            for root in roots_np:
                ax.scatter(root, 0, color="red", label=f"Точка перетину: {root:.2f}")
                ax.annotate(
                    f"{root:.2f}",
                    (root, 0),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", edgecolor="blue", facecolor="lightyellow")
                )

            ax.set_title("Графік функції з точками перетину", fontsize=14, color="black")
            ax.set_xlabel("Вісь X", fontsize=12)
            ax.set_ylabel("Вісь Y", fontsize=12)
            ax.legend(loc="best")
            ax.grid(True, linestyle="--", alpha=0.7)

            st.pyplot(fig)
    except Exception as e:
        st.error(f"Помилка побудови графіка: {e}")

# Кнопка для обчислень
if user_function and st.button("🔍 Обчислити"):
    try:
        if "Інтегрування" in operation:
            result = sp.integrate(function, x)
            st.success(f"Інтеграл: {result}")
        elif "Диференціювання" in operation:
            result = sp.diff(function, x)
            st.success(f"Похідна: {result}")
        else:
            st.error("Некоректна операція.")
    except Exception as e:
        st.error(f"Помилка обчислення: {e}")

# Фонова стилізація
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to bottom, #f0f2f6, #e6ecf3);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        border-radius: 12px;
        transition-duration: 0.4s;
    }
    .stButton>button:hover {
        background-color: white;
        color: black;
        border: 2px solid #4CAF50;
    }
    </style>
    """,
    unsafe_allow_html=True
)
