from database import run_query
from datetime import datetime
from services.vehicle_services import register_vehicle, get_vehicle
from services.fee_services import get_fee


def ticket_register(licenseplate, type, ownerdoc, idFee, idUser):
    existe = run_query(
        "SELECT * FROM ticket WHERE licenseplate = %s AND exit IS NULL",
        (licenseplate,),
        fetch=True,
    )
    if existe:
        return {"error": "Vehicle is already inside with an active ticket"}

    if get_vehicle(licenseplate)["error"]:
        register_vehicle(licenseplate, type)

    run_query(
        "INSERT INTO ticket (ownerdoc, entry, licenseplate, idFee, idUser) VALUES (%s, %s, %s, %s, %s)",
        (ownerdoc, datetime.now(), licenseplate, idFee, idUser),
    )
    return {"ok": f"Vehicle {licenseplate} ticket created succesfully!."}


def exit_register(licenseplate):
    ticket = run_query(
        "SELECT * FROM ticket WHERE licenseplate = %s AND exit IS NULL",
        (licenseplate,),
        fetch=True,
    )
    if not ticket:
        return {"error": f"There is no active ticket for {licenseplate}"}
    ticket = ticket[0]
    entry_time = ticket[2]

    horas = round((datetime.now() - entry_time).seconds / 3600, 2) or 1
    pago = horas * get_fee(ticket[5])

    run_query(
        "UPDATE ticket SET exit = %s WHERE ticketid = %s",
        (datetime.now(), ticket[0]),
    )
    run_query(
        "INSERT INTO payment (ticketid, datepayment, payment) VALUES (%s, %s, %s)",
        (ticket[0], datetime.now(), pago),
    )
    return {"ok": f"Exit registered. Payment: {pago}"}
