from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, APIRouter,status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from db.initdb import postgreSQL_query
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import secrets
from libs.emails import enviar_correo
load_dotenv()
secret = os.getenv('JWT_SECRET')
algorithm = os.getenv('JWT_ALGORITHM')
access_token_expire_minutes = os.getenv('JWT_EXPIRATION_MINUTES')

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
class User(BaseModel):
    email:str
    password:str | None = None
    userType:str | None = None
    ci:int | None = None
    name:str | None = None
    lastName:str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str
  
class ChangePswd(BaseModel):
    email:str
    password:str
    codigoConfirmacion:str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(email)
    if user is None:
        raise credentials_exception
    return user

def get_user(email: str):
    query = 'SELECT * FROM usuario WHERE correo = %(email)s'
    values = {'email': email}
    response = postgreSQL_query(query,values,'get_one')
    print('La respuesta de la db')
    print(response)
    if response:
        return {'email':response[1],'password':response[2],'user_type':response[3],'ci':response[4],'name':response[5],'last_name':response[6],'recovery_code':response[7]}
    
def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
    return encoded_jwt

# current_user: Annotated[User, Depends(get_current_user)]


@router.post("/sign-up",)
def sign_up(user: User):
    print('Esto llego com body',user)
    psw = get_password_hash(user.password)
    query = '''INSERT INTO usuario (correo, password, user_type, cedula_identidad, nombre, apellido) 
    VALUES (%(email)s, %(password)s, %(user_type)s, %(cedula_identidad)s, %(name)s, %(last_name)s);
    '''
    values = {'email':user.email, 'password':psw,'user_type':user.userType,'cedula_identidad':user.ci,'name':user.name,'last_name':user.lastName,}
    response = postgreSQL_query(query,values,'post')
    print('La respuesta de la db al sign-up')
    print(response)
    return {"exito?": response}

@router.post("/login")
async def login(user: User):
    complete_user = authenticate_user(user.email,user.password)
    if not complete_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario/contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=float(access_token_expire_minutes))
    access_token = create_access_token(
        data={"sub": user.email,"user_type":complete_user['user_type']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer","user_type":complete_user['user_type']}

@router.post("/password-recovery")
async def recovery(user: User):
    start= 100000
    end= 999999
    numero_aleatorio = secrets.choice(range(start, end + 1))
    actual_user = get_user(user.email)
    print('el usuario encontrado')
    print(actual_user)
    if not actual_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no existe en el sistema",
            headers={"WWW-Authenticate": "Bearer"},
        )
    query = '''UPDATE usuario SET password_recovery_code = %(recovery_code)s WHERE correo = %(email)s'''
    values = {'email':actual_user['email'],'recovery_code':numero_aleatorio}
    response = postgreSQL_query(query,values,'post')
    print('La respuesta de la db al password-recovery')
    print(response)
    enviar_correo(actual_user['email'],'Código de Verificación','Su código de confirmación para reestablecer su contraseña es: {}'.format(numero_aleatorio))
    return {'response':response,'codigo':numero_aleatorio,'datos_encontrados':actual_user}

@router.post("/resend-email")
async def resend(user: User):
    start= 100000
    end= 999999
    numero_aleatorio = secrets.choice(range(start, end + 1))
    actual_user = get_user(user.email)
    if not actual_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no existe en el sistema",
            headers={"WWW-Authenticate": "Bearer"},
        )
    query = '''UPDATE usuario SET password_recovery_code = %(recovery_code)s WHERE correo = %(email)s'''
    values = {'email':actual_user['email'],'recovery_code':numero_aleatorio}
    response = postgreSQL_query(query,values,'post')
    print('La respuesta de la db al resend-email')
    print(response)
    enviar_correo(actual_user['email'],'Código de Verificación','Su código de confirmación para reestablecer su contraseña es: {}'.format(numero_aleatorio))
    return {'response':response,'codigo':numero_aleatorio,'datos_encontrados':actual_user}

@router.post("/confirm-password-recovery")
async def confirm_recovery(user: ChangePswd):
    actual_user = get_user(user.email)
    if not actual_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no existe en el sistema",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not actual_user['recovery_code'] == user.codigoConfirmacion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de recuperación de contraseña es incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    psw = get_password_hash(user.password)
    query = '''UPDATE usuario SET password_recovery_code = %(recovery_code)s,password = %(password)s WHERE correo = %(email)s'''
    values = {'email':actual_user['email'],'password':psw,'recovery_code':None}
    response = postgreSQL_query(query,values,'post')
    print('La respuesta de la db al confirm-password-recovery')
    print(response)
    enviar_correo(actual_user['email'],'Cambio de contraseña - Sistema construcción curricular','Su contraseña se ha modificado recientemente')
    return {'response':response,'datos_encontrados':actual_user}