from pydantic import BaseModel, Field
from flask import url_for



class Doctor(BaseModel):
    id_doctor: int
    id_user: int
    nume: str = Field(max_length=50)
    prenume: str = Field(max_length=50)
    email: str = Field(max_length=70)
    telefon: str = Field(max_length=10)
    specializare: list
