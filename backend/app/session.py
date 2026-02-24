import uuid
from datetime import datetime, timedelta

SESSION_TIMEOUT_MINUTES = 10

SESSIONS = {}

def create_session(role: str, patient_id: str | None = None):
    session_id = str(uuid.uuid4())

    SESSIONS[session_id] = {
        "role": role,
        "patient_id": patient_id,
        "expires_at": datetime.utcnow() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    }

    return session_id


def get_session(session_id: str):
    session = SESSIONS.get(session_id)

    if not session:
        return None

    if session["expires_at"] < datetime.utcnow():
        delete_session(session_id)
        return None

    return session


def delete_session(session_id: str):
    SESSIONS.pop(session_id, None)