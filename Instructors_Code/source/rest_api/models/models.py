from pydantic import BaseModel
from datetime import date

class SimulacaoRequest(BaseModel):
    salario_bruto: float
    data_admissao: date
    percentual_cv: float

class SimulacaoResponse(BaseModel):
    salario_bruto: float
    anos_servico: float
    ur_referencia: float

    percentual_patroc1: float
    percentual_patroc2: float

    valor_cv: float
    valor_patroc1: float
    valor_patroc2: float

    total_mensal: float