from passlib.context import CryptContext

# There is a warning for crypt deprecation here so we need to use
# bcrypt in another way that doesn't call crypt indirectly from passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    hashed_password = pwd_context.hash(password)
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
