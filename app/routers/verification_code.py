from database.sqlite.connection import conexao_do_banco
from fastapi import APIRouter, HTTPException
from routers.shared_data import temp_data
from pydantic import BaseModel

verification_router = APIRouter()

# Definindo um modelo de dados para a verificação do usuário
class UserVerification(BaseModel):
    username: str
    verification_code: str

# Definindo uma rota para a verificação do usuário
@verification_router.post('/verification', response_model=UserVerification)
def verification(user: UserVerification):
    database = conexao_do_banco()
    cursor = database.cursor()

    # Obtendo os dados do usuário e o código de verificação armazenados temporariamente
    stored_user, stored_verification_code = temp_data.get_temp_user_data(user.username)
    
    # Verifica se o usuário não foi encontrado nos dados temporários
    if stored_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verifica se o código de verificação fornecido pelo usuário é válido
    if not stored_verification_code.verify(user.verification_code):
        raise HTTPException(status_code=400, detail=f"Invalid verification code: {stored_verification_code}")
    else:
        # Se o código de verificação for válido, insere os dados do usuário no banco de dados
        cursor.execute(f"INSERT INTO users (username, email, password, address, cpf, gender, age) VALUES ('{stored_user.username}','{stored_user.email}', '{stored_user.password}', '{stored_user.address}', '{stored_user.cpf}','{stored_user.gender}','{stored_user.age}');")
        database.commit()
        cursor.close()
    
    return {"username": stored_user.username, "verification_code": user.verification_co}