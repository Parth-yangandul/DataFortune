import json
from datetime import datetime
from app.database import SessionLocal, engine
from app.models import Base, Patient, Test


def seed_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Prevent reseeding
    if db.query(Patient).first():
        db.close()
        return

    # Load patients
    with open("data/patients.json") as f:
        patients = json.load(f)

        for p in patients:
            patient = Patient(
                patient_id=p["patient_id"],
                name=p["name"],
                email=p["email"],
                phone=p["phone"],
                gender=p["gender"],
                dob=datetime.strptime(p["dob"], "%Y-%m-%d"),
                reg_date=datetime.strptime(p["reg_date"], "%Y-%m-%d"),
            )
            db.add(patient)

    # Load tests
    with open("data/tests.json") as f:
        tests = json.load(f)

        for t in tests:
            test = Test(
                p_id=t["p_id"],
                test=t["test"],
                val=t["val"],
                unit=t["unit"],
                stat=t["stat"],
                date=datetime.strptime(t["date"], "%Y-%m-%d"),
            )
            db.add(test)

    db.commit()
    db.close()