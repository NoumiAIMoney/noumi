import os
from plaid import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(
    client_id=os.getenv("PLAID_CLIENT_ID"),
    secret=os.getenv("PLAID_SECRET"),
    environment=os.getenv("PLAID_ENV"),
)
