from pydantic import BaseModel, Field

class Programari(BaseModel):
    id_pacient: int
    id_doctor: int
    data: str
    status: list
