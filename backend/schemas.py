from typing import Union

from pydantic import BaseModel, EmailStr, constr, field_validator

class PhoneNumberSchema(BaseModel):
    country_code: int
    number: str


class OTPVerification(BaseModel):
    email: EmailStr
    otp: constr(min_length=6, max_length=6)

class CompleteSignup(BaseModel):
    full_name: str
    phone_number: PhoneNumberSchema

class Login(BaseModel):
    email: Union[EmailStr, None] = None
    phone_number: Union[PhoneNumberSchema, None] = None
    password: str

    @field_validator("email")
    def check_email_or_phone_number_present(cls, v, info):
        if v is None and not info.data.get("phone_number"):
            raise ValueError("At least one of 'email' or 'phone_number' must be provided")
        return v

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=100)
    confirm_password: str

    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

class UserVerify(BaseModel):
    email: EmailStr
    otp: constr(min_length=6, max_length=6)
    password: str

class UserSchema(BaseModel):
    email: EmailStr
    # phone_number: PhoneNumberSchema
    full_name: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
