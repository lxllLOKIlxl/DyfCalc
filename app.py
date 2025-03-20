import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objs as go

# Заголовок із іконкою
st.markdown("<h1 style='text-align: center;'>🔢 DyfCalc</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Інтегрування та Диференціювання Функцій</h3>", unsafe_allow_html=True)
st.markdown("---")

# Бічне меню із чітким вибором і іконками
st.sidebar.markdown("## 🛠️ Оберіть операцію:")
operation = st.sidebar.radio(
    "",
    ["🧮 Інтегрування", "✂️ Диференціювання"],
    format_func=lambda x: x.split(" ")[1],  # Відображає лише текст після іконки
)

st.sidebar.markdown("---")

# Введення функції
st.markdown("### 🧮 Введіть функцію для обчислення:")
user_function = st.text_input("Введіть функцію тут, наприклад, x**2 - 4*x + 3", placeholder="x**2 - 4*x + 3")

if user_function:
    try:
        x = sp.symbols('x')
        function = sp.sympify(user_function)

        # Кнопка для обчислення
        if st.button("🔍 Обчислити"):
            if "Інтегрування" in operation:
                result = sp.integrate(function, x)
                st.success(f"Інтеграл: {result}")
            elif "Диференціювання" in operation:
                result = sp.diff(function, x)
                st.success(f"Похідна: {result}")

            # Кнопка для побудови графіка
            if st.button("📊 Показати графік"):
                func_np = sp.lambdify(x, function, "numpy")
                x_vals = np.linspace(-10, 10, 500)
                y_vals = func_np(x_vals)

                # Точки перетину
                roots = sp.solve(function, x)
                roots_np = [float(root.evalf()) for root in roots if sp.im(root) == 0]

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
                    template="plotly_white"
                )

                st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Помилка в обчисленнях чи побудові графіка: {e}")
