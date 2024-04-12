import json
import random

from DTOs.doctor import Doctor as doct
from DTOs.Pacient import Pacient as patt
from flask import Flask, url_for, jsonify,request
import mysql.connector
from flasgger import Swagger
from pymongo import MongoClient

app = Flask(__name__)
id_doctor_count = 4
id_user_count = 9
############################################### Maria ###########################################

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
        if dtos.__len__() == 0:
            return "no values"
        else:
            return dtos


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
        query = "SELECT date_pacienti.* FROM date_pacienti JOIN date_programari ON date_pacienti.id_user = date_programari.id_pacient JOIN date_doctori ON date_programari.id_doctor = date_doctori.id_doctor WHERE date_doctori.id_doctor = " + dct_id
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
        if dtos.__len__() == 0:
            return "no values"
        else:
            return dtos

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
        if dtos.__len__() == 0:
            return "no values"
        else:
            return dtos

def get_new_doctor_id():
    connected = connectDB()

    if connected.is_connected():
        cursor = connected.cursor()
        query = "SELECT COUNT(*) FROM date_doctori"
        cursor.execute(query)
        row = cursor.fetchone()[0]
        cursor.close()
        connected.close()
        return int(row) + 1

def get_new_user_id():
    connected = connectDB()

    if connected.is_connected():
        cursor = connected.cursor()
        query = "SELECT COUNT(*) FROM IDM_Utilizatori"
        cursor.execute(query)
        row = cursor.fetchone()[0]
        cursor.close()
        connected.close()
        return int(row) + 1


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
        return docs,404

    return jsonify(add_hateoas_links_1(docs)), 200

@app.route("/api/medical_office/physicians/<id>/patients", methods=['GET'])
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
        return docs,404
    return jsonify(add_hateoas_links_2(docs, id)),200

@app.route("/api/medical_office/physicians", methods=['GET'])
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
        return docs,404

    jsondocs = [add_hateoas_links_1(doc) for doc in docs]
    return jsonify({"physicians": jsondocs}),200

@app.route("/api/medical_office/physicians/", methods=['GET'])
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
        return docs,404

    jsondocs = [add_hateoas_links_1(doc) for doc in docs]
    return jsonify({"physicians": jsondocs}),200

@app.route('/api/medical_office/physicians/', methods=['GET'])
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
        return docs,404

    jsondocs = [add_hateoas_links_1(doc) for doc in docs]
    return jsonify({"physicians": jsondocs}),200

@app.route('/api/medical_office/add_physician',methods=['POST'])
def add_new_physician():
    """
    Adaugă un medic în baza de date.

    ---
    tags:
      - Medic
    parameters:
      - name: nume
        in: formData
        type: string
        required: true
        description: Numele medicului
      - name: prenume
        in: formData
        type: string
        required: true
        description: Prenumele medicului
      - name: email
        in: formData
        type: string
        required: true
        description: Adresa de email a medicului
      - name: telefon
        in: formData
        type: string
        required: true
        description: Numărul de telefon al medicului
      - name: specializare
        in: formData
        type: string
        required: true
        description: Specializarea medicului
    responses:
      201:
        description: Medicul a fost adăugat cu succes
      500:
        description: Eroare internă
    """
    data = request.form

    id_doctor = get_new_doctor_id()
    id_user = get_new_user_id()
    nume = data.get('nume')
    prenume = data.get('prenume')
    email = data.get('email')
    telefon = data.get('telefon')
    specializare = ",".join([data.get('specializare')])

    connected = connectDB()

    try:
        if connected.is_connected():
            cursor = connected.cursor()
            query ="INSERT INTO IDM_Utilizatori (id_user,roluri) VALUES ("+str(id_user)+",'Medic')"
            cursor.execute(query)
            query = "INSERT INTO date_doctori (id_doctor,id_user,nume, prenume, email, telefon, specializare) VALUES (%s, %s,%s, %s, %s, %s, %s)"
            values = (id_doctor, id_user, nume, prenume, email, telefon, specializare)
            cursor.execute(query, values)
            connected.commit()
            cursor.close()
            connected.close()
            return jsonify({"message": "Medicul a fost adăugat cu succes"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medical_office/add_physician',methods=['PUT'])
def update_physician():
    """
    Update un medic în baza de date.

    ---
    tags:
      - Medic
    parameters:
      - name: id_doctor
        in: formData
        type: string
        required: true
        description: Id-ul doctorului
      - name: nume
        in: formData
        type: string
        required: false
        description: Numele medicului
      - name: prenume
        in: formData
        type: string
        required: false
        description: Prenumele medicului
      - name: email
        in: formData
        type: string
        required: false
        description: Adresa de email a medicului
      - name: telefon
        in: formData
        type: string
        required: false
        description: Numărul de telefon al medicului
      - name: specializare
        in: formData
        type: string
        required: false
        description: Specializarea medicului
    responses:
      201:
        description: Medicul a fost updated
      500:
        description: Eroare internă
    """

    data = request.form

    id_doctor = data.get('id_doctor')

    doctor = afisareDoctor(id_doctor)

    # Nume
    if data.get('nume') in {None, ""}:
        nume = doctor.nume
    else:
        nume = data.get('nume')

    # Prenume
    if data.get('prenume') in {None, ""}:
        prenume = doctor.prenume
    else:
        prenume = data.get('prenume')

    # Email
    if data.get('email') in {None, ""}:
        email = doctor.email
    else:
        email = data.get('email')

    # Telefon
    if data.get('telefon') in {None, ""}:
        telefon = doctor.telefon
    else:
        telefon = data.get('telefon')

    # Specializare
    if data.get('specializare') in {None, ""}:
        specializare = ",".join(doctor.specializare)
    else:
        specializare = ",".join([data.get('specializare')])
    connected = connectDB()

    try:
        if connected.is_connected():
            cursor = connected.cursor()
            query = "UPDATE date_doctori SET nume = %s, prenume = %s, email = %s, telefon = %s, specializare = %s WHERE id_doctor = %s"
            values = (nume, prenume, email, telefon, specializare,id_doctor)
            cursor.execute(query, values)
            connected.commit()
            cursor.close()
            connected.close()
            return jsonify({"message": "Medicul a fost updated cu succes"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
