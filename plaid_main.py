from fastapi import FastAPI
from plaid_service import client

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI + Plaid API"}

@app.post("/link_token")
def create_link_token():
    response = client.LinkToken.create({
        'user': {'client_user_id': 'unique-user-id'},
        'client_name': 'Plaid Test App',
        'products': ['auth'],
        'country_codes': ['US'],
        'language': 'en',
    })
    return response
