from pydantic import BaseModel

class CriarColaboradorRequest(BaseModel):
    nome: str
    saldo_folgas_dias: float
    cargo: str
    endereco: str

class AtualizarCargoRequest(BaseModel):
    id: str
    novo_cargo: str

class AtualizarEnderecoRequest(BaseModel):
    id: str
    novo_endereco: str

class SolicitarFolgaRequest(BaseModel):
    id: str
    data_inicio: str  
    data_fim: str    