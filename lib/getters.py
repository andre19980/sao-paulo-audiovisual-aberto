import json

def capitais_brasileiras():
  with open("assets/uf-capitais-brasileiras.json", "r") as file:
    uf_capitais = json.load(file)

  return list(uf_capitais.keys())

def uf_capitais_brasileiras():
  with open("assets/uf-capitais-brasileiras.json", "r") as file:
    uf_capitais = json.load(file)
  
  return uf_capitais