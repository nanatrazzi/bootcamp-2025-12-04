from typing import List, Optional
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


class NewEmployee(BaseModel):
    name: str
    role: str
    vacation_days: int
    address: str

@tool(
    name="list_employees",
    display_name="List employees",
    description="Return a list of all employees."
)
def list_employees() -> List[Employee]:
    print("[DEBUG] list_employees called")
    return EMPLOYEES


@tool(
    name="get_employee",
    display_name="Get employee",
    description="Get an employee by ID."
)
def get_employee(employee_id: int) -> Optional[Employee]:
    print("[DEBUG] get_employee called")
    for emp in EMPLOYEES:
        if emp.id == employee_id:
            return emp
    return None


@tool(
    name="search_employee",
    display_name="Search employee",
    description="Search employees by name."
)
def search_employee(name: str) -> List[Employee]:
    print("[DEBUG] search_employee called")
    name = name.lower()
    return [emp for emp in EMPLOYEES if name in emp.name.lower()]


@tool(
    name="update_employee_vacation",
    display_name="Update vacation days",
    description="Update number of vacation days of an employee."
)
def update_employee_vacation(employee_id: int, vacation_days: int) -> str:
    print("[DEBUG] update_employee_vacation called")
    for emp in EMPLOYEES:
        if emp.id == employee_id:
            emp.vacation_days = vacation_days
            return f"Vacation days updated to {vacation_days} for {emp.name}."
    return "Employee not found."


@tool(
    name="update_employee_address",
    display_name="Update employee address",
    description="Update the home address of an employee."
)
def update_employee_address(employee_id: int, new_address: str) -> str:
    print("[DEBUG] update_employee_address called")
    for emp in EMPLOYEES:
        if emp.id == employee_id:
            emp.address = new_address
            return f"Address updated to '{new_address}' for {emp.name}."
    return "Employee not found."


@tool(
    name="add_employee",
    display_name="Add employee",
    description="Add a new employee to the system."
)
def add_employee(data: NewEmployee) -> Employee:
    print("[DEBUG] add_employee called")
    new_id = max(emp.id for emp in EMPLOYEES) + 1
    new_emp = Employee(
        id=new_id,
        name=data.name,
        role=data.role,
        vacation_days=data.vacation_days,
        address=data.address
    )
    EMPLOYEES.append(new_emp)
    return new_emp


@tool(
    name="remove_employee",
    display_name="Remove employee",
    description="Remove an employee by ID."
)
def remove_employee(employee_id: int) -> str:
    print("[DEBUG] remove_employee called")
    for i, emp in enumerate(EMPLOYEES):
        if emp.id == employee_id:
            EMPLOYEES.pop(i)
            return f"Employee {emp.name} removed."
    return "Employee not found."