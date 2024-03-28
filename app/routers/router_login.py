from fastapi import APIRouter, Request, HTTPException
from database.sqlite.connection import conexao_do_banco
from passlib.context import CryptContext
from pydantic import BaseModel
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

auth_router = APIRouter()

# Criando um objeto para lidar com hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Gerando um par de chaves RSA
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# Função para criar um hash de senha
def get_password_hash(password):
    return pwd_context.hash(password)

# Função para criptografar o CPF usando a chave pública RSA
def encrypt_cpf(cpf):
    cipher_text = public_key.encrypt(
        cpf.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return cipher_text

# Fazendo conexão com o banco
database = conexao_do_banco()
cursor = database.cursor()

# Definindo os modelos Pydantic para validar os dados de entrada
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    address: str
    cpf: str
    gender: str
    age: int

class UserLogin(BaseModel):
    username: str
    password: str
    
# Rota de registro de usuário
@auth_router.post('/register', response_model=UserRegister)
async def register(user: UserRegister):
    
    cursor.execute(f"SELECT * FROM users WHERE username = '{user.username}'")
    has_a_user = cursor.fetchone()

    if has_a_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    else:
        hashed_password = get_password_hash(user.password)
        encrypted_cpf = encrypt_cpf(user.cpf).hex()
        cursor.execute(f"INSERT INTO users (username, email, password, address, cpf, gender, age) VALUES ('{user.username}','{user.email}', '{hashed_password}', '{user.address}', '{encrypted_cpf}','{user.gender}','{user.age}');")
        database.commit()
    return user