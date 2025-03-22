import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "chatproject-6722b",
    "private_key_id": "ваш_private_key_id",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nВАШ ПРИВАТНИЙ КЛЮЧ\\n-----END PRIVATE KEY-----\\n",
    "client_email": "firebase-adminsdk-fbsvc@chatproject-6722b.iam.gserviceaccount.com",
    "client_id": "773472907651",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc@chatproject-6722b.iam.gserviceaccount.com"
})
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://chatproject-6722b-default-rtdb.firebaseio.com/'
})
)

# Функція для тестування підключення до Firebase
def test_firebase_connection():
    try:
        ref = db.reference('test')
        ref.set({"status": "connected"})
        st.success("Підключення до Firebase успішне!")
    except Exception as e:
        st.error(f"Помилка підключення до Firebase: {e}")

# Інтерфейс додатку Streamlit
st.title("DyfCalc")
if st.button("Перевірити підключення до Firebase"):
    test_firebase_connection()
