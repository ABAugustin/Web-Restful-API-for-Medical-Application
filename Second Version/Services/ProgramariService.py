from datetime import datetime

from DTOs.Programari import Programari
from DTOs.doctor import Doctor as doct
from DTOs.Pacient import Pacient as patt
from DTOs.Consultatii import DateInvestigatii as Dinvest
from flask import Flask, url_for, jsonify,request
import mysql.connector
from flasgger import Swagger, swag_from
from pymongo import MongoClient
from DTOs.Consultatii import DateConsultatii as Dcos
import random
from bson import ObjectId

from Services.DoctorService import connectDB

app = Flask(__name__)
swagger = Swagger(app)

def return_appointments_for_consultation():
    connected = connectDB()
    if connected.is_connected():
        cursor = connected.cursor()
        query = "SELECT * FROM date_programari"
        cursor.execute(query)
        appointments = []
        for row in cursor.fetchall():
            appointment = Programari(
                id_pacient=row[0],
                id_doctor=row[1],
                data=str(row[2]),
                status=[(row[3])]
            )
        appointments.append(appointment)
    return appointments


@app.route('/api/medical_office/create_appointment',methods=['POST'])
def create_appointment():
    """
       Crează o nouă programare în sistem.

       ---
       tags:
         - Programare
       parameters:
         - name: id_pacient
           in: formData
           type: string
           required: true
           description: ID-ul pacientului
         - name: id_doctor
           in: formData
           type: string
           required: true
           description: ID-ul doctorului
         - name: data
           in: formData
           type: string
           required: true
           description: Data programării ("YYYY-MM-DD")
       responses:
         201:
           description: Programarea a fost adăugată cu succes
         500:
           description: Eroare internă
       """


    dat = request.form
    id_pacient=dat.get('id_pacient')
    id_doctor=dat.get('id_doctor')
    data_str = dat.get('data')
    data = datetime.strptime(data_str, '%Y-%m-%d').date()
    status="neprezentat"

    connected = connectDB()
    if connected.is_connected():
        cursor = connected.cursor()
        query = "INSERT INTO date_programari (id_pacient,id_doctor,data,status) VALUES(%s,%s,%s,%s)"
        values = (id_pacient, id_doctor, data, status)
        cursor.execute(query, values)
        connected.commit()
        cursor.close()
        connected.close()
        return jsonify({"message": "Programarea a fost adaugata"}), 201

    else:
        return jsonify({"Nu s-a putut adauga programare"}), 500



@app.route('/api/medical_office/appointments', methods=['GET'])

def list_appointments():
    """
        Obține lista programărilor în sistem.

        ---
        tags:
          - Programare
        responses:
          200:
            description: Lista programărilor a fost obținută cu succes
          500:
            description: Eroare internă
        """


    connected = connectDB()
    if connected.is_connected():
        cursor = connected.cursor()
        query = "SELECT * FROM date_programari"
        cursor.execute(query)
        appointments =[]
        for row in cursor.fetchall():
            appointment = Programari(
                id_pacient=row[0],
                id_doctor=row[1],
                data=str(row[2]),
                status=[(row[3])]
            )
            appointments.append(appointment.model_dump())

        cursor.close()
        connected.close()

        return jsonify(appointments), 200

    return jsonify({"error": "Nu s-a putut obține lista programărilor"}), 500