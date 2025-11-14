import uvicorn
import os
import csv
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="BeClever API", 
    description="API para consultar datos y documentos.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

### Configuración CSV ###
CSV_FIELDS = [
    "tipo_id","num_identificacion","nombre_completo","nombres","primer_apellido",
    "segundo_apellido","fecha_nacimiento","genero_cliente","edad","grupo_pad",
    "cod_ciudad","ciudad","cod_depto","departamento","celular_1","productos_aprob",
    "disponible","gastos_fliar","disponible_pp","plazo_pp","tasa_pp","monto_pp",
    "cuota_pp","Monto_Lbz_60","Monto_Lbz_72","Monto_Lbz_84","Monto_Lbz_96",
    "Cuota_Lbz_60","Cuota_Lbz_72","Cuota_Lbz_84","Cuota_Lbz_96"
]

def _csv_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(base_dir, "docs", "data.csv")
    return os.path.normpath(p)

# Modelo de entrada (payload de app externa)
class EntradaCampania(BaseModel):
    # La otra app envía muchos campos; aquí listamos los que usamos
    num_telefono: str
    tipo_id: str
    num_identificacion: str
    nombre_completo: str
    nombres: str
    primer_apellido: str
    segundo_apellido: str
    fecha_nacimiento: str
    genero_cliente: str
    edad: str
    grupo_pad: str
    cod_ciudad: str
    ciudad: str
    cod_depto: str
    departamento: str
    productos_aprob: str
    disponible: str
    gastos_fliar: str
    disponible_pp: str
    plazo_pp: str
    tasa_pp: str
    monto_pp: str
    cuota_pp: str
    Monto_Lbz_60: str
    Monto_Lbz_72: str
    Monto_Lbz_84: str
    Monto_Lbz_96: str
    Cuota_Lbz_60: str
    Cuota_Lbz_72: str
    Cuota_Lbz_84: str
    Cuota_Lbz_96: str

    # Campos adicionales (opcionales)
    id_cliente: Optional[str] = None


@app.get("/filter/{id}")
def filter_data(id: str):
    """
    Devuelve la fila del CSV donde 'num_identificacion' coincida con el id.
    - 'id' (obligatorio): Refiere al número de identificación o documento de identidad a buscar.

    Returns:
        dict: Fila encontrada como diccionario, o mensaje si no se encuentra.
    """
    csv_path = _csv_path()

    try:
        with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            reader.fieldnames = [field.strip() for field in reader.fieldnames]
            for row in reader:
                row = {k.strip(): v for k, v in row.items()}
                id_match = str(row.get('num_identificacion', '')).strip() == id.strip()
                if id_match:
                    return row

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="CSV file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "No se encontró ninguna coincidencia."}


@app.post("/append")
def append_row(data: EntradaCampania):
    """
    Recibe un registro (de la otra app) y lo agrega como nueva fila al CSV,
    mapeando 'num_telefono' -> 'celular_1' y respetando el encabezado original.
    """
    csv_path = _csv_path()
    try:
        row = {
            "tipo_id": data.tipo_id,
            "num_identificacion": data.num_identificacion,
            "nombre_completo": data.nombre_completo,
            "nombres": data.nombres,
            "primer_apellido": data.primer_apellido,
            "segundo_apellido": data.segundo_apellido,
            "fecha_nacimiento": data.fecha_nacimiento,
            "genero_cliente": data.genero_cliente,
            "edad": data.edad,
            "grupo_pad": data.grupo_pad,
            "cod_ciudad": data.cod_ciudad,
            "ciudad": data.ciudad,
            "cod_depto": data.cod_depto,
            "departamento": data.departamento,
            "celular_1": data.num_telefono,  # mapeo clave
            "productos_aprob": data.productos_aprob,
            "disponible": data.disponible,
            "gastos_fliar": data.gastos_fliar,
            "disponible_pp": data.disponible_pp,
            "plazo_pp": data.plazo_pp,
            "tasa_pp": data.tasa_pp,
            "monto_pp": data.monto_pp,
            "cuota_pp": data.cuota_pp,
            "Monto_Lbz_60": data.Monto_Lbz_60,
            "Monto_Lbz_72": data.Monto_Lbz_72,
            "Monto_Lbz_84": data.Monto_Lbz_84,
            "Monto_Lbz_96": data.Monto_Lbz_96,
            "Cuota_Lbz_60": data.Cuota_Lbz_60,
            "Cuota_Lbz_72": data.Cuota_Lbz_72,
            "Cuota_Lbz_84": data.Cuota_Lbz_84,
            "Cuota_Lbz_96": data.Cuota_Lbz_96,
        }

        with open(csv_path, "rb+") as f:
            f.seek(0, os.SEEK_END)
            if f.tell() > 0:
                f.seek(-1, os.SEEK_END)
                last_char = f.read(1)
                if last_char != b'\n':
                    f.write(b'\n')

        with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, delimiter=";")
            writer.writerow(row)

        logger.info("Fila agregada para num_identificacion=%s", data.num_identificacion)
        return {"message": "Registro agregado correctamente.", "num_identificacion": data.num_identificacion}

    except Exception as e:
        logger.exception("Error al escribir en el CSV")
        raise HTTPException(status_code=500, detail=f"Error al escribir en el CSV: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
