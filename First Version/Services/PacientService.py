from DTOs.doctor import Doctor as doct
from DTOs.Pacient import Pacient as patt
from flask import Flask, url_for, jsonify
import mysql.connector


app = Flask(__name__)

def connectDB():
    connection = mysql.connector.connect(
        host='localhost',
        database='pos',
        user='user',
        password='pass'
    )
    return connection

def afisarePacient(id:int):
    connected = connectDB()
    if connected.is_connected():
        cursor = connected.cursor(dictionary=True)
        query = "SELECT cnp, id_user, id_user, nume, prenume, email, telefon,data_nasterii,is_active FROM date_pacienti WHERE id_user = " + id
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            new_patt = patt(cnp=row['cnp'],
                            id_user=row['id_user'],
                            nume=row['nume'],
                            prenume=row['prenume'],
                            email=row['email'],
                            telefon=row['telefon'],
                            data_nasterii=row['data_nasterii'],
                            is_active=row['is_active'])

            cursor.close()
            connected.close()
            return new_patt
        else:
            return "No such Patient with such id"

def afisarePacienti():
    connected = connectDB()
    if connected.is_connected():

        cursor = connected.cursor(dictionary=True)
        query = "SELECT cnp, id_user, id_user, nume, prenume, email, telefon,data_nasterii,is_active FROM date_pacienti"
        cursor.execute(query)
        rows = cursor.fetchall()
        dtos = []
        for row in rows:
            # Create DTO objects and fill them with data from the database
            new_patt = patt(cnp=row['cnp'],
                           id_user=row['id_user'],
                           nume=row['nume'],
                           prenume=row['prenume'],
                           email=row['email'],
                           telefon=row['telefon'],
                           data_nasterii=row['data_nasterii'],
                           is_active=row['is_active'])
            dtos.append(new_patt)
        cursor.close()
        connected.close()
        return dtos
    else:
        return "no values"


def afisareDocsFromPat(id):
    connected = connectDB()
    if connected.is_connected():
        cursor = connected.cursor(dictionary=True)
        query = "SELECT date_doctori.* FROM date_doctori JOIN programari_consultatii ON date_doctori.id_doctor = programari_consultatii.id_doctor WHERE programari_consultatii.id_pacient =" + id
        cursor.execute(query)
        rows = cursor.fetchall()
        dtos = []
        for row in rows:
            # Create DTO objects and fill them with data from the database
            new_doc = doct(id_doctor=row['id_doctor'],
                           id_user=row['id_user'],
                           nume=row['nume'],
                           prenume=row['prenume'],
                           email=row['email'],
                           telefon=row['telefon'],
                           specializare=row['specializare'].split(', '))
            dtos.append(new_doc)
        cursor.close()
        connected.close()
        return dtos
    else:
        return "no values"

############################################### HATEOAS ###########################################

def add_hateoas_links_1(patt):
    patt_dict = patt.dict()
    patt_dict["links"] = {
        "self": url_for("get_one_patient", id=patt.id_user, _external=True),
        "parent": url_for("get_all_patients", _external=True),
    }
    return patt_dict


def add_hateoas_links_2_single(doct, id_user):
    doct_dict = doct.dict()
    doct_dict["links"] = {
        "self": url_for("get_doctors_of_patient_id", id=id_user, _external=True),
        "parent": url_for("get_one_patient", id=id_user, _external=True),
    }
    return doct_dict


def add_hateoas_links_2(doct, id_user):
    if isinstance(doct, list):
        return [add_hateoas_links_2_single(p, id_user) for p in doct]
    else:
        return add_hateoas_links_2_single(doct, id_user)


############################################### HATEOAS ###########################################


@app.get('/api/medical_office/patients/')
def get_all_patients():
    docs = afisarePacienti()

    if isinstance(docs, str):
        return docs

    jsondocs = [add_hateoas_links_1(doc) for doc in docs]
    return jsonify({"patients": jsondocs})


@app.get("/api/medical_office/patients/<id>")
def get_one_patient(id: int):
    docs = afisarePacient(id)
    if isinstance(docs, str):
        return docs

    return jsonify(add_hateoas_links_1(docs))

@app.get("/api/medical_office/patients/<id>/physicians")
def get_doctors_of_patient_id(id: int):
    docs = afisareDocsFromPat(id)
    if isinstance(docs, str):
        return docs
    return jsonify(add_hateoas_links_2(docs, id))