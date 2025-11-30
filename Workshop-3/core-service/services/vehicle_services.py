from database import run_query
from datetime import datetime


def register_vehicle(lisenceplate, type):
    exist = run_query(
        "SELECT * FROM vehicle WHERE licenseplate = %s",
        (lisenceplate,),
        fetch=True,
    )

    if exist:
        return {"error": "Vehículo ya se encuentra en el sistema."}

    run_query(
        "INSERT INTO vehicle (licenseplate, type, dateregistered) VALUES (%s, %s, %s)",
        (lisenceplate, type, datetime.now()),
    )
    return {"ok": f"Vehículo {lisenceplate} ingresó correctamente."}


def get_vehicle(licenseplate):
    exist = run_query(
        "SELECT * FROM vehicle WHERE licenseplate = %s", (licenseplate,), fetch=True
    )

    if exist:
        return exist[0]
    else:
        return {"error": f"Vehicle {licenseplate} doesn't exist."}


def get_all_vehicles():
    exist = run_query("SELECT * FROM vehicle ", fetch=True)

    if exist:
        return exist[0]
    else:
        return {"error": f"There is not vehicles registered."}
