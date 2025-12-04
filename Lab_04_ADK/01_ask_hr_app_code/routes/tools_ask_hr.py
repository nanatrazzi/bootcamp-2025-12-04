from datetime import datetime as dt
from ibm_watsonx_orchestrate.agent_builder.tools import tool
 
# from models import (
#     AtualizarCargoRequest,
#     AtualizarEnderecoRequest,
#     SolicitarFolgaRequest
# )

from pydantic import BaseModel
from typing import List

# ============================================================
# Base de dados
# ============================================================

class Employee(BaseModel):
    id: int
    name: str
    role: str
    vacation_days: int
    address: str


EMPLOYEES = [
    Employee(id=1, name="Guilherme Indiciate", role="AI Engineer", vacation_days=20, address="Rua ABC, 123"),
    Employee(id=2, name="Nathalia Trazzi", role="TechLead", vacation_days=15, address="Av Watsonx, 98"),
    Employee(id=3, name="Savana Regina", role="Gestora de Projetos", vacation_days=25, address="Rua Blue, 44"),
]

# ============================================================
# Funções auxiliares
# ============================================================

def find_user(user_id: int) -> Employee:
    """Retorna o colaborador pelo ID ou lança erro."""
    for user in EMPLOYEES:
        if user.id == user_id:
            return user
    raise ValueError("Colaborador não encontrado.")

# ============================================================
# Tools
# ============================================================

@tool(
    name="get_user_profile",
    display_name="Consultar perfil do colaborador",
    description="Retorna todos os dados de um colaborador específico, incluindo nome, cargo, endereço e saldo de férias."
)
def user_profile_details(id: int) -> dict:
    """Retorna os dados completos do colaborador."""
    user = find_user(id)
    return user.dict()


@tool(
    name="list_all_employees",
    display_name="Listar todos os colaboradores",
    description="Retorna uma lista completa com todos os colaboradores cadastrados."
)
def list_employees() -> List[Employee]:
    """Retorna uma lista com todos os colaboradores."""
    return EMPLOYEES

@tool(
    name="get_vacation_balance",
    display_name="Consultar saldo de folgas",
    description="Retorna o saldo atual de férias/folgas disponíveis para um colaborador específico."
)
def time_off_balance(id: int) -> dict:
    """Retorna o saldo de folgas do colaborador."""
    user = find_user(id)
    return {"vacation_days_balance": user.vacation_days}


# @tool(
#     name="request_vacation",
#     display_name="Registrar solicitação de folga",
#     description="Registra uma nova solicitação de férias/folga e atualiza automaticamente o saldo do colaborador."
# )
# def request_time_off(request: SolicitarFolgaRequest) -> dict:
#     """Registra uma solicitação de folga e atualiza o saldo."""
#     user = find_user(request.id)

#     try:
#         inicio = dt.strptime(request.data_inicio, "%Y-%m-%d")
#         fim = dt.strptime(request.data_fim, "%Y-%m-%d")
#     except ValueError:
#         raise ValueError("Datas devem estar no formato YYYY-MM-DD.")

#     dias = (fim - inicio).days
#     if dias <= 0:
#         raise ValueError("A data final deve ser posterior à data inicial.")

#     if dias > user.vacation_days:
#         raise ValueError("Saldo de folgas insuficiente.")

#     user.vacation_days -= dias

#     return {
#         "message": "Solicitação registrada com sucesso.",
#         "dias_solicitados": dias,
#         "saldo_restante": user.vacation_days
#     }


# @tool(
#     name="update_employee_title",
#     display_name="Atualizar cargo do colaborador",
#     description="Atualiza o cargo/função de um colaborador específico usando o ID dele."
# )
# def update_title(request: AtualizarCargoRequest) -> dict:
#     """Atualiza o cargo do colaborador."""
#     user = find_user(request.id)

#     user.role = request.novo_cargo

#     return {
#         "message": "Cargo atualizado com sucesso.",
#         "cargo_atualizado": user.role
#     }


# @tool(
#     name="update_employee_address",
#     display_name="Atualizar endereço do colaborador",
#     description="Atualiza o endereço residencial cadastrado para um colaborador específico."
# )
# def update_address(request: AtualizarEnderecoRequest) -> dict:
#     """Atualiza o endereço do colaborador."""
#     user = find_user(request.id)

#     user.address = request.novo_endereco

#     return {
#         "message": "Endereço atualizado com sucesso.",
#         "endereco_atualizado": user.address
#     }
