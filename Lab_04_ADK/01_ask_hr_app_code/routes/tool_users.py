from datetime import datetime as dt
from ibm_watsonx_orchestrate.agent_builder.tools import tool

from models import (
    AtualizarCargoRequest,
    AtualizarEnderecoRequest,
    SolicitarFolgaRequest
)
from pydantic import BaseModel
from typing import List

# ============================================================
# Base de dados em memória
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

def find_user(user_id: int) -> dict:
    """Retorna o colaborador pelo ID ou lança erro."""
    for user in EMPLOYEES:
        if user["ID"] == user_id:
            return user
    raise ValueError("Colaborador não encontrado.")


# ============================================================
# Tools
# ============================================================

@tool (
    name="Detalhes de Perfil do Usuário",
    display_name="Dados completos do colaborador",
    description="Retorna os dados "
)
def user_profile_details(id: int) -> dict:
    """Retorna os dados completos do colaborador."""
    return find_user(id)

@tool(
    name="list_employees",
    display_name="List employees",
    description="Return a list of all employees."
)
def list_employees() -> List[Employee]:
    """
    Return all employees.

    Returns:
        List[Employee]: all employee records.
    """
    return EMPLOYEES

@tool
def time_off_balance(id: int) -> dict:
    """Retorna o saldo de folgas do colaborador."""
    user = find_user(id)
    return {"saldo_folgas_dias": user["Saldo de Folgas (dias)"]}


@tool
def request_time_off(request: SolicitarFolgaRequest) -> dict:
    """Registra uma solicitação de folga e atualiza o saldo."""

    user = find_user(request.id)

    try:
        inicio = dt.strptime(request.data_inicio, "%Y-%m-%d")
        fim = dt.strptime(request.data_fim, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Datas devem estar no formato YYYY-MM-DD.")

    dias = (fim - inicio).days
    if dias <= 0:
        raise ValueError("A data final deve ser posterior à data inicial.")

    saldo = float(user["Saldo de Folgas (dias)"])
    if dias > saldo:
        raise ValueError("Saldo de folgas insuficiente.")

    user["Folgas Solicitadas (dias)"] = dias
    user["Saldo de Folgas (dias)"] = saldo - dias

    return {
        "message": "Solicitação registrada com sucesso",
        "dias_solicitados": dias,
        "saldo_restante": user["Saldo de Folgas (dias)"]
    }


@tool
def update_title(request: AtualizarCargoRequest) -> dict:
    """Atualiza o cargo do colaborador."""
    user = find_user(request.id)

    user["Cargo"] = request.novo_cargo

    return {
        "message": "Cargo atualizado com sucesso",
        "cargo": request.novo_cargo
    }


@tool
def update_address(request: AtualizarEnderecoRequest) -> dict:
    """Atualiza o endereço do colaborador."""
    user = find_user(request.id)

    user["Endereço"] = request.novo_endereco

    return {
        "message": "Endereço atualizado com sucesso",
        "endereco": request.novo_endereco
    }