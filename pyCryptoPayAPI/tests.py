import inspect, datetime
from time import sleep
try:
    from pyCryptoPayAPI import pyCryptoPayAPI, pyCryptoPayException
except:
    from api import pyCryptoPayAPI, pyCryptoPayException

test_api_token = "52586:AA2DKQyUAnZFELNOihEqjlfact0XsxoUmGy"

def run_and_print(f):
    try:
        sleep(1)
        print()
        print(inspect.getsourcelines(f)[0][0].strip())
        res = f()
        print(res)
        return res
    except pyCryptoPayException as pe:
        if pe.code in [-2]:
            print("API call failed. Code: {}, Message: {}".format(pe.code, pe.message))
        else:
            raise pe
    except Exception as e:
        raise e
    return None

def run_api_functions(result_as_class):
    client = pyCryptoPayAPI(test_api_token, print_errors=True, result_as_class=result_as_class)
    run_and_print(lambda: client.get_me())
    run_and_print(lambda: client.get_balance())
    run_and_print(lambda: client.get_exchange_rates())
    run_and_print(lambda: client.get_currencies())
    invoice = run_and_print(lambda: client.create_invoice(
        "TON",
        1,
        description="Test at {}".format(datetime.datetime.now()),
        hidden_message="Hidden in test",
        paid_btn_name="viewItem",
        paid_btn_url="https://help.crypt.bot/crypto-pay-api",
        payload="Payload in test",
        allow_comments=True,
        allow_anonymous=True,
        expires_in=None
    ))
    run_and_print(lambda: client.get_invoices(
        "TON",
        status="active",
        offset=0,
        count=10,
        return_items = True,
    ))
    run_and_print(lambda: client.delete_invoice(invoice.invoice_id if result_as_class else invoice["invoice_id"]))
    run_and_print(lambda: client.get_checks(
        "TON",
        status="active",
        offset=0,
        count=10,
    ))
    run_and_print(lambda: client.get_transfers(
        "TON",
        offset=0,
        count=10,
    ))

def test_api_functions_raw():
    run_api_functions(False)

def test_api_functions_class():
    run_api_functions(True)

test_api_functions_raw()
test_api_functions_class()
