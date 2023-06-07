from fastapi import FastAPI
# from dependencies import get_query_token
from routers import auth,fichas
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(auth.router)
app.include_router(fichas.router)
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
