from fastapi import APIRouter, HTTPException
from routers.shared_data import temp_data
from pydantic import BaseModel
import pyotp
from database.sqlite.connection import conexao_do_banco

verification_router = APIRouter()

class UserVerification(BaseModel):
    username: str
    verification_code: str 

@verification_router.post('/verification', response_model=UserVerification)
def verification(user: UserVerification):
    # Fazendo conexão com o banco
    database = conexao_do_banco()
    cursor = database.cursor()

    stored_user, stored_verification_code = temp_data.get_temp_user_data(user.username)
    if stored_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verifica o código usando o método verify do objeto TOTP
    if not stored_verification_code.verify(user.verification_code):
        raise HTTPException(status_code=400, detail="Invalid verification code")
    else:
        cursor.execute(f"INSERT INTO users (username, email, password, address, cpf, gender, age) VALUES ('{stored_user.username}','{stored_user.email}', '{stored_user.password}', '{stored_user.address}', '{stored_user.cpf}','{stored_user.gender}','{stored_user.age}');")
        database.commit()
    return {"username": stored_user.username, "verification_code": user.verification_code}