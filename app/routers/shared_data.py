from typing import Dict, Optional
from pydantic import BaseModel
from typing import Tuple
from pyotp import TOTP

# Definindo um modelo de dados para o registro do usuário
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    address: str
    cpf: str
    gender: str
    age: int
    verification_code: Optional[str]

# Definindo uma classe para armazenar dados temporários
class TempData:
    def __init__(self):
        self.temp_user_data: Dict[str, Tuple[UserRegister, TOTP]] = {}
    
    # Método para armazenar os dados temporários do usuário
    def store_temp_user_data(self, user: UserRegister, verification_code: TOTP):
        self.temp_user_data[user.username] = (user, verification_code)
    
    # Método para obter os dados temporários do usuário pelo nome de usuário
    def get_temp_user_data(self, username: str) -> Tuple[UserRegister, TOTP]:
        return self.temp_user_data.get(username)

# Instanciando a classe TempData para criar um objeto para armazenar os dados temporários
temp_data = TempData()
