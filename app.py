import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objs as go

# Дизайн заголовка
st.markdown("<h1 style='text-align: center; color: blue;'>DyfCalc</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Інтегрування та Диференціювання Функцій з Анімацією</h3>", unsafe_allow_html=True)
st.markdown("---")

# Змінна для математичних обчислень
x = sp.symbols('x')

# Вибір операції
operation = st.sidebar.selectbox("Оберіть операцію:", ["Інтегрування", "Диференціювання"])

# Введення функції
st.markdown("### 🧮 Введіть функцію:")
user_function = st.text_input("Наприклад, x**2 - 4*x + 3")

if user_function:
    function = sp.sympify(user_function)

    # Показати динамічний графік
    if st.checkbox("Показати анімований графік"):
        func_np = sp.lambdify(x, function, "numpy")
        x_vals = np.linspace(-10, 10, 500)
        y_vals = func_np(x_vals)

        # Створення точок перетину
        roots = sp.solve(function, x)
        roots_np = [float(root.evalf()) for root in roots if sp.im(root) == 0]

        # Графік функції
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=f"f(x) = {user_function}"))

        # Анімація точок перетину
        for root in roots_np:
            fig.add_trace(go.Scatter(x=[root], y=[func_np(root)], mode='markers+text',
                                     marker=dict(size=10, color='red'),
                                     text=f"Root: {root:.2f}",
                                     textposition="top center",
                                     name="Точка перетину"))

        fig.update_layout(
            title="Анімований графік з точками перетину",
            xaxis_title="x",
            yaxis_title="f(x)",
            showlegend=True,
            template="plotly_white"
        )

        st.plotly_chart(fig)

    # Обчислення обраної операції
    if st.button("🔍 Обчислити"):
        if operation == "Інтегрування":
            result = sp.integrate(function, x)
            st.success(f"Інтеграл: {result}")
        elif operation == "Диференціювання":
            result = sp.diff(function, x)
            st.success(f"Похідна: {result}")
