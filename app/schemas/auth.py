from pydantic import BaseModel
class PhoneNumber(BaseModel):
    phone: str

class SMSVerification(BaseModel):
    phone: str
    code: str