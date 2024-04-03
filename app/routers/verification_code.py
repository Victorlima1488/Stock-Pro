# from database.sqlite.connection import conexao_do_banco
from fastapi import APIRouter, HTTPException
from routers.shared_data import temp_data
from pydantic import BaseModel
from utils.User import User, SessionLocal

verification_router = APIRouter()

# Definindo um modelo de dados para a verificação do usuário
class UserVerification(BaseModel):
    username: str
    verification_code: str

# Definindo uma rota para a verificação do usuário
@verification_router.post('/verification', response_model=UserVerification)
def verification(user: UserVerification):

    # Obtendo os dados do usuário e o código de verificação armazenados temporariamente
    stored_user, stored_verification_code = temp_data.get_temp_user_data(user.username)
    
    # Verifica se o usuário não foi encontrado nos dados temporários
    if stored_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verifica se o código de verificação fornecido pelo usuário é válido
    if not stored_verification_code.verify(user.verification_code):
        raise HTTPException(status_code=400, detail=f"Invalid verification code: {stored_verification_code}")
    else:
        # Se o código de verificação for válido, insere os dados do usuário no banco de dados usando o ORM
        database = SessionLocal()
        db_user = User(username=stored_user.username, email=stored_user.email, password=stored_user.password,
                       address=stored_user.address, cpf=stored_user.cpf, gender=stored_user.gender, age=stored_user.age)
        database.add(db_user)
        database.commit()
        database.close()
    
    return {"username": stored_user.username, "verification_code": user.verification_code}