import requests
from .classes import *

MAIN_API_URL = "https://pay.crypt.bot/api/"
TEST_API_URL = "https://testnet-pay.crypt.bot/api/"

# noinspection PyPep8Naming
class pyCryptoPayException(Exception):
    def __init__(self, code, name, message, full_error = "", status_code = None,
                 response_text = None, request_url = None, cause = None):
        self.code = code
        self.name = name
        self.message = message
        self.full_error = full_error
        self.status_code = status_code
        self.response_text = response_text
        self.request_url = request_url
        self.cause = cause
        super().__init__(self.message)


# noinspection PyPep8Naming
class pyCryptoPayAPI:
    """
    Crypto Pay API Client
    """

    def __init__(self, api_token, result_as_class = None, test_net = False, print_errors = False, timeout = 10):
        """
        Create the pyCryptoPayAPI instance.

        :param api_token: API token obtained via @CryptoBot
        :param result_as_class: (Optional) If True, returns instances of classes, otherwise returns raw data
        :param test_net: (Optional) Use testnet instead of mainnet
        :param print_errors: (Optional) Print dumps on request errors
        :param timeout: (Optional, default=10) Request timeout in seconds. Pass None to disable it.
        """
        self.api_token = api_token
        self.result_as_class = result_as_class if result_as_class else False
        self.test_net = test_net
        self.print_errors = print_errors
        self.timeout = timeout
        if result_as_class is None:
            print("Deprecation warning! The 'result_as_class' parameter should be set to False or True, default behaviour will be changed to 'True' in future versions!")


    def __request(self, method, **kwargs):
        if kwargs:
            data = dict(kwargs)
        else:
            data = {}

        headers = {
            "Crypto-Pay-API-Token": self.api_token
        }
        request_url = (TEST_API_URL if self.test_net else MAIN_API_URL) + method
        response = None
        try:
            response = requests.get(
                request_url,
                params=data,
                headers = headers,
                timeout=self.timeout
            )
            resp = response.json()
        except ValueError as ve:
            status_code = response.status_code if response is not None else None
            response_text = response.text if response is not None else None
            message = "Response decode failed: {}".format(ve)
            if self.print_errors:
                print(message)
            raise pyCryptoPayException(
                -2, "JSON", message, full_error=response_text or "",
                status_code=status_code, response_text=response_text,
                request_url=request_url, cause=ve) from ve
        except requests.RequestException as re:
            message = "Request transport exception: {}".format(re)
            if self.print_errors:
                print(message)
            raise pyCryptoPayException(
                -3, "TRANSPORT", message, request_url=request_url,
                cause=re) from re
        except Exception as e:
            message = "Request unknown exception: {}".format(e)
            if self.print_errors:
                print(message)
            raise pyCryptoPayException(
                -3, "UNKNOWN", message, request_url=request_url,
                cause=e) from e
        status_code = response.status_code if response is not None else None
        response_text = response.text if response is not None else None
        if not resp:
            message = "None request response"
            if self.print_errors:
                print(message)
            raise pyCryptoPayException(
                -4, "NONE", message, status_code=status_code,
                response_text=response_text, request_url=request_url)
        elif not resp.get("ok"):
            if self.print_errors:
                print("Response: {}".format(resp))
            if resp.get("error"):
                raise pyCryptoPayException(
                    resp["error"].get("code", 1),
                    resp["error"].get("name", "---"),
                    resp["error"].get("message", resp["error"].get("description", "No info")),
                    full_error=str(resp["error"]), status_code=status_code,
                    response_text=response_text, request_url=request_url)
            else:
                raise pyCryptoPayException(
                    -1, "NO_INFO", "No error info provided", status_code=status_code,
                    response_text=response_text, request_url=request_url)
        else:
            return resp

    @staticmethod
    def get_assets():
        """
        Non-API method
        Returns the documented mainnet asset list used by this SDK helper.
        This static list is not a live capability query and does not include
        testnet-only JET.
        """
        return ["USDT", "TON", "BTC", "ETH", "LTC", "BNB", "TRX", "USDC"]

    def process_webhook(self, raw_body, signature):
        """Verify and parse an inbound webhook using this client's token.

        ``raw_body`` must be exact HTTP bytes and ``signature`` must be the
        crypto-pay-api-signature header. The application owns HTTP reception,
        database-backed idempotency, request_date policy, acknowledgement, and
        business processing; this method only verifies and parses.
        """
        from .webhooks import parse_and_verify_webhook
        return parse_and_verify_webhook(raw_body, signature, self.api_token)

    def get_me(self):
        """
        getMe method
        Use this method to test your app's authentication token.

        :return: On success, returns basic information about an app.
        """
        method = "getMe"
        result = self.__request(method).get("result")
        return Me(result) if self.result_as_class else result

    def create_invoice(
            self, asset = None, amount = 0,
            description = None, hidden_message = None,
            paid_btn_name = None, paid_btn_url = None, payload = None,
            allow_comments = None, allow_anonymous = None,
            expires_in = None, currency_type = None, fiat = None,
            accepted_assets = None, swap_to = None
    ):
        """
        createInvoice method
        Use this method to create a new invoice.

        :param currency_type: (String) Optional. Type of the price, can be “crypto” or “fiat”. Defaults to crypto.
        :param asset: (String) Required if currency_type is “crypto”. Currency code. Supported documented mainnet assets: “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC”.
        :param fiat: (String) Optional. Required if currency_type is “fiat”. Fiat currency code. Supported fiat currencies: “USD”, “EUR”, “RUB”, “BYN”, “UAH”, “GBP”, “CNY”, “KZT”, “UZS”, “GEL”, “TRY”, “AMD”, “THB”, “INR”, “BRL”, “IDR”, “AZN”, “AED”, “PLN” and “ILS".
        :param accepted_assets: (String) Optional. List of cryptocurrency alphabetic codes separated by commas. Assets which can be used to pay the invoice. Available only if currency_type is “fiat”. Supported mainnet assets: “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC” (and “JET” for testnet). Defaults to all currencies.
        :param amount: (String) Invoice amount as a decimal string. For example: 125.50
        :param description: (String) Optional. Description for the invoice. User will see this description when they pay the invoice. Up to 1024 characters.
        :param hidden_message: (String) Optional. Text of the message that will be shown to a user after the invoice is paid. Up to 2048 characters.
        :param paid_btn_name: (String) Optional. Name of the button that will be shown to a user after the invoice is paid. Supported names:
            viewItem – “View Item”
            openChannel – “View Channel”
            openBot – “Open Bot”
            callback – “Return”
        :param swap_to : (String) Optional. The asset that will be attempted to be swapped into after the user makes a payment (the swap is not guaranteed). Supported assets: "USDT", "TON", "TRX", "ETH", "SOL", "BTC", "LTC".
        :param paid_btn_url: (String) Optional. Required if paid_btn_name is used. URL to be opened when the button is pressed. You can set any success link (for example, a link to your bot). Starts with https or http.
        :param payload: (String) Optional. Any data you want to attach to the invoice (for example, user ID or payment ID). Up to 4 KB.
        :param allow_comments: (Boolean) Optional. Allow a user to add a comment to the payment. Default is true.
        :param allow_anonymous: (Boolean) Optional. Allow a user to pay the invoice anonymously. Default is true.
        :param expires_in: (Number) Optional. You can set a payment time limit for the invoice in seconds. Values between 1-2678400 are accepted.
        :return: On success, returns an object of the created invoice (https://help.cr.bot/en/articles/10279948-crypto-pay-api).
        """
        method = "createInvoice"
        params = {
            "amount": amount if amount else 0,
        }
        if currency_type:
            params["currency_type"] = currency_type
        if asset:
            params["asset"] = asset
        if fiat:
            params["fiat"] = fiat
        if accepted_assets:
            params["accepted_assets"] = accepted_assets
        if description:
            params["description"] = description
        if hidden_message:
            params["hidden_message"] = hidden_message
        if paid_btn_name:
            params["paid_btn_name"] = paid_btn_name
        if swap_to:
            params["swap_to"] = swap_to
        if paid_btn_url:
            params["paid_btn_url"] = paid_btn_url
        if payload:
            params["payload"] = payload
        if allow_comments is not None:
            params["allow_comments"] = allow_comments
        if allow_anonymous is not None:
            params["allow_anonymous"] = allow_anonymous
        if expires_in:
            params["expires_in"] = expires_in
        result = self.__request(method, **params).get("result")
        return Invoice(result) if self.result_as_class else result

    def delete_invoice(self, invoice_id):
        """
        deleteInvoice method
        Use this method to delete invoices created by your app.

        :param invoice_id: (Number) Invoice ID to be deleted.
        :return: Returns True on success.
        """
        method = "deleteInvoice"
        params = {
            "invoice_id": invoice_id
        }
        result = self.__request(method, **params).get("result")
        return result

    def transfer(
            self, user_id , asset, amount, spend_id,
            comment = None, disable_send_notification  = None
    ):
        """
        transfer method
        Use this method to send coins from your app's balance to a user.

        :param user_id: (Number) Telegram user ID. User must have previously used @CryptoBot (@CryptoTestnetBot for testnet).
        :param asset: (String) Currency code. Supported documented mainnet assets: “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC” (and “JET” for testnet).
        :param amount: (String) Transfer amount as a decimal string. The minimum and maximum amounts for each supported asset roughly correspond to the limit of 1-25000 USD. Use get_exchange_rates to convert amounts. For example: 125.50
        :param spend_id: (String) Unique ID to make your request idempotent and ensure that only one of the transfers with the same spend_id is accepted from your app. This parameter is useful when the transfer should be retried (i.e. request timeout, connection reset, 500 HTTP status, etc). Up to 64 symbols.
        :param comment: (String) Optional. Comment for the transfer. Users will see this comment when they receive a notification about the transfer. Up to 1024 symbols.
        :param disable_send_notification: (Boolean) Optional. Pass true if the user should not receive a notification about the transfer. Default is false.
        :return: On success, returns an object of the created transfer (https://help.cr.bot/en/articles/10279948-crypto-pay-api).
        """
        method = "transfer"
        params = {
            "user_id": user_id ,
            "asset": asset,
            "amount": amount,
            "spend_id": spend_id,
        }
        if comment:
            params["comment"] = comment
        if disable_send_notification is not None:
            params["disable_send_notification"] = disable_send_notification
        result = self.__request(method, **params).get("result")
        return Transfer(result) if self.result_as_class else result

    def get_invoices(
            self, asset = None, fiat = None, invoice_ids = None, status = None, offset = None, count  = None, return_items = False
    ):
        """
        getInvoices method
        Use this method to get invoices of your app.

        :param asset: (String) Optional. Cryptocurrency alphabetic code. Supported assets: “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC” (and “JET” for testnet). Defaults to all currencies.
        :param fiat: (String) Optional. Fiat currency code. Supported fiat currencies: “USD”, “EUR”, “RUB”, “BYN”, “UAH”, “GBP”, “CNY”, “KZT”, “UZS”, “GEL”, “TRY”, “AMD”, “THB”, “INR”, “BRL”, “IDR”, “AZN”, “AED”, “PLN” and “ILS". Defaults to all currencies.
        :param invoice_ids: (String) Optional. Invoice IDs separated by comma.
        :param status: (String) Optional. Status of invoices to be returned. Available statuses: “active” and “paid”. Defaults to all statuses.
        :param offset: (Number) Optional. Offset needed to return a specific subset of invoices. Default is 0.
        :param count: (Number) Optional. Number of invoices to be returned. Values between 1-1000 are accepted. Default is 100.
        :param return_items: (Boolean) Optional. Return items instead of the whole response. Default is False (for compatibility), recommended True.
        :return: On success, returns an array of invoices (https://help.crypt.bot/crypto-pay-api#Invoice).
        """
        method = "getInvoices"
        params = {}
        if asset:
            params["asset"] = asset
        if fiat:
            params["fiat"] = fiat
        if invoice_ids:
            params["invoice_ids"] = invoice_ids
        if status:
            params["status"] = status
        if offset:
            params["offset"] = offset
        if count:
            params["count"] = count
        if params:
            result = self.__request(method, **params).get("result")
        else:
            result = self.__request(method).get("result")
        if not result:
            return [] if return_items else None
        elif self.result_as_class:
            return [Invoice(item) for item in result.get("items", [])]
        elif return_items:
            return result.get("items")
        else:
            return result

    def get_checks(
            self, asset = None, check_ids = None, status = None, offset = None, count = None, return_items = True
    ):
        """
        getChecks method
        Use this method to get checks created by your app.

        :param asset: (String) Optional. Cryptocurrency alphabetic code. Supported documented mainnet assets: “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC” (and “JET” for testnet). Defaults to all currencies.
        :param check_ids: (String) Optional. List of check IDs separated by comma.
        :param status: (String) Optional. Status of check to be returned. Available statuses: “active” and “activated”. Defaults to all statuses.
        :param offset: (Number) Optional. Offset needed to return a specific subset of check. Defaults to 0.
        :param count: (Number) Optional. Number of check to be returned. Values between 1-1000 are accepted. Defaults to 100.
        :param return_items: (Boolean) Optional. Return items instead of the whole response. Default is True.
        :return: On success, returns an array of Checks (https://help.crypt.bot/crypto-pay-api#Check).
        """
        method = "getChecks"
        params = {}
        if asset:
            params["asset"] = asset
        if check_ids:
            params["check_ids"] = check_ids
        if status:
            params["status"] = status
        if offset:
            params["offset"] = offset
        if count:
            params["count"] = count
        if params:
            result = self.__request(method, **params).get("result")
        else:
            result = self.__request(method).get("result")
        if not result:
            return [] if return_items else None
        elif self.result_as_class:
            return [Check(item) for item in result.get("items", [])]
        elif return_items:
            return result.get("items")
        else:
            return result

    def get_transfers(
            self, asset = None, transfer_ids = None, spend_id = None, offset = None, count = None, return_items = True
    ):
        """
        getTransfers method
        Use this method to get transfers created by your app.

        :param asset: (String) Optional. Cryptocurrency alphabetic code. Supported documented mainnet assets: “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC” (and “JET” for testnet). Defaults to all currencies.
        :param transfer_ids: (String) Optional. List of transfer IDs separated by comma.
        :param spend_id : (String) Optional. Unique UTF-8 transfer string.
        :param offset: (Number) Optional. Offset needed to return a specific subset of transfers. Defaults to 0.
        :param count: (Number) Optional. Number of transfers to be returned. Values between 1-1000 are accepted. Defaults to 100.
        :param return_items: (Boolean) Optional. Return items instead of the whole response. Default is True.
        :return: On success, returns an array of transfers (https://help.crypt.bot/crypto-pay-api#Transfer).
        """
        method = "getTransfers"
        params = {}
        if asset:
            params["asset"] = asset
        if transfer_ids:
            params["transfer_ids"] = transfer_ids
        if spend_id:
            params["spend_id"] = spend_id
        if offset:
            params["offset"] = offset
        if count:
            params["count"] = count
        if params:
            result = self.__request(method, **params).get("result")
        else:
            result = self.__request(method).get("result")
        if not result:
            return [] if return_items else None
        elif self.result_as_class:
            return [Transfer(item) for item in result.get("items", [])]
        elif return_items:
            return result.get("items")
        else:
            return result

    def get_balance(self):
        """
        getBalance method
        Use this method to get a balance of your app.

        :return: Returns array of assets.
        """
        method = "getBalance"
        result = self.__request(method).get("result")
        if not result:
            return []
        elif self.result_as_class:
            return [Balance(item) for item in result]
        else:
            return result

    def get_exchange_rates(self):
        """
        getExchangeRates method
        Use this method to get exchange rates of supported currencies.

        :return: Returns array of currencies.
        """
        method = "getExchangeRates"
        result = self.__request(method).get("result")
        if not result:
            return []
        elif self.result_as_class:
            return [ExchangeRate(item) for item in result]
        else:
            return result

    def get_currencies(self):
        """
        getCurrencies method
        Use this method to get a list of supported currencies.

        :return: Returns array of currencies.
        """
        method = "getCurrencies"
        result = self.__request(method).get("result")
        if not result:
            return []
        elif self.result_as_class:
            return [Currency(item) for item in result]
        else:
            return result

    def create_check(
            self, asset, amount, pin_to_user_id = None, pin_to_username = None
    ):
        """
        createCheck method
        Use this method to create a new check.

        :param asset: (String) Cryptocurrency alphabetic code. Supported documented mainnet assets: “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC” (and “JET” for testnet).
        :param amount: (String) Amount of the check in float. For example: 125.50
        :param pin_to_user_id: (Number) Optional. ID of the user who will be able to activate the check.
        :param pin_to_username: (String) Optional. A user with the specified username will be able to activate the check.
        :return: On success, returns an object of the created check (https://help.crypt.bot/crypto-pay-api#Check).
        """
        method = "createCheck"
        params = {
            "asset": asset,
            "amount": amount,
        }
        if pin_to_user_id:
            params["pin_to_user_id"] = pin_to_user_id
        if pin_to_username:
            params["pin_to_username"] = pin_to_username
        result =  self.__request(method, **params).get("result")
        return Check(result) if self.result_as_class else result

    def delete_check(self, check_id):
        """
        deleteCheck method
        Use this method to delete checks created by your app.

        :param check_id: (Number) Check ID to be deleted.
        :return: Returns True on success.

        """
        method = "deleteCheck"
        params = {
            "check_id": check_id
        }
        return self.__request(method, **params).get("result")

    def get_stats(self, start_at = None, end_at = None):
        """
        getStats method
        Use this method to get app statistics.

        :param start_at: (DateTime/String) Optional. Date from which start calculating statistics in ISO 8601 format. Defaults is current date minus 24 hours.
        :param end_at: (DateTime/String) Optional. The date on which to finish calculating statistics in ISO 8601 format. Defaults is current date.
        :return: Returns AppStats.
        """
        method = "getStats"
        params = {}
        if start_at:
            params["start_at"] = start_at if isinstance(start_at, str) else start_at.isoformat()
        if end_at:
            params["end_at"] = end_at if isinstance(end_at, str) else end_at.isoformat()
        result = self.__request(method, **params).get("result")
        return AppStats(result) if self.result_as_class else result
