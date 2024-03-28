from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from email.mime.text import MIMEText
import smtplib
import pyotp
from routers.shared_data import UserRegister
from routers.shared_data import temp_data
from database.sqlite.connection import conexao_do_banco

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

# Função para enviar e-mail com o código de verificação
def send_verification_email(username, email, verification_code):
    sender_email = "limaeriko48@gmail.com"  # Coloque aqui o endereço de e-mail do remetente
    sender_password = "puca mncx waot awuv"  # Coloque aqui a senha do remetente
    verification_code_now = verification_code.now()
    message = MIMEText(f"Olá, {username}! Seu código de verificação é: {verification_code_now}")

    message["Subject"] = "Código de verificação"
    message["From"] = sender_email
    message["To"] = email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, email, message.as_string())
    server.quit()
    
authentication_master_key = 'RQ5S2B2ENMHNEK6PZDBONU5FUUM4DG7E'
    
# Rota de registro de usuário
@auth_router.post('/register', response_model=UserRegister)
async def register(user: UserRegister):
    # Fazendo conexão com o banco
    database = conexao_do_banco()
    cursor = database.cursor()

    cursor.execute(f"SELECT * FROM users WHERE username = '{user.username}'")
    has_a_user = cursor.fetchone()

    if has_a_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    else:
        hashed_password = get_password_hash(user.password)
        encrypted_cpf = encrypt_cpf(user.cpf).hex()
        verification_code = pyotp.TOTP(authentication_master_key)
        send_verification_email(user.username, user.email, verification_code)
        
        user.password = hashed_password
        user.cpf = encrypted_cpf
        
        # Armazena o objeto TOTP
        temp_data.store_temp_user_data(user, verification_code)
    return user