from fastapi import FastAPI
from plaid_service import client
from pydantic import BaseModel
from typing import Dict, Any

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

# User sign-up model
class SignUpRequest(BaseModel):
    email: str
    password: str
    name: str

# Quiz submission model
class QuizSubmission(BaseModel):
    user_id: str
    answers: Dict[str, Any]

@app.post("/signup")
def signup(user: SignUpRequest):
    # TODO: Add user registration logic (e.g., save to DB)
    return {"message": "User registered successfully", "user": user}

@app.post("/quiz")
def submit_quiz(quiz: QuizSubmission):
    # TODO: Add quiz submission logic (e.g., save to DB)
    return {"message": "Quiz submitted successfully", "quiz": quiz}
