import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp
import firebase_admin
from firebase_admin import credentials, db
import json
import time  # Для роботи з часовими мітками

# Функція для завантаження файлів перекладу
def load_language(lang):
    with open(f"translations/{lang}.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Ініціалізація Firebase з перевіркою
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
    })
    firebase_admin.initialize_app(cred, {
        'databaseURL': st.secrets["firebase"]["databaseURL"]
    })

# Функція для відправки повідомлення в Firebase
def send_message():
    if "user_message" in st.session_state and "user_name" in st.session_state:
        user = st.session_state["user_name"]
        text = st.session_state["user_message"]
        try:
            ref = db.reference('messages')
            new_message = {
                "user": user,
                "text": text,
                "timestamp": int(time.time())  # Час у UNIX-форматі
            }
            ref.push(new_message)
            st.success("Повідомлення надіслано!")
            st.session_state["user_message"] = ""  # Очищення поля після відправки
        except Exception as e:
            st.error(f"Помилка надсилання повідомлення: {e}")
    else:
        st.warning("Будь ласка, введіть ім'я та текст!")

# Функція для отримання повідомлень із Firebase
def get_messages():
    try:
        current_time = int(time.time())
        cutoff_time = current_time - 40  # Видалення повідомлень старше 40 секунд
        ref = db.reference('messages')

        # Видалення старих повідомлень
        old_messages = ref.order_by_child('timestamp').end_at(cutoff_time).get()
        if old_messages:
            for key in old_messages:
                ref.child(key).delete()

        # Отримання актуальних повідомлень
        messages = ref.order_by_child('timestamp').start_at(cutoff_time).get()
        if messages:
            return [(msg["user"], msg["text"]) for msg in messages.values()]
        return []
    except Exception as e:
        st.error(f"Помилка отримання даних: {e}")
        return []

# Лічильник користувачів
if 'user_count' not in st.session_state:
    st.session_state['user_count'] = 1
st.session_state['user_count'] += 1

# Вибір мови
with st.sidebar:
    # Радіо-кнопка для вибору мови без заголовка
    lang_choice = st.radio("", ["uk", "en"], key="language_radio")  # Тільки кнопки

    # Завантаження перекладу після вибору мови
    translations = load_language(lang_choice)

    # Стилізована секція для "Мова інтерфейсу"
    st.markdown(
        f"""
        <div style="background-color: rgba(240, 240, 240, 0.5); padding: 6px 10px; border-radius: 14px; border: 1px solid rgba(200, 200, 200, 0.5); margin-bottom: 10px; text-align: center;">
            <h4 style="margin: 0; color: #000; font-family: Arial, sans-serif;">🌍 {translations['interface_language']}</h4>
        </div>
        <hr style="border: none; border-top: 1px solid rgba(180, 180, 180, 0.8); margin: 8px 0;">
        """,
        unsafe_allow_html=True
    )

# Заголовок із стилем
st.markdown(f"<h1 style='text-align: center; color: blue;'>🔢 {translations['greeting']} DyfCalc</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: gray;'>{translations['calculation_prompt']}</h3>", unsafe_allow_html=True)
st.markdown("---")

# Бокова панель із параметрами та чатом
with st.sidebar:
    # Лічильник користувачів із емодзі 👥
    st.markdown(
        f"""
        <div style="background-color: rgba(230, 245, 230, 0.8); padding: 8px; border-radius: 12px; border: 1px solid rgba(200, 200, 200, 0.6); margin-bottom: 10px; text-align: center;">
            <h4 style="margin: 0; color: #333; font-family: Arial, sans-serif;">👥 {translations['online_users']}</h4>
            <p style="margin: 0; font-size: 16px; color: #000; font-weight: bold;">👤 {st.session_state['user_count']} {translations['online_count']}</p>
        </div>
        <hr style="border: none; border-top: 1px solid rgba(180, 180, 180, 0.8); margin: 8px 0;">
        """,
        unsafe_allow_html=True
    )

    # Налаштування
    st.header(f"🔧 {translations['settings_title']}")  # Динамічний заголовок

    # Динамічні радіо-кнопки для операцій
    operation = st.radio(
        translations["operation_prompt"], 
        [translations["integration"], translations["differentiation"]],  # Локалізовані значення
        key="operation_radio"
    )

    # Динамічні радіо-кнопки для теми
    theme = st.radio(
        translations["theme_prompt"], 
        [translations["theme_light"], translations["theme_dark"]],  # Локалізовані значення
        key="theme_radio"
    )

    st.markdown("---")

    # Чат у боковій панелі
with st.sidebar:
    # Заголовок чату
    st.header(f"💬 {translations['online_chat']}")

    # Відображення повідомлень
    messages = get_messages()
    if messages:  # Якщо є повідомлення
        for user, text in messages:
            st.write(f"**{user}:** {text}")
    else:
        st.write("Наразі немає повідомлень.")  # Коректний текст для порожнього чату

    # Поле для введення імені
    user_name = st.text_input(
        translations["name_prompt"], 
        key="user_name"
    )

    # Тимчасова змінна для роботи з введеним текстом
    user_message = st.text_input(
        translations["message_prompt"], 
        key="user_message",
        value=""  # Ініціалізація поля як порожнього для кожного рендера
    )

    # Кнопка для відправки повідомлення
    if st.button(translations["send_button_chat"]):  # Використання правильного ключа "Відправити"
        if not user_name.strip():  # Перевірка, чи введено ім'я
            st.warning(translations["name_warning"])
        elif not user_message.strip():  # Перевірка, чи введено повідомлення
            st.warning(translations["message_warning"])
        else:
            send_message()  # Виклик функції для відправки повідомлення
            st.text_input(  # Оновлюємо поле для вводу
                translations["message_prompt"], 
                key="user_message",
                value=""  # Очищення після відправки
            )

    # Додати інформацію про автора
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: gray;">
        {translations['project_by']}<br>
        <b>Студент 1 курсу ІПЗ-24-1-if</b><br>
        <b>Шаблінський С.І.</b>
        </div>
        """, unsafe_allow_html=True
    )

# Введення функції
st.markdown(
    f"""
    <div style="border: 1px solid #ccc; padding: 10px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
    <h4>🧮 {translations['calculation_prompt']}</h4>
    </div>
    """,
    unsafe_allow_html=True
)
user_function = st.text_input(translations["input_example"], placeholder="x**2 - 4*x + y + z")

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

        # Перевірка розмірності масивів x та y
        if len(x_vals) != len(y_vals):
            raise ValueError("Опа, вибачте, ви напевне помилилися у функції! Спробуйте перевірити її синтаксис або логіку.")

        # Знаходження коренів функції
        roots = sp.solve(function, x)
        roots_np = [float(root.evalf()) for root in roots if sp.im(root) == 0]

        # Побудова графіка
        if st.checkbox(translations["plot_function"]):
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
        st.error(f"Опа, вибачте, сталася неочікувана помилка: {e}")

# Кнопка для обчислення інтегралу або похідної
if st.button("🔍 Обчислити"):
    try:
        if operation == "Інтегрування":
            result = sp.integrate(function, x)
            st.success(f"**Інтеграл:** {result}")
        elif operation == "Диференціювання":
            result = sp.diff(function, x)
            st.success(f"**Похідна:** {result}")
    except Exception as e:
        st.error(f"Опа, вибачте, сталася помилка під час обчислення. Можливо, ваша функція некоректна: {e}")

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
