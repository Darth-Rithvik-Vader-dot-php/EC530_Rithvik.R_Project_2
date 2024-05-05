from datetime import datetime
from flask import Flask
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB setup
app.config["MONGO_URI"] = "mongodb+srv://visaaln2:visaal456@ec530.qevqtrc.mongodb.net/healthmonitoring?retryWrites=true&w=majority"
mongo_client = MongoClient('mongodb+srv://visaaln2:visaal456@ec530.qevqtrc.mongodb.net/healthmonitoring?retryWrites=true&w=majority')
db = mongo_client.medicalDatabase


# RQ setup
redis_conn = Redis()
queue = Queue(connection=redis_conn)
scheduler = Scheduler(queue=queue, connection=redis_conn)


def get_patients_with_devices():
    """Fetch patients with devices."""
    # Assuming 'patients' is your collection name
    patients = db.patients.find({})
    return list(patients)

def has_updated_reading_today(patient):
    """Check if there's an updated reading for today for any device of the patient."""
    today = datetime.now().strftime("%Y-%m-%d")
    for device in patient.get("devices", []):
        for reading in device.get("dailyReadings", []):
            if reading.get("date") == today:
                return True
    return False

def notify_patient_and_doctor(patient):
    """Placeholder function to send notifications to patient and doctor."""
    # Implement your notification logic here
    # This could be an email, SMS, or any other type of notification
    print(f"Sending notification for patient {patient['name']}")

def check_and_notify():
    """Check each patient and notify if no reading for today."""
    patients = get_patients_with_devices()
    for patient in patients:
        if not has_updated_reading_today(patient):
            notify_patient_and_doctor(patient)

def schedule_daily_checks():
    """Schedule the daily check job."""
    # Schedule this to run daily at a specific time, for example, every day at 7 PM
    scheduler.schedule(
        scheduled_time=datetime.now(),  # Start time for the first job, adjust as needed
        func=check_and_notify,
        interval=86400,  # Schedule daily, 86400 seconds in a day
    )

@app.route('/start_checks')
def start_checks():
    """Endpoint to start the scheduling of daily checks."""
    schedule_daily_checks()
    return "Scheduled daily checks"

if __name__ == '__main__':
    app.run(debug=True)
