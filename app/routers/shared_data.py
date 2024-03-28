from pydantic import BaseModel
from typing import Dict, Optional
from pyotp import TOTP
from typing import Tuple

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    address: str
    cpf: str
    gender: str
    age: int
    verification_code: Optional[str]

class TempData:
    def __init__(self):
        self.temp_user_data: Dict[str, Tuple[UserRegister, TOTP]] = {}

    def store_temp_user_data(self, user: UserRegister, verification_code: TOTP):
        self.temp_user_data[user.username] = (user, verification_code)

    def get_temp_user_data(self, username: str) -> Tuple[UserRegister, TOTP]:
        return self.temp_user_data.get(username)

temp_data = TempData()
