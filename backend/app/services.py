from sqlalchemy.orm import Session
from app.models import Patient, Test
from datetime import date


def find_patient_by_phone(db: Session, phone: str):
    return db.query(Patient).filter(Patient.phone == phone).first()


def find_patient_by_email(db: Session, email: str):
    return db.query(Patient).filter(Patient.email == email).first()


def get_next_test_date(db: Session, patient_id: str):
    today = date.today()

    next_test = (
        db.query(Test)
        .filter(Test.p_id == patient_id, Test.date >= today)
        .order_by(Test.date.asc())
        .first()
    )

    return next_test

def get_latest_test(db: Session, patient_id: str):
        return (
        db.query(Test)
        .filter(Test.p_id == patient_id)
        .order_by(Test.date.desc())
        .first()
    )


def get_tests_by_name(db: Session, patient_id: str, test_name: str):
    return (
        db.query(Test)
        .filter(Test.p_id == patient_id, Test.test.ilike(f"%{test_name}%"))
        .order_by(Test.date.desc())
        .all()
    )


def get_abnormal_tests(db: Session, patient_id: str):
    return (
        db.query(Test)
        .filter(Test.p_id == patient_id, Test.stat != "Normal")
        .order_by(Test.date.desc())
        .all()
    )