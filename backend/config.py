import os
import toml

def get_groq_api_key():
    secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".secrets", "secrets.toml")
    secrets = toml.load(secrets_path)
    return secrets["GROQ_API_KEY"]
