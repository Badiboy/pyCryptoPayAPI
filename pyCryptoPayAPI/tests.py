import inspect, datetime
import os
from time import sleep

try:
    from pyCryptoPayAPI import pyCryptoPayAPI, pyCryptoPayException
    from pyCryptoPayAPI.test_config import load_test_api_token
except:
    from api import pyCryptoPayAPI, pyCryptoPayException
    from test_config import load_test_api_token

def get_live_test_api_token():
    """Load the local live token only for an explicitly requested live run."""
    if os.environ.get("RUN_CRYPTO_PAY_LIVE_TESTS") != "1":
        import pytest
        pytest.skip("live Crypto Pay API tests require RUN_CRYPTO_PAY_LIVE_TESTS=1")
    return load_test_api_token()

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
    client = pyCryptoPayAPI(get_live_test_api_token(), print_errors=True, result_as_class=result_as_class)
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

if __name__ == "__main__":
    test_api_functions_raw()
    test_api_functions_class()
