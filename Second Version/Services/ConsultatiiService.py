from DTOs.doctor import Doctor as doct
from DTOs.Pacient import Pacient as patt
from DTOs.Consultatii import DateInvestigatii as Dinvest, DateInvestigatii, DateConsultatii
from flask import Flask, url_for, jsonify,request
import mysql.connector
from flasgger import Swagger
from pymongo import MongoClient
from DTOs.Consultatii import DateConsultatii as Dcos
import random
from bson import ObjectId


from Services.DoctorService import connectDB


############################################### MONGO ###########################################

app = Flask(__name__)
swagger = Swagger(app)

def connectMongoClient():
    client = MongoClient('localhost', 27017, username='root', password='password')
    return client

@app.route('/api/medical_office/create_consultation_table',methods=['POST'])
def create_consultation_table():
    """
       Endpoint to create consultation records in MongoDB based on existing appointments.

       ---
       tags:
         - Consultation
       responses:
         200:
           description: Operation on the database performed successfully
       """



    connectMongo = connectMongoClient()
    connectMaria = connectDB()

    dbmongo = connectMongo["Programari"]

#incepe popularea
    colectie = dbmongo['Programari']
    if connectMaria.is_connected():
        query = "SELECT COUNT(*) FROM date_programari"
        cursor = connectMaria.cursor()
        cursor.execute(query)
        nrProgramari = cursor.fetchone()[0]

        query = "SELECT * FROM date_programari"
        cursor.execute(query)
        rowsProg = cursor.fetchall()

        prog = []

        for row in rowsProg:
            invest = [ Dinvest(
                    _id = str(ObjectId()),
                    denumire = str(random.choice(["gripa", "raceala", "diabet", "hipertensiune", "alergie", "migrena", "artrita", "astm"])),
                    durata_de_procesare = int(random.choice([1,2,3,4,5,6])),
                    rezultat = str(random.choice(['pozitv','negativ']))) ]
            new_Dcos = Dcos(
                id= str(ObjectId()),
                id_pacient= row[0],
                id_doctor= row[1],
                data= str(row[2]),
                diagnostic= random.choice(['bolnav','sanatos']),
                investigatii =invest

            )
            prog.append(new_Dcos.dict())
        colectie.insert_many(prog)
        cursor.close()
        connectMaria.close()

    return "Operatie pe baza de date efectuata",200

@app.route('/api/medical_office/delete_consultation_table',methods=['DELETE'])
def delete_consultation_table():
    """
        Endpoint to delete the entire consultation table from MongoDB.

        ---
        tags:
          - Consultation
        responses:
          200:
            description: Database table deleted successfully
        """
    connectMongo = connectMongoClient()
    dbmongo = connectMongo["Programari"]
    colectie = dbmongo['Programari']

    #sterg baza de date daca exista
    if 'Programari' in dbmongo.list_collection_names():

        colectie.drop()

    return 'baza de date stearsa'

@app.route('/api/medical_office/delete_consultation_element',methods=['DELETE'])
def delete_entry_from_table():

    """
    Endpoint to delete a specific entry from the consultation table in MongoDB.

    ---
    tags:
      - Consultation
    parameters:
      - name: id_pacient
        in: query
        type: string
        required: true
        description: ID of the patient
      - name: id_doctor
        in: query
        type: string
        required: true
        description: ID of the doctor
      - name: data
        in: query
        type: string
        required: true
        description: Date of the consultation ("YYYY-MM-DD")
    responses:
      200:
        description: Consultation entry deleted successfully
      400:
        description: Not enough parameters provided
      404:
        description: Consultation not found
      500:
        description: Internal server error
    """
    connectMaria = connectDB()
    try:
        connectMongo = connectMongoClient()
        dbmongo = connectMongo["Programari"]
        colectie = dbmongo['Programari']

        id_pacient = request.args.get('id_pacient')
        id_doctor = request.args.get('id_doctor')
        data_consultatie = request.args.get('data')


        if id_pacient is None or id_doctor is None or data_consultatie is None:
            return jsonify({"error": "Not enough params"}), 400


        id_pacient = int(id_pacient)
        id_doctor = int(id_doctor)

        result = colectie.delete_one({
            "id_pacient": id_pacient,
            "id_doctor": id_doctor,
            "data": data_consultatie
        })

        if result.deleted_count == 1:
            if connectMaria.is_connected():
                cursor = connectMaria.cursor()
                query = "DELETE FROM date_programari WHERE id_pacient=%s AND id_doctor=%s AND data=%s"
                values = (id_pacient, id_doctor, data_consultatie)
                cursor.execute(query, values)
                connectMaria.commit()
                cursor.close()
                connectMaria.close()
            return jsonify({"message": "Consultatie Stearsa"}), 200

        else:
            return jsonify({"error": "Nu a fost gasita consultatia"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/medical_office/create_consultation', methods=['POST'])
def create_consultation():

    try:
        # Connect to databases
        connectMongo = connectMongoClient()
        dbmongo = connectMongo["Programari"]
        colectie_mongo = dbmongo['Programari']

        connectMariaDB = connectDB()
        if not connectMariaDB.is_connected():
            raise Exception("MariaDB connection failed")


        id_pacient = request.json.get('id_pacient')
        id_doctor = request.json.get('id_doctor')
        data_programare = request.json.get('data_programare')
        status_programare ="neprezentat"
        data_consultatie = request.json.get('data_consultatie')
        diagnostic_consultatie = request.json.get('diagnostic_consultatie')
        denumire = request.json.get('denumire')
        durata_de_procesare = request.json.get('durata_de_procesare')
        rezultat = request.json.get('rezultat')


        cursor_maria = connectMariaDB.cursor()
        query_programari = "INSERT INTO date_programari (id_pacient, id_doctor, data, status) VALUES (%s, %s, %s, %s)"
        values_programari = (id_pacient, id_doctor, data_programare, status_programare)
        cursor_maria.execute(query_programari, values_programari)



        new_Dcos = Dcos(
            id=str(ObjectId()),
            id_pacient=id_pacient,
            id_doctor=id_doctor,
            data=data_consultatie,
            diagnostic=diagnostic_consultatie,
            investigatii=[
                Dinvest(
                    _id=str(ObjectId()),
                    denumire=denumire,
                    durata_de_procesare=durata_de_procesare,
                    rezultat=rezultat
                )
            ]
        )
        colectie_mongo.insert_one(new_Dcos.dict())


        connectMariaDB.commit()
        cursor_maria.close()
        connectMariaDB.close()

        return jsonify({"message": "Consultation and appointment created successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medical_office/update_consultation',methods=['PUT'])
def update_consultation():
    try:
        connectMongo = connectMongoClient()
        dbmongo = connectMongo["Programari"]
        colectie = dbmongo['Programari']


        data = request.json
        id_pacient = data.get('id_pacient')
        id_doctor = data.get('id_doctor')
        data_consultatie = data.get('data_consultatie')
        rezultat_nou = data.get('rezultat_nou')
        diagnostic_nou = data.get('diagnostic_nou')


        if id_pacient is None or id_doctor is None or data_consultatie is None:
            return jsonify({"error": "Not enough parameters provided"}), 400


        filtru = {
            "id_pacient": id_pacient,
            "id_doctor": id_doctor,
            "data": data_consultatie
        }


        actualizare = {"$set": {"rezultat": rezultat_nou, "diagnostic": diagnostic_nou}}


        rezultat = colectie.update_one(filtru, actualizare)


        if rezultat.matched_count == 1:
            return jsonify({"message": "Consultation updated successfully"}), 200
        else:
            return jsonify({"error": "Consultation not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/api/medical_office/list_all_consultations", methods=['GET'])
def list_consultations():
    """
        Endpoint to get a list of all consultations from MongoDB.

        ---
        tags:
          - Consultation
        responses:
          200:
            description: List of consultations retrieved successfully
          500:
            description: Internal server error
        """
    connectMongo = connectMongoClient()
    dbmongo = connectMongo["Programari"]
    colectie = dbmongo['Programari']

    consultations = colectie.find({}, {'_id': 0})

    consultation_list = list(consultations)

    return jsonify(consultation_list), 200
