from array import array

from pydantic import BaseModel
from typing import List

class DateInvestigatii(BaseModel):
    _id: str
    denumire: str
    durata_de_procesare: int
    rezultat: str

class DateConsultatii(BaseModel):
    id: str
    id_pacient: int
    id_doctor: int
    data: str
    diagnostic: str
    investigatii: list[DateInvestigatii]

