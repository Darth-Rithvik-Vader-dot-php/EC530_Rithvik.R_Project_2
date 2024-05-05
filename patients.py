from flask import Flask, jsonify, request
from flask_pymongo import PyMongo, ObjectId

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://visaaln2:visaal456@ec530.qevqtrc.mongodb.net/healthmonitoring?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Convert MongoDB document to a dictionary
def document_to_dict(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
        return doc
    return None

# Convert list of MongoDB documents to list of dictionaries
def documents_to_list(docs):
    return [document_to_dict(doc) for doc in docs]

# Add a New Patient
@app.route('/patients', methods=['POST'])
def add_patient():
    patient_data = request.json
    patient_id = mongo.db.patients.insert_one(patient_data).inserted_id
    return jsonify({'message': 'Patient added successfully', 'patient_id': str(patient_id)}), 201

# 2. Get All Patients
@app.route('/patients', methods=['GET'])
def get_all_patients():
    patients = mongo.db.patients.find()
    return jsonify(documents_to_list(patients)), 200

# 3. Get a Single Patient
@app.route('/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = mongo.db.patients.find_one({'_id': ObjectId(patient_id)})
    return jsonify(document_to_dict(patient)), 200

# 4. Update Patient Information
@app.route('/patients/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    update_data = request.json
    mongo.db.patients.update_one({'_id': ObjectId(patient_id)}, {'$set': update_data})
    return jsonify({'message': 'Patient updated successfully'}), 200

# 5. Delete a Patient
@app.route('/patients/<patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    mongo.db.patients.delete_one({'_id': ObjectId(patient_id)})
    return jsonify({'message': 'Patient deleted successfully'}), 200

# 6. Add a Device to a Patient
@app.route('/patients/<patient_id>/devices', methods=['POST'])
def add_device(patient_id):
    device_data = request.json
    mongo.db.patients.update_one({'_id': ObjectId(patient_id)}, {'$push': {'devices': device_data}})
    return jsonify({'message': 'Device added successfully'}), 201

# 7. Update a Device
@app.route('/patients/<patient_id>/devices/<device_id>', methods=['PUT'])
def update_device(patient_id, device_id):
    update_data = request.json
    # MongoDB doesn't support direct array element update by _id in a nested document. This is a workaround.
    mongo.db.patients.update_one({'_id': ObjectId(patient_id), 'devices._id': ObjectId(device_id)},
                                 {'$set': {'devices.$': update_data}})
    return jsonify({'message': 'Device updated successfully'}), 200

# 8. Remove a Device from a Patient
@app.route('/patients/<patient_id>/devices/<device_id>', methods=['DELETE'])
def remove_device(patient_id, device_id):
    mongo.db.patients.update_one({'_id': ObjectId(patient_id)},
                                 {'$pull': {'devices': {'_id': ObjectId(device_id)}}})
    return jsonify({'message': 'Device removed successfully'}), 200

# 9. Record a Device Reading
@app.route('/patients/<patient_id>/devices/<device_id>/readings', methods=['POST'])
def record_reading(patient_id, device_id):
    reading_data = request.json
    mongo.db.patients.update_one({'_id': ObjectId(patient_id), 'devices._id': ObjectId(device_id)},
                                 {'$push': {'devices.$.dailyReadings': reading_data}})
    return jsonify({'message': 'Reading recorded successfully'}), 201

# 10. Get Device Readings
@app.route('/patients/<patient_id>/devices/<device_id>/readings', methods=['GET'])
def get_readings(patient_id, device_id):
    patient = mongo.db.patients.aggregate([
        {'$match': {'_id': ObjectId(patient_id)}},
        {'$unwind': '$devices'},
        {'$match': {'devices._id': ObjectId(device_id)}},
        {'$project': {'readings': '$devices.dailyReadings'}}
    ])
    readings = list(patient)
    if readings:
        return jsonify(readings[0]['readings']), 200
    else:
        return jsonify({'message': 'No readings found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
