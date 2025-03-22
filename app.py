[firebase]
type = "service_account"
project_id = "chatproject-6722b"
private_key_id = "your_private_key_id"
private_key = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADAN...
-----END PRIVATE KEY-----
""".replace("\\n", "\n")
client_email = "your_client_email"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/v1/certs"
client_x509_cert_url = "your_client_x509_cert_url"
