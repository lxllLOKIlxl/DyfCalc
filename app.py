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

# Заголовок із стилем
st.markdown("<h1 style='text-align: center; color: blue;'>🔢 DyfCalc</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Інтегрування та Диференціювання Функцій</h3>", unsafe_allow_html=True)
st.markdown("---")

# Оголошення змінних
x, y, z = sp.symbols('x y z')  # Додані змінні y і z

# Бокова панель із параметрами
with st.sidebar:
    # Лічильник користувачів
    st.header("👥 Користувачі")
    st.markdown(f"![Людина](https://img.icons8.com/emoji/48/null/bust-in-silhouette.png) **{st.session_state['user_count']} користувач(і/ів) онлайн**")
    st.markdown("---")

    # Чат
    st.header("💬 Онлайн-чат")
    for msg in st.session_state['chat_history']:
        st.write(msg)

    # Поле для введення повідомлення
    user_input = st.text_input("Напишіть повідомлення:", key="chat_input")
    if st.button("Відправити", key="send"):
        if user_input.strip():  # Перевірка непорожнього повідомлення
            st.session_state['chat_history'].append(f"Користувач: {user_input}")
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
        # Перетворення функції у SymPy вираз
        function = sp.sympify(user_function)

        # Перевірка ділення на нуль
        if sp.simplify(function).has(sp.zoo) or sp.simplify(function).has(sp.oo):
            raise ZeroDivisionError("Ділення на нуль не допускається!")

        # Підстановка значень для змінних y і z, якщо вони є у функції
        substitutions = {var: 1 for var in [y, z] if var in function.free_symbols}  # Підставляємо 1 тільки для змінних, які присутні
        function = function.subs(substitutions)  # Застосування підстановок

        # Генеруємо числову версію функції
        func_np = sp.lambdify(x, function, 'numpy')

        # Генеруємо числові значення для графіка
        x_vals = np.linspace(-10, 10, 500)
        y_vals = func_np(x_vals)

        # Перевірка лише числових значень
        if not np.isfinite(y_vals).all():
            raise ValueError("Функція має особливі точки або нескінченність!")

        # Знаходження коренів функції
        roots = sp.solve(function, x)
        roots_np = [float(root.evalf()) for root in roots if sp.im(root) == 0]

        if st.checkbox("📊 Показати графік функції"):
            # Побудова графіка
            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label=f"f(x) = {user_function}", color="blue")

            # Додавання точок перетину
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

            ax.set_title("Графік функції", fontsize=14)
            ax.set_xlabel("x", fontsize=12)
            ax.set_ylabel("f(x)", fontsize=12)
            ax.legend(loc="best")
            ax.grid(True)

            st.pyplot(fig)

    except ZeroDivisionError as zde:
        st.error(f"Ви щось зробили не так: {zde}")
    except ValueError as ve:
        st.error(f"Ви щось зробили не так: {ve}")
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

# Фонова стилізація
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
