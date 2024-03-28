from fastapi import FastAPI
from routers.register_router import auth_router
from routers.verification_code import verification_router
import uvicorn

app = FastAPI()

@app.get('/')
def read_root():
    return {"message": "Hello, world!"}

# Inclusão dos roteadores
routers = [auth_router, verification_router]
for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)