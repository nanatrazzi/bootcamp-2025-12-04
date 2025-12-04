from typing import List
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from pydantic import BaseModel

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

@tool(
    name="TESTELISTEMPLOOYES",
    display_name="TESTE-LIST-EMPLOOYES",
    description="Return a list of all employees."
)
def list_employees() -> List[Employee]:
    """
    Return all employees.

    Returns:
        List[Employee]: all employee records.
    """
    return EMPLOYEES