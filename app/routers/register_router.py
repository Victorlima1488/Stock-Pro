from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from routers.shared_data import UserRegister, temp_data
from database.sqlite.connection import conexao_do_banco
from cryptography.hazmat.primitives import hashes
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from email.mime.text import MIMEText
from dotenv import load_dotenv
import smtplib
import pyotp
import os

auth_router = APIRouter()

# Carregando as variáveis de ambiente do arquivo .env
load_dotenv()

# Acessando variáveis de ambiente
master_key = os.getenv("MASTER_KEY")
sender_email_key = os.getenv("SENDER_EMAIL")
sender_password_key = os.getenv("SENDER_PASSWORD")

# Criando um objeto para lidar com hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Chave mestra para autenticação
authentication_master_key = master_key

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
    # Criptografando o CPF usando o algoritmo OAEP com SHA256
    cipher_text = public_key.encrypt(
        cpf.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # Retornando o CPF criptografado em formato hexadecimal
    return cipher_text.hex()

# Função para enviar e-mail com o código de verificação
def send_verification_email(username, email, verification_code):
    # Configurações do e-mail remetente
    sender_email = sender_email_key
    sender_password = sender_password_key
    
    # Criando a mensagem de e-mail
    verification_code_now = verification_code.now()
    message = MIMEText(f"Olá, {username}! Seu código de verificação é: {verification_code_now}")
    message["Subject"] = "Código de verificação"
    message["From"] = sender_email
    message["To"] = email

    # Enviando o e-mail usando SMTP
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, email, message.as_string())
    server.quit()

# Rota de registro de usuário
@auth_router.post('/register', response_model=UserRegister)
async def register(user: UserRegister):
    database = conexao_do_banco()
    cursor = database.cursor()

    # Verificando se o usuário já existe
    cursor.execute(f"SELECT * FROM users WHERE username = '{user.username}'")
    has_a_user = cursor.fetchone()

    if has_a_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash da senha do usuário
    hashed_password = get_password_hash(user.password)
    
    # Criptografando o CPF do usuário
    encrypted_cpf = encrypt_cpf(user.cpf)
    
    # Gerando um código de verificação usando TOTP (Time-based One-Time Password)
    verification_code = pyotp.TOTP(authentication_master_key)
    
    # Enviando o código de verificação por e-mail
    send_verification_email(user.username, user.email, verification_code)
    
    # Atualizando a senha e o CPF do usuário com os valores criptografados
    user.password = hashed_password
    user.cpf = encrypted_cpf
    
    # Armazenando temporariamente os dados do usuário e o código de verificação
    temp_data.store_temp_user_data(user, verification_code)
    
    return user