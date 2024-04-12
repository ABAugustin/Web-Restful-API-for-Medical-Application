from pydantic import BaseModel

class Pacient(BaseModel):
    id_user: int
    rol: list


