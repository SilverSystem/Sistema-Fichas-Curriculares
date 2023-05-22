import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
dbname= os.getenv('DB_NAME')
user= os.getenv('DB_USER')
password= os.getenv('DB_PASSWORD')
host= os.getenv('DB_HOST')
port= os.getenv('DB_PORT')


query_init = """CREATE TYPE tipoUC AS ENUM ('Básicas/Comunes', 'Transversales/Genéricas', 'Específicas/Técnicas');
CREATE TYPE modalidadFormacion AS ENUM ('Presencial', 'A distancia', 'Mixta');
CREATE TYPE userType AS ENUM ('Constructor Curricular', 'Coordinador curricular', 'Aprobador', 'Supervisor', 'Administrador', 'Presidencia');
CREATE TYPE evaluacionSegunProposito AS ENUM ('Diagnóstica', 'Formativa', 'Sumativa');
CREATE TYPE ubicacionTemporalEvaluacion AS ENUM ('Inicio', 'Desarrollo', 'Cierre');
CREATE TYPE estadoUC AS ENUM ('Aprobada', 'En curso', 'Con rechazo', 'Pendiente');
CREATE TYPE rolColectivoMesaEvaluacion AS ENUM ('COORDINACIÓN GENERAL', 'ACOMPAÑAMIENTO Y REVISIÓN', 'APOYO TÉCNICO (CONOCEDORES DEL ESTADO DEL ARTE)', 'APOYO LOGÍSTICO', 'SISTEMATIZACIÓN DE LA UNIDAD CURRICULAR');
CREATE TYPE tipoRecursos AS ENUM ('Materiales', 'Equipos', 'Programas (software)/Aplicaciones', 'Herramientas', 'Maquinarias', 'Instrumentos', 'Equipos de Seguridad e Higiene');

CREATE TABLE ficha_resumen_uc (
  id serial PRIMARY KEY,
  estado_uc estadoUC,
  area_especifica text,
  area_ocupacional text,
  sub_area_ocupacional text,
  codigo_uc text,
  tipo_uc tipoUC,
  uc text, modalidad_formacion_productiva modalidadFormacion,
  proposito_clave_uc text,
  dirigido_a text,
  sinopsis text,
  ejes_transversales_formacion text,
  perfil_facilitador text[],
  perfil_generico_ingreso text[],
  consideraciones_perfil_ingreso text,
  perfil_egreso text[],
  totalHoras decimal,
  nivel_dominio_esperado text
  );
CREATE TABLE recursos_educativos_digitales (
  id serial PRIMARY KEY, 
  uc_id integer REFERENCES ficha_resumen_uc (id),
  descripcion text
);
CREATE TABLE referencias_recomendadas (
  id serial PRIMARY KEY, 
  uc_id integer REFERENCES ficha_resumen_uc (id),
  enlaces_de_referencia text
);
CREATE TABLE colectivo_mesa_evaluacion (
  id serial PRIMARY KEY, 
  uc_id integer REFERENCES ficha_resumen_uc (id),
  rol rolColectivoMesaEvaluacion,
  nombre text,
  apellido text,
  dependencia_unidad text,
  nivel_de_formacion text
);
CREATE TABLE recursos_espacios_formacion (
  id serial PRIMARY KEY, 
  uc_id integer REFERENCES ficha_resumen_uc (id),
  numero_participantes integer
);
CREATE TABLE recursos (
  id serial PRIMARY KEY, 
  recursos_espacios_id integer REFERENCES recursos_espacios_formacion (id),
  tipo tipoRecursos,
  cantidad integer,
  unidad_medida text,
  especificaciones text
);
CREATE TABLE infraestructura_requerida_espacio_formacion (
  id serial PRIMARY KEY, 
  recursos_espacios_id integer REFERENCES recursos_espacios_formacion (id),
  caracteristicas_espacio text,
  dimensiones_espacio text,
  acceso_internet boolean,
  conexion_red boolean,
  audio boolean,
  video boolean,
  capacidad_minima_espacio integer,
  capacidad_maxima_espacio integer,
  evidencias_producto text,
  campo_aplicacion text
);
CREATE TABLE usuario (
  id serial PRIMARY KEY, 
  correo text,
  password text,
  user_type userType,
  cedula_identidad integer,
  nombre text,
  apellido text
);
CREATE TABLE tutor (
  id serial PRIMARY KEY, 
  uc_id integer REFERENCES ficha_resumen_uc (id),
  user_id integer REFERENCES usuario (id),
  fecha_revision timestamp with time zone
);
CREATE TABLE mapa_aprendizaje (
  id serial PRIMARY KEY,
  uc_id integer REFERENCES ficha_resumen_uc (id),
  realizacion_logro_participante text,
  horas_practicas decimal,
  horas_teoricas decimal,
  ejes_tematicos text[],
  observacion_directa text[],
  producto text[],
  conocimiento_comprension text[]
);
CREATE TABLE criterios_desempeño (
  id serial PRIMARY KEY,
  mapa_aprendizaje_id integer REFERENCES mapa_aprendizaje (id),
  descripcion text,
  lapso_ejecucion integer
);
CREATE TABLE guia_evaluacion (
  id serial PRIMARY KEY,
  mapa_aprendizaje_id integer REFERENCES mapa_aprendizaje (id),
  evaluacion_segun_su_proposito evaluacionSegunProposito,
  tecnicas_instrumento text[],
  formas_participacion text[],
  ubicacion_temporal_evaluacion ubicacionTemporalEvaluacion
);
CREATE TABLE estrategias_metodologicas_didacticas_pedagogicas (
  id serial PRIMARY KEY,
  mapa_aprendizaje_id integer REFERENCES mapa_aprendizaje (id),
  estrategias_enseñanza text[],
  medios_instruccionales text[],
  tecnicas_instruccionales text[],
  cognitivas text,
  metacognitivas text,
  estrategia_regulacion_recursos text,
  motivacionales text
);"""

def postgreSQL_query(query: str, values:dict, request_type:str = ''):
# Connect to an existing database
  conn = psycopg2.connect(dbname=dbname,user=user,password=password,host=host,port=port)
# Open a cursor to perform database operations
  cur = conn.cursor()
  if("get" in request_type):
    cur.execute(query,values)
    response = cur.fetchall() if (request_type == "get_all" or request_type == "get_some") else cur.fetchone()
    cur.close()
    conn.close()
    return response
  else:
    response = cur.execute(query,values)
    print('respuesta de la query enviada a la db es ---->',response)
    # Make the changes to the database persistent
    conn.commit()
    # Close communication with the database
    cur.close()
    conn.close()
    return {'success': True}