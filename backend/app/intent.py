from pydantic import BaseModel
from typing import Literal


class Intent(BaseModel):
    intent: Literal[
        "get_next_appointment",
        "get_prescriptions",
        "get_medical_records",
        "get_latest_test",
"get_abnormal_tests",
"get_specific_test",
        "unknown"
    ]