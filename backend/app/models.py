from sqlalchemy import Column, String, Date, Float, Integer, ForeignKey
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    gender = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    reg_date = Column(Date, nullable=False)


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    p_id = Column(String, ForeignKey("patients.patient_id"), nullable=False)
    test = Column(String, nullable=False)
    val = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    stat = Column(String, nullable=False)
    date = Column(Date, nullable=False)