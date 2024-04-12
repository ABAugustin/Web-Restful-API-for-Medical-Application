from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Programari(BaseModel):
    id_pacient: int
    id_doctor: int
    data: str
    status: list


@app.get("/")
def Mesaj():
    return {"Hello World"}
