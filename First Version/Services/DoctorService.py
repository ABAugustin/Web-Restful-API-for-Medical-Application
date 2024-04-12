from DTOs.doctor import Doctor as doct
from DTOs.Pacient import Pacient as patt
from flask import Flask, url_for, jsonify,request
import mysql.connector
from flasgger import Swagger

app = Flask(__name__)


def connectDB():
    connection = mysql.connector.connect(
        host='localhost',
        database='pos',
        user='user',
        password='pass'
    )
    return connection


def afisareDoctori():
    connected = connectDB()
    if connected.is_connected():

        cursor = connected.cursor(dictionary=True)
        query = "SELECT id_doctor, id_user, nume, prenume, email, telefon, specializare FROM date_doctori"
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


def afisareDoctor(id):
    connected = connectDB()
    if connected.is_connected():
        cursor = connected.cursor(dictionary=True)
        query = "SELECT id_doctor, id_user, nume, prenume, email, telefon, specializare FROM date_doctori WHERE id_doctor = " + id
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            new_doc = doct(id_doctor=row['id_doctor'],
                           id_user=row['id_user'],
                           nume=row['nume'],
                           prenume=row['prenume'],
                           email=row['email'],
                           telefon=row['telefon'],
                           specializare=row['specializare'].split(', '))
            cursor.close()
            connected.close()
            return new_doc
        else:
            return "No such Doctor with such id"

def afisarePatFromDoc(dct_id: int):
    connected = connectDB()
    if connected.is_connected():
        cursor = connected.cursor(dictionary=True)
        query = "SELECT date_pacienti.* FROM date_pacienti JOIN programari_consultatii ON date_pacienti.id_user = programari_consultatii.id_pacient JOIN date_doctori ON programari_consultatii.id_doctor = date_doctori.id_doctor WHERE date_doctori.id_doctor = " + dct_id
        cursor.execute(query)
        rows = cursor.fetchall()
        dtos = []
        for row in rows:
            # Create DTO objects and fill them with data from the database
            new_patt = patt(
                cnp=row['cnp'],
                id_user=row['id_user'],
                nume=row['nume'],
                prenume=row['prenume'],
                email=row['email'],
                telefon=row['telefon'],
                data_nasterii=row['data_nasterii'],
                is_active=row['is_active']
            )
            dtos.append(new_patt)
        cursor.close()
        connected.close()
        return dtos
    else:
        return "no values"

def afisareDoctorDupaSpecializare(specialization):
    connected = connectDB()

    if connected.is_connected():
        cursor = connected.cursor(dictionary=True)
        query = "SELECT date_doctori.* FROM date_doctori WHERE '"+ specialization +"' IN (date_doctori.specializare)"
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

def get_doctor_by_name_aprox(appname):
    connected = connectDB()

    if connected.is_connected():
        cursor = connected.cursor(dictionary=True)
        query = "SELECT * FROM date_doctori WHERE nume LIKE '"+appname+"%'"
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

def add_hateoas_links_1(doctor):
    doctor_dict = doctor.dict()
    doctor_dict["links"] = {
        "self": url_for("get_one_doctor", id=doctor.id_doctor, _external=True),
        "parent": url_for("get_all_physicians", _external=True),
    }
    return doctor_dict


def add_hateoas_links_2_single(patt, id_doctor):
    patt_dict = patt.dict()
    patt_dict["links"] = {
        "self": url_for("get_patients_of_doctor_id", id=id_doctor, _external=True),
        "parent": url_for("get_one_doctor", id=id_doctor, _external=True),
    }
    return patt_dict


def add_hateoas_links_2(patt, id_doctor):
    if isinstance(patt, list):
        return [add_hateoas_links_2_single(p, id_doctor) for p in patt]
    else:
        return add_hateoas_links_2_single(patt, id_doctor)


############################################### HATEOAS ###########################################


Swagger(app)

@app.route("/api/medical_office/physicians/<id>", methods=['GET'])
def get_one_doctor(id: int):
    """
    Get details of a specific doctor

    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the doctor
    responses:
      200:
        description: Doctor details
    """
    docs = afisareDoctor(id)
    if isinstance(docs, str):
        return docs

    return jsonify(add_hateoas_links_1(docs))

@app.get("/api/medical_office/physicians/<id>/patients")
def get_patients_of_doctor_id(id: int):
    """
    Get patients of a specific doctor

    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The ID of the doctor
    responses:
      200:
        description: List of patients
    """
    docs = afisarePatFromDoc(id)
    if isinstance(docs, str):
        return docs
    return jsonify(add_hateoas_links_2(docs, id))

@app.get("/api/medical_office/physicians")
def get_physicians_by_specialization():
    """
    Get doctors by specialization

    ---
    parameters:
      - name: specialization
        in: query
        type: string
        required: true
        description: The specialization of the doctors
    responses:
      200:
        description: List of doctors
    """
    specialization = request.args.get('specialization')
    docs = afisareDoctorDupaSpecializare(specialization)
    if isinstance(docs, str):
        return docs

    jsondocs = [add_hateoas_links_1(doc) for doc in docs]
    return jsonify({"physicians": jsondocs})

@app.get("/api/medical_office/physicians/")
def search_physicians_by_name():
    """
    Search doctors by name

    ---
    parameters:
      - name: name
        in: query
        type: string
        required: true
        description: The name to search for
    responses:
      200:
        description: List of doctors
    """
    search_name = request.args.get('name', '')
    docs = get_doctor_by_name_aprox(search_name)

    if isinstance(docs, str):
        return docs

    jsondocs = [add_hateoas_links_1(doc) for doc in docs]
    return jsonify({"physicians": jsondocs})

@app.get('/api/medical_office/physicians/')
def get_all_physicians():
    """
    Get all physicians

    ---
    responses:
      200:
        description: List of doctors
    """
    docs = afisareDoctori()

    if isinstance(docs, str):
        return docs

    jsondocs = [add_hateoas_links_1(doc) for doc in docs]
    return jsonify({"physicians": jsondocs})