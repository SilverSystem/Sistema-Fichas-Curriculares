
from fastapi import Depends, HTTPException, APIRouter,status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from db.initdb import postgreSQL_query
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class FichaResume(BaseModel):
    estadoUC: str | None = None
    areaOcupacional:str | None = None
    subAreaOcupacional:str | None = None
    areaConocimiento:str | None = None
    uc:str | None = None
    codigoUc:int | None = None
    totalHorasFormacion:int | None = None
    tipoUc:str | None = None
    modalidadFormacion:str | None = None
    proposito:str | None = None
    dirigidoA:str | None = None
    nivelDominioEsperado:str | None = None
    sinopsis:str | None = None
    perfilFacilitador:list | None = None
    ejesTransversales:str | None = None
    perfilGenericoIngreso:list | None = None
    perfilEgreso:list | None = None
    consideracionesPerfilGenerico:str | None = None


@router.post("/fichas")
async def save_ficha_resumen(ficha: FichaResume):
    print(ficha)
    query = '''INSERT INTO ficha_resumen_uc (estado_uc, area_especifica, area_ocupacional, sub_area_ocupacional, codigo_uc, tipo_uc, uc, modalidad_formacion_productiva, proposito_clave_uc, dirigido_a, sinopsis, ejes_transversales_formacion, perfil_facilitador, perfil_generico_ingreso, consideraciones_perfil_ingreso, perfil_egreso, nivel_dominio_esperado, totalHoras) 
    VALUES (%(estado)s, %(area_especifica)s, %(area_ocupacional)s, %(sub_area_ocupacional)s, %(codigo_uc)s, %(tipo_uc)s, %(uc)s, %(modalidad_formacion_productiva)s, %(proposito_clave_uc)s, %(dirigido_a)s, %(sinopsis)s, %(ejes_transversales_formacion)s, %(perfil_facilitador)s, %(perfil_generico_ingreso)s, %(consideraciones_perfil_ingreso)s, %(perfil_egreso)s, %(nivel_dominio_esperado)s, %(totalHoras)s);
    '''
    values = {'estado':ficha.estadoUC,'area_especifica':ficha.areaConocimiento,'area_ocupacional':ficha.areaOcupacional,'sub_area_ocupacional':ficha.subAreaOcupacional,'codigo_uc':ficha.codigoUc,'tipo_uc':ficha.tipoUc,'uc':ficha.uc,'modalidad_formacion_productiva':ficha.modalidadFormacion,'proposito_clave_uc':ficha.proposito,'dirigido_a':ficha.dirigidoA,'sinopsis':ficha.sinopsis,'ejes_transversales_formacion':ficha.ejesTransversales,'perfil_facilitador':ficha.perfilFacilitador,'perfil_generico_ingreso':ficha.perfilGenericoIngreso,'consideraciones_perfil_ingreso':ficha.consideracionesPerfilGenerico,'perfil_egreso':ficha.perfilEgreso,'nivel_dominio_esperado':ficha.nivelDominioEsperado,'totalHoras': ficha.totalHorasFormacion}
    response = postgreSQL_query(query,values,'post')
    print('La respuesta de la db al sign-up')
    print(response)
    return {"exito en salvar la ficha?": response}

@router.get("/fichas")
async def get_fichas_resumen():
    query = 'SELECT * FROM ficha_resumen_uc'
    values = {}
    response = postgreSQL_query(query,values,'get_all')
    print('La respuesta de la db')
    print(response)
    return{'data':response }