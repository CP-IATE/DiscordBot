from fastapi import FastAPI
from api_endpoints import router
app = FastAPI()
app.include_router(router)