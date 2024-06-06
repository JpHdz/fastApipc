from fastapi import FastAPI,Body, Path, Query, Request, HTTPException, Depends;
from fastapi.responses import HTMLResponse, JSONResponse;
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from jwt_manager import create_token, validate_token
from typing import Coroutine, Optional, List
from fastapi.security import HTTPBearer
from config.database import Session, engine, Base
from models.computer import Computer as ComputerModel
from fastapi.encoders import jsonable_encoder

app = FastAPI();
app.title = "Venta de computadoras"


Base.metadata.create_all(bind=engine)

class Computer(BaseModel):
    id: Optional[int] = None #Indicamos que es opcional
    modelo: str = Field(min_length=5, max_length=50)
    marca: str = Field(min_length=5, max_length=25)
    color: str = Field(min_length=1, max_length=15)
    ram: str = Field(min_length=1, max_length=15)
    almacenamiento: str = Field(min_length=1, max_length=15)

    class Config:
        json_schema_extra = {
            "example":{
                "id": 1,
                "modelo": "Asus-tra-431",
                "marca": "Asus",
                "color": "Rojo",
                "ram": "16gb",
                "almacenamiento": "1tb"
            }
        }


# computadoras = [
#   {
#     "id":1,
#     "marca":"asus",
#     "modelo":"asusx10z",
#     "color": "rojo",
#     "ram":"16gb",
#     "almacenamiento":"1tb"
#   },
#   {
#     "id":2,
#     "marca":"lenovo",
#     "modelo":"lenovoc40",
#     "color": "azul",
#     "ram":"16gb",
#     "almacenamiento":"1tb"
#   },
#   {
#     "id":3,
#     "marca":"acer",
#     "modelo":"acerm21",
#     "color": "negro",
#     "ram":"16gb",
#     "almacenamiento":"2tb"
#   },
#   {
#     "id":4,
#     "marca":"mac",
#     "modelo":"macbook12",
#     "color": "blanco",
#     "ram":"32gb",
#     "almacenamiento":"5tb"
#   },
#   {
#     "id":5,
#     "marca":"asus",
#     "modelo":"asusx430z",
#     "color": "rojo",
#     "ram":"32gb",
#     "almacenamiento":"2tb"
#   }
# ]

class User(BaseModel):
  email:str
  password:str

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if(data['email'] != "jpnator18@gmail.com"):
            raise HTTPException(status_code=403, detail="Credenciales invalidas")

@app.post('/login',tags=['auth'])
def login(user:User):
  if user.email == "jpnator18@gmail.com" and user.password == "12345678":
    token:str = create_token(user.dict())
    return JSONResponse(status_code=200,content=token) 



@app.get("/", tags=["home"])
def message():
  return HTMLResponse('<h1>Menu principal</h1>');


@app.get("/computadoras", tags=["computadoras"],status_code=200,dependencies=[Depends(JWTBearer())])
def get_computadoras():
  db = Session()
  result = db.query(ComputerModel).all()
  return JSONResponse(content=jsonable_encoder(result),status_code=200)

@app.get("/computadoras:{id}",tags=["computadoras"])
def get_computadoras(id : int):
  #  for item in computadoras:
  #   if item["id"] == id:
  #     return item
  #  return []
   db = Session()
   result = db.query(ComputerModel).filter(ComputerModel.id == id).first()
   if not result:
      return JSONResponse(status_code=404,content={'message': 'No encontrado'})
   return JSONResponse(status_code=200, content=jsonable_encoder(result))

@app.get('/computadoras/', tags=['computadoras'])
def get_computadoras_by_marca(marca:str):
  # res = []
  # for computadora in computadoras:
  #   if computadora["marca"] == marca:
  #      res.append(computadora)
  # return res
   db = Session()
   result = db.query(ComputerModel).filter(ComputerModel.marca == marca).all()
   return JSONResponse(status_code=200, content=jsonable_encoder(result))


# Realizar los endpoints para la venta de computadoras con una 
#lista de 5 registros con los siguientes valores: id, marca, modelo,
# color, ram y almacenamiento. Realiza los endpoints ya hechos en 
#clase, en lugar de get by categoria sera get by marca, de manera 
#que se obtengatodo el cuerpo de la computadora por la marca. 
#En caso de ser mas de una mostrara todas las que sea de la misma 
#marca

# @app.post('/computadoras', tags=['computadoras'])
# def create_computadora(id: int = Body(), marca:str = Body(), modelo:str = Body(),color:str = Body(),ram:str = Body(),almacenamiento:str = Body()):
#   computadoras.append({
#     "id": id,
#     "marca": marca,
#     "modelo": modelo,
#     "color": color,
#     "ram": ram,
#     "almacenamiento": almacenamiento
#   })
#   return computadoras


@app.post('/computadoras', tags=['computadoras'])
def create_computadora(computer: Computer) -> dict:
  # computadoras.append({
  #   "id": id,
  #   "marca": marca,
  #   "modelo": modelo,
  #   "color": color,
  #   "ram": ram,
  #   "almacenamiento": almacenamiento
  # })
  # return computadoras
   db = Session()
   new_computer = ComputerModel(**computer.model_dump())
   db.add(new_computer)
   db.commit()
   return JSONResponse(content={"Message" : "Se ha registrado la computadora"}, status_code=201)


@app.put('/computadoras/{idQuery}', tags=['computadoras'])
def update_computadora(id: int, computer:Computer) -> dict:
  # for item in computadoras:
  #   if item["id"] == idQuery:
  #     item.update({
  #         "id": id,
  #         "marca": marca,
  #         "modelo": modelo,
  #         "color": color,
  #         "ram": ram,
  #         "almacenamiento": almacenamiento
  #     })
  # return computadoras
   db = Session()
   result = db.query(ComputerModel).filter(ComputerModel.id == id).first()
   if not result:
      return JSONResponse(status_code=404, content={'message':'No encontrado'})
   result.marca = computer.marca  
   result.modelo = computer.modelo
   result.color = computer.color
   result.ram = computer.ram
   result.almacenamiento = computer.almacenamiento

   db.commit()

   return JSONResponse(content={"Message":"Se ha modificado la computadora"}, status_code=202)

@app.delete('/computadoras/{id}', tags=['computadoras'], response_model = List[Computer],status_code=200)
def delete_computadora(id: int) -> dict:
  #  nuevo = computadoras.copy()
  #  computadoras.clear()
  #  for item in nuevo:
  #    if item["id"] != id:
  #       computadoras.append(item)
  #  return computadoras
   db = Session()
   result = db.query(ComputerModel).filter(ComputerModel.id == id).first()

   if not result:
      return JSONResponse(status_code=404, content={'message':'No encontrado'})
   db.delete(result)
   db.commit()
   return JSONResponse(status_code=202, content={'message':'Se ha eliminado la computadora'})
