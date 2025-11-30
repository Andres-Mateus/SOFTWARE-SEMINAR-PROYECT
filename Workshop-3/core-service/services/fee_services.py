from database import run_query


def create_fee(idfee, desc, type, price):
    run_query(
        "INSERT INTO fee (idfee, descfee, type, pricefee) VALUES( %s, %s, %s, %s)",
        (idfee, desc, type, price),
    )
    return {"ok": f"Fee {idfee} registered succesfully."}


def get_fee(idfee):
    exist = run_query("SELECT * FROM fee WHERE idfee = %s", (idfee,), fetch=True)

    if exist:
        return exist[0]
    else:
        return {"error": f"Fee {idfee} doesn't exist."}


def get_all_fees():
    exist = run_query("SELECT * FROM fee ", fetch=True)

    if exist:
        return exist[0]
    else:
        return {"error": f"There is not fees registered."}


def delete_fee(idfee):
    exist = run_query("SELECT * FROM fee WHERE idfee=%s", (idfee,), fetch=True)
    if exist:
        run_query("DELETE FROM fee WHERE idfee=%s", (idfee,))
        return {"ok": f"Fee {idfee} was deleted"}
    else:
        return {"error": f"Fee {idfee} is not registered."}
