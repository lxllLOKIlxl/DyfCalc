import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objs as go

# Заголовок із іконкою
st.markdown("<h1 style='text-align: center;'>🔢 DyfCalc</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Інтегрування та Диференціювання Функцій</h3>", unsafe_allow_html=True)
st.markdown("---")

# Бічне меню із іконками
st.sidebar.markdown("## 🛠️ Опції:")
operation = st.sidebar.selectbox("Оберіть операцію:", ["Інтегрування", "Диференціювання"])
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 Теми:")
theme = st.sidebar.radio("Оберіть тему:", ["Світла", "Темна"])

# Введення функції
st.markdown("### 🧮 Введіть функцію для обчислення:")
user_function = st.text_input("Введіть функцію тут, наприклад, x**2 - 4*x + 3", placeholder="x**2 - 4*x + 3")

# Покращення: Додавання кнопок
if st.button("Показати графік") and user_function:
    x = sp.symbols('x')
    function = sp.sympify(user_function)
    func_np = sp.lambdify(x, function, "numpy")
    x_vals = np.linspace(-10, 10, 500)
    y_vals = func_np(x_vals)

    # Точки перетину
    roots = sp.solve(function, x)
    roots_np = [float(root.evalf()) for root in roots if sp.im(root) == 0]

    # Побудова графіка з урахуванням теми
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=f"f(x) = {user_function}"))

    for root in roots_np:
        fig.add_trace(go.Scatter(x=[root], y=[func_np(root)], mode='markers+text',
                                 marker=dict(size=10, color='red'),
                                 text=f"Root: {root:.2f}",
                                 textposition="top center",
                                 name="Точка перетину"))

    fig.update_layout(
        title="Графік функції з точками перетину",
        xaxis_title="x",
        yaxis_title="f(x)",
        template="plotly_dark" if theme == "Темна" else "plotly_white"
    )

    st.plotly_chart(fig)

# Виконання операції
if user_function and st.button("🔍 Обчислити"):
    x = sp.symbols('x')
    function = sp.sympify(user_function)
    if operation == "Інтегрування":
        result = sp.integrate(function, x)
        st.success(f"Інтеграл: {result}")
    elif operation == "Диференціювання":
        result = sp.diff(function, x)
        st.success(f"Похідна: {result}")
