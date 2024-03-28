from  fastapi import FastAPI
from routers.router_login import auth_router
import uvicorn

app = FastAPI()

@app.get('/')
def read_root():
    return {"message": "Hello, world!"}

app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)