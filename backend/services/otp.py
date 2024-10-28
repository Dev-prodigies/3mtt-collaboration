import pyotp

def create_otp() -> str:
    secret_key = pyotp.random_base32()
    totp = pyotp.TOTP(secret_key)
    otp = totp.now()
    return otp

def verify_otp(stored_otp: str, user_provided_otp: str) -> bool:
    return stored_otp == user_provided_otp
