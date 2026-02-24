from fastapi import Header, HTTPException, Depends
from app.session import get_session


def get_current_session(session_id: str = Header(...)):
    session = get_session(session_id)

    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return session


def require_patient(session: dict = Depends(get_current_session)):
    if session["role"] != "patient":
        raise HTTPException(status_code=403, detail="Patient access required")
    return session


def require_admin(session: dict = Depends(get_current_session)):
    if session["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return session