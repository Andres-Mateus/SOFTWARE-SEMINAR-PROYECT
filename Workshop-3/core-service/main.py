from pickletools import float8
from fastapi import FastAPI
from services.user_services import create_user, autenticate_user
from services.fee_services import get_all_fees, create_fee, delete_fee
from services.vehicle_services import register_vehicle, get_vehicle, get_all_vehicles
from services.ticket_services import ticket_register, exit_register
from database import try_connection

app = FastAPI(title="Parking")


@app.get("/")
def root():
    return


@app.get("/conection/")
def try_connection_db():
    return {"message": f">{try_connection()}"}


@app.post("/user/")
def create_user_endpoint(idUser: str, username: str, password: str, tipo: str):
    return create_user(idUser, username, password, tipo)


@app.post("/login/")
def login_endpoint(username: str, password: str):
    return autenticate_user(username, password)


# -----     FEE     -------


@app.post("/fee/")
def create_fee_endpoint(idfee: str, descfee: str, type: str, price: float):
    return create_fee(idfee, descfee, type, price)


@app.get("/fee/")
def get_all_fees_endpoint():
    return get_all_fees()


@app.post("/fee/{idfee}")
def delete_fee_endpoint(idfee):
    return delete_fee(idfee)


# -----     VEHICLE     -------


@app.post("/vehicle/")
def register_vehicle_endpoint(licenseplate: str, type: str):
    return register_vehicle(licenseplate, type)


@app.get("/vechicle/")
def get_all_vehicles_endpoint():
    return get_all_vehicles()


@app.get("/vechicle/{idfee}")
def get_vehicle_endpoint(licenseplate: str):
    return get_vehicle(licenseplate)


# ----- TICKET -------


@app.post("/ticket/")
def ticket_register_endpoint(
    licenseplate: str, type: str, ownerdoc: str, idFee: str, idUser: str
):
    return ticket_register(licenseplate, type, ownerdoc, idFee, idUser)


@app.post("/ticket/{licenseplate}")
def exit_register_endpoint(licenseplate: str):
    return exit_register(licenseplate)
