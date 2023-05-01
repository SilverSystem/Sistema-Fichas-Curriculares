from fastapi import FastAPI
# from dependencies import get_query_token
from routers import auth

app = FastAPI()
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
