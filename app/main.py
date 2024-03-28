from routers.verification_code import verification_router
from routers.register_router import auth_router
from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Inclusão dos roteadores
routers = [auth_router, verification_router]
for router in routers:
    app.include_router(router)

# Iniciação do servidor Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)