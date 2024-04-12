from sqlite3 import Date
from pydantic import BaseModel,Field



class Pacient(BaseModel):
    cnp: str = Field(max_length=13 , min_length=13)
    id_user: int
    nume: str = Field(max_length=50)
    prenume: str = Field(max_length=50)
    email: str = Field(max_length=70)
    telefon: str = Field(max_length=10)
    data_nasterii: Date
    is_active: bool

