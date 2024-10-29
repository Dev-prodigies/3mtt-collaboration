from sqlalchemy import select
from connection.database import database_init
from services.auth import generate_access_token, get_current_user
from dependencies import db_con, redis_con
from services.email import send_email_async
from services.otp import create_otp, verify_otp
from util import hash_password, verify_password
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from models import PhoneNumber, User
from schemas import CompleteSignup, Login, Token, UserCreate, UserSchema, UserVerify, OTPVerification


import json
from typing import Union, cast

import redis
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError


EMAIL_OTP_SUBJECT = "Your otp verification code"

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await database_init()

@app.post("/register")
async def register(user: UserCreate, redis_client: Redis = Depends(redis_con)):
    user_email = user.email
    otp = create_otp()
    print("OTP", otp)
    success = True #await send_email_async(EMAIL_OTP_SUBJECT, user_email, otp)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP.",
        )
    user =user.dict()
    user.pop("confirm_password")
    user = UserVerify(**user, otp=otp)
    user_json_str = user.json()
    redis_client.setex(user_email, 600, user_json_str)  # Store OTP with 10-minute expiry
    return ORJSONResponse(
        {"message": "OTP sent to mail"},
        status_code=status.HTTP_201_CREATED,
    )

@app.post("/verify-otp")
async def verify_registration(
    request: OTPVerification,
    db: AsyncSession = Depends(db_con),
    redis_client: redis.Redis =  Depends(redis_con),
) -> ORJSONResponse:
    stored_user_json = redis_client.get(request.email)
    if not stored_user_json:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OTP expired or not found"
        )
    user_data = json.loads(stored_user_json)
    try:
        stored_user = UserVerify(**user_data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user data",
        ) from e

    if not verify_otp(stored_user.otp, request.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    user = User(
        email=stored_user.email,
        password_hash=hash_password(stored_user.password)  # Replace with hashed password
    )
    db.add(user)
    await db.commit()
    #redis_client.delete(request.email)

    return {"msg": "User registered successfully"}

@app.post("/login/", response_model=Token)
async def login(
    login_data: Login,
    db: AsyncSession = Depends(db_con),
) -> Token:
    error_message = "Incorrect " + ("email" if login_data.email else "phone number") + " or password."
    if login_data.email:
        quary = (
            select(User).filter(
                User.email == login_data.email
            )
        )
        print(login_data.email)
    else:
        quary = (
            select(User)
            .join(PhoneNumber)
            .filter(
                PhoneNumber.number == login_data.phone_number.number,
                PhoneNumber.country_code == login_data.phone_number.country_code
            )
        )
    result = await db.execute(quary)
    user_ = result.scalars().first()
    user = UserSchema(
        email=user_.email,
        full_name="Temp",
        # phone_number=user.phone_number,
    ) if user_ else None

    if not user or not verify_password(login_data.password, cast(str, user_.password_hash)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_message)

    access_token = generate_access_token(user)
    return Token(access_token=access_token)

@app.post("/complete-signup")
async def complete_signup(
    request: CompleteSignup,
    db: AsyncSession = Depends(db_con),
    current_user = Depends(get_current_user),
) -> ORJSONResponse:
    async with db.begin():
        try:
            assert request.phone_number
            phone_number = PhoneNumber(
                country_code=request.phone_number.country_code,
                number=request.phone_number.number
            )
            db.add(phone_number)
            await db.flush()

            if not phone_number.id:
                raise ValueError("Failed to generate a unique ID for the phone number.")

            quary = select(User).where(User.email == current_user.email)
            result = await db.execute(quary)
            user: Union[User, None] = result.scalars().first()

            if not user:
                raise ValueError(f"User with email {current_user.email} not found")

            user.full_name = request.full_name
            user.phone_number_id  = phone_number.id
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise e
    return ORJSONResponse(
        {"message": "Signup completed successfully"},
        status_code=status.HTTP_200_OK,
    )
