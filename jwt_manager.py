from jwt import encode
from jwt import decode

def create_token(data:dict):
  token: str = encode(payload=data,key="roger-goated-nadal-goated",algorithm="HS256")
  return token

def validate_token(token:str):
  data:dict=decode(token,key="roger-goated-nadal-goated",algorithms=["HS256"])
  return data
