from fastapi import FastAPI

app = FastAPI()

employees = [
    {
        "e_id": 101,
        "e_name": "Abhi",
        "e_age": 25,
        "e_salary": 40000,
        "e_department": "SDE",
        "e_active_status": True
    },
    {
        "e_id": 102,
        "e_name": "Sunny",
        "e_age": 26,
        "e_salary": 55000,
        "e_department": "DS",
        "e_active_status": True
    },
    {
        "e_id": 103,
        "e_name": "Lalit",
        "e_age": 24,
        "e_salary": 200000,
        "e_department": "DE",
        "e_active_status": True
    },
    {
        "e_id": 104,
        "e_name": "Kalyani",
        "e_age": 27,
        "e_salary": 40000,
        "e_department": "SDE",
        "e_active_status": False
    },
    {
        "e_id": 105,
        "e_name": "Om",
        "e_age": 23,
        "e_salary": 5000,
        "e_department": "FSD",
        "e_active_status": True
    }
]


@app.get("/employees")
def GetEmployees():
    return employees


@app.get("/employees/{employee_id}")
def GetEmployee(employee_id: int):

    for employee in employees:
        if employee["e_id"] == employee_id:
            return employee

    return {"message": "Employee not found"}


@app.get("/employees/name-salary")
def GetNameSalary():
    return [
        {
            "e_name": employee["e_name"],
            "e_salary": employee["e_salary"]
        }
        for employee in employees
    ]

