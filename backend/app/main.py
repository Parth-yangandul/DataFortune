from fastapi import FastAPI, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from datetime import date
from app.database import SessionLocal
from app.seed import seed_database
from app.services import find_patient_by_phone, find_patient_by_email
from app.session import create_session, delete_session
from app.auth import security, verify_admin
from fastapi.security import HTTPBasicCredentials
import json
from app.intent_engine import extract_intent
from app.dependencies import require_patient, require_admin
from app.response_engine import generate_response
from app.services import (
    get_next_test_date,
    get_latest_test,
    get_abnormal_tests,
    get_tests_by_name,
)
from app.models import Patient, Test

app = FastAPI(title="AI Voice Patient Portal")


@app.on_event("startup")
def startup():
    seed_database()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------
# Patient Login
# -------------------

@app.post("/auth/patient-login")
def patient_login(phone: str | None = None,
                  email: str | None = None,
                  db: Session = Depends(get_db),
                  request: Request = None):

    # region agent log
    try:
        with open(r"d:\DataFortune\debug-66ca42.log", "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "66ca42",
                "runId": "initial",
                "hypothesisId": "H1-H3",
                "location": "app.main:patient_login",
                "message": "patient_login entry",
                "data": {
                    "has_phone": bool(phone),
                    "has_email": bool(email),
                    "method": request.method if request else None,
                    "url": str(request.url) if request else None
                },
                "timestamp": __import__("time").time()
            }) + "\n")
    except Exception:
        pass
    # endregion

    if not phone and not email:
        raise HTTPException(status_code=400, detail="Phone or email required")

    patient = None

    if phone:
        patient = find_patient_by_phone(db, phone)

    if email:
        patient = find_patient_by_email(db, email)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    session_id = create_session(role="patient", patient_id=patient.patient_id)

    return {
        "message": "Login successful",
        "session_id": session_id,
        "patient_id": patient.patient_id
    }


# -------------------
# Admin Login
# -------------------

@app.post("/auth/admin-login")
def admin_login(credentials: HTTPBasicCredentials = Depends(security)):
    verify_admin(credentials)

    session_id = create_session(role="admin")

    return {
        "message": "Admin login successful",
        "session_id": session_id
    }


# -------------------
# Logout
# -------------------

@app.post("/auth/logout")
def logout(session_id: str = Header(default=None)):
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID missing")

    delete_session(session_id)

    return {"message": "Logged out successfully"}


from pydantic import BaseModel


class VoiceQuery(BaseModel):
    text: str


from app.services import get_next_test_date
from app.services import (
    get_next_test_date,
    get_latest_test,
    get_tests_by_name,
    get_abnormal_tests,
)
from app.response_engine import generate_response


@app.post("/voice/query")
def voice_query(
    payload: VoiceQuery,
    session: dict = Depends(require_patient),
    db: Session = Depends(get_db),
):
    intent = extract_intent(payload.text)
    patient_id = session["patient_id"]

    if intent.intent == "get_next_appointment":
        next_test = get_next_test_date(db, patient_id)

        if not next_test:
            return {"intent": intent.intent, "data": None}

        return {
            "intent": intent.intent,
            "data": {
                "test_id": next_test.id,
                "test_name": next_test.test,
                "date": str(next_test.date),
                "status": next_test.stat,
            },
        }

    elif intent.intent == "get_latest_test":
        test = get_latest_test(db, patient_id)

        if not test:
            return {"intent": intent.intent, "data": None}

        return {
            "intent": intent.intent,
            "data": {
                "test_name": test.test,
                "value": test.val,
                "unit": test.unit,
                "status": test.stat,
                "date": str(test.date),
            },
        }

    elif intent.intent == "get_abnormal_tests":
        tests = get_abnormal_tests(db, patient_id)

        return {
            "intent": intent.intent,
            "data": [
                {
                    "test_name": t.test,
                    "value": t.val,
                    "unit": t.unit,
                    "status": t.stat,
                    "date": str(t.date),
                }
                for t in tests
            ],
        }

    elif intent.intent == "get_specific_test":
        tests = get_tests_by_name(db, patient_id, payload.text)

        return {
            "intent": intent.intent,
            "data": [
                {
                    "test_name": t.test,
                    "value": t.val,
                    "unit": t.unit,
                    "status": t.stat,
                    "date": str(t.date),
                }
                for t in tests
            ],
        }

    else:
        return {
            "intent": "unknown",
            "message": "Sorry, I didn't understand that.",
        }

@app.post("/voice/chat")
def voice_chat(
    payload: VoiceQuery,
    session: dict = Depends(require_patient),
    db: Session = Depends(get_db),
):
    intent = extract_intent(payload.text)
    patient_id = session["patient_id"]

    structured_data = None

    # ----------------------
    # Intent Routing
    # ----------------------

    if intent.intent == "get_next_appointment":
        next_test = get_next_test_date(db, patient_id)

        if next_test:
            structured_data = {
                "type": "next_appointment",
                "test_name": next_test.test,
                "date": str(next_test.date),
                "status": next_test.stat,
            }

    elif intent.intent == "get_latest_test":
        test = get_latest_test(db, patient_id)

        if test:
            structured_data = {
                "type": "latest_test",
                "test_name": test.test,
                "value": test.val,
                "unit": test.unit,
                "status": test.stat,
                "date": str(test.date),
            }

    elif intent.intent == "get_abnormal_tests":
        tests = get_abnormal_tests(db, patient_id)

        structured_data = {
            "type": "abnormal_tests",
            "tests": [
                {
                    "test_name": t.test,
                    "value": t.val,
                    "unit": t.unit,
                    "status": t.stat,
                    "date": str(t.date),
                }
                for t in tests
            ],
        }

    elif intent.intent == "get_specific_test":
        tests = get_tests_by_name(db, patient_id, payload.text)

        structured_data = {
            "type": "specific_test",
            "tests": [
                {
                    "test_name": t.test,
                    "value": t.val,
                    "unit": t.unit,
                    "status": t.stat,
                    "date": str(t.date),
                }
                for t in tests
            ],
        }

    # ----------------------
    # Unknown Intent
    # ----------------------

    if not structured_data:
        return {
            "answer": "I'm sorry, I couldn't find the information you're looking for."
        }

    # ----------------------
    # Generate Final Response
    # ----------------------

    answer = generate_response(payload.text, structured_data)

    return {
        "answer": answer
    }


# -------------------
# Patient Full Test History
# -------------------

@app.get("/patient/tests/history")
def get_patient_test_history(
    session: dict = Depends(require_patient),
    db: Session = Depends(get_db),
):
    patient_id = session["patient_id"]

    tests = (
        db.query(Test)
        .filter(Test.p_id == patient_id)
        .order_by(Test.date.desc())
        .all()
    )

    return [
        {
            "test_name": t.test,
            "value": t.val,
            "unit": t.unit,
            "status": t.stat,
            "date": str(t.date),
        }
        for t in tests
    ]


# -------------------
# Admin Aggregate Endpoints
# -------------------

@app.get("/admin/patients/today")
def get_patients_registered_today(
    session: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    today = date.today()

    patients = (
        db.query(Patient)
        .filter(Patient.reg_date == today)
        .order_by(Patient.name.asc())
        .all()
    )

    return [
        {
            "patient_id": p.patient_id,
            "name": p.name,
            "email": p.email,
            "phone": p.phone,
            "gender": p.gender,
            "reg_date": str(p.reg_date),
        }
        for p in patients
    ]


@app.get("/admin/patients/high-cholesterol-male")
def get_male_patients_high_cholesterol(
    session: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    lipid_patients_subq = (
        db.query(Test.p_id)
        .filter(Test.test == "Lipid Profile", Test.stat.in_(["High", "Very High"]))
        .distinct()
        .subquery()
    )

    patients = (
        db.query(Patient)
        .filter(Patient.gender == "Male", Patient.patient_id.in_(lipid_patients_subq))
        .order_by(Patient.name.asc())
        .all()
    )

    return [
        {
            "patient_id": p.patient_id,
            "name": p.name,
            "email": p.email,
            "phone": p.phone,
            "gender": p.gender,
        }
        for p in patients
    ]