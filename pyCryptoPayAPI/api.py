import requests

MAIN_API_URL = "https://pay.crypt.bot/api/"
TEST_API_URL = "https://testnet-pay.crypt.bot/api/"

# noinspection PyPep8Naming
class pyCryptoPayException(Exception):
    def __init__(self, code, message, full_error = ""):
        self.code = code
        self.message = message
        self.full_error = full_error
        super().__init__(self.message)


# noinspection PyPep8Naming
class pyCryptoPayAPI:
    """
    Crypto Pay API Client
    """

    def __init__(self, api_token, test_net = False, print_errors = False, timeout = None):
        """
        Create the pyCryptoPayAPI instance.

        :param api_token: API token obtained via @CryptoBot
        :param test_net: (Optional) Use testnet instead of mainnet
        :param print_errors: (Optional) Print dumps on request errors
        :param timeout: (Optional) Request timeout
        """
        self.api_token = api_token
        self.test_net = test_net
        self.print_errors = print_errors
        self.timeout = timeout

    def __request(self, method, **kwargs):
        if kwargs:
            data = dict(kwargs)
        else:
            data = {}

        headers = {
            "Crypto-Pay-API-Token": self.api_token
        }
        try:
            resp = requests.get(
                (TEST_API_URL if self.test_net else MAIN_API_URL) + method,
                params=data,
                headers = headers,
                timeout=self.timeout
            ).json()
        except ValueError as ve:
            message = "Response decode failed: {}".format(ve)
            if self.print_errors:
                print(message)
            raise pyCryptoPayException(-2, message)
        except Exception as e:
            message = "Request unknown exception: {}".format(e)
            if self.print_errors:
                print(message)
            raise pyCryptoPayException(-3, message)
        if not resp:
            message = "None request response"
            if self.print_errors:
                print(message)
            raise pyCryptoPayException(-4, message)
        elif not resp.get("ok"):
            if self.print_errors:
                print("Response: {}".format(resp))
            if resp.get("error"):
                raise pyCryptoPayException(
                    resp["error"].get("code", 1),
                    resp["error"].get("name", "No info"),
                    full_error = str(resp["error"]))
            else:
                raise pyCryptoPayException(1, "No error info provided")
        else:
            return resp

    @staticmethod
    def get_assets():
        """
        Non-API method
        Returns the list of assets supported by Crypto Pay API.
        """
        return ["BTC", "TON", "ETH", "USDT", "USDC", "BUSD", "BNB"]

    def get_me(self):
        """
        getMe method
        Use this method to test your app's authentication token.

        :return: On success, returns basic information about an app.
        """
        method = "getMe"
        return self.__request(method).get("result")

    def create_invoice(
            self, asset, amount,
            description = None, hidden_message = None,
            paid_btn_name = None, paid_btn_url = None, payload = None,
            allow_comments = None, allow_anonymous = None,
            expires_in = None
    ):
        """
        createInvoice method
        Use this method to create a new invoice.

        :param asset: (String) Currency code. Supported assets: “BTC”, “TON”, “ETH”, “USDT”, “USDC” and “BUSD” (and should be "BNB").
        :param amount: (String) Amount of the invoice in float. For example: 125.50
        :param description: (String) Optional. Description for the invoice. User will see this description when they pay the invoice. Up to 1024 characters.
        :param hidden_message: (String) Optional. Text of the message that will be shown to a user after the invoice is paid. Up to 2o48 characters.
        :param paid_btn_name: (String) Optional. Name of the button that will be shown to a user after the invoice is paid. Supported names:
            viewItem – “View Item”
            openChannel – “View Channel”
            openBot – “Open Bot”
            callback – “Return”
        :param paid_btn_url: (String) Optional. Required if paid_btn_name is used.URL to be opened when the button is pressed. You can set any success link (for example, a link to your bot). Starts with https or http.
        :param payload: (String) Optional. Any data you want to attach to the invoice (for example, user ID, payment ID, ect). Up to 4kb.
        :param allow_comments: (Boolean) Optional. Allow a user to add a comment to the payment. Default is true.
        :param allow_anonymous: (Boolean) Optional. Allow a user to pay the invoice anonymously. Default is true.
        :param expires_in: (Number) Optional. You can set a payment time limit for the invoice in seconds. Values between 1-2678400 are accepted.
        :return: On success, returns an object of the created invoice (https://help.crypt.bot/crypto-pay-api#Invoice).
        """
        method = "createInvoice"
        params = {
            "asset": asset,
            "amount": amount,
        }
        if description:
            params["description"] = description
        if hidden_message:
            params["hidden_message"] = hidden_message
        if paid_btn_name:
            params["paid_btn_name"] = paid_btn_name
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
        return self.__request(method, **params).get("result")

    def transfer(
            self, user_id , asset, amount, spend_id,
            comment = None, disable_send_notification  = None
    ):
        """
        transfer method
        Use this method to send coins from your app's balance to a user.

        :param user_id: (Number) Telegram user ID. User must have previously used @CryptoBot (@CryptoTestnetBot for testnet).
        :param asset: (String) Currency code. Supported assets: “BTC”, “TON”, “ETH”, “USDT”, “USDC” and “BUSD” (and should be "BNB").
        :param amount: (String) Amount of the transfer in float. The minimum and maximum amounts for each of the support asset roughly correspond to the limit of 1-25000 USD. Use get_exchange_rates to convert amounts. For example: 125.50
        :param spend_id: (String) Unique ID to make your request idempotent and ensure that only one of the transfers with the same spend_id is accepted from your app. This parameter is useful when the transfer should be retried (i.e. request timeout, connection reset, 500 HTTP status, etc). Up to 64 symbols.
        :param comment: (String) Optional. Comment for the transfer. Users will see this comment when they receive a notification about the transfer. Up to 1024 symbols.
        :param disable_send_notification: (Boolean) Optional. Pass true if the user should not receive a notification about the transfer.Default is false.
        :return: On success, returns an object of the created transfer (https://help.crypt.bot/crypto-pay-api#Transfer).
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
        return self.__request(method, **params).get("result")

    def get_invoices(
            self, asset = None, invoice_ids = None, status = None, offset = None, count  = None
    ):
        """
        getInvoices method
        Use this method to get invoices of your app.

        :param asset: (String) Optional. Currency code. Supported assets: “BTC”, “TON”, “ETH”, “USDT”, “USDC” and “BUSD” (and should be "BNB").
        :param invoice_ids: (String) Optional. Invoice IDs separated by comma.
        :param status: (String) Optional. Status of invoices to be returned. Available statuses: “active” and “paid”. Defaults to all statuses.
        :param offset: (Number) Optional. Offset needed to return a specific subset of invoices. Default is 0.
        :param count: (Number) Optional. Number of invoices to be returned. Values between 1-1000 are accepted. Default is 100.
        :return: On success, returns an array of invoices (https://help.crypt.bot/crypto-pay-api#Invoice).
        """
        method = "getInvoices"
        params = {}
        if asset:
            params["asset"] = asset
        if invoice_ids:
            params["invoice_ids"] = invoice_ids
        if status:
            params["status"] = status
        if offset:
            params["offset"] = offset
        if count:
            params["count"] = count
        return self.__request(method, **params).get("result")

    def get_balance(self):
        """
        getBalance method
        Use this method to get a balance of your app.

        :return: Returns array of assets.
        """
        method = "getBalance"
        return self.__request(method).get("result")

    def get_exchange_rates(self):
        """
        getExchangeRates method
        Use this method to get exchange rates of supported currencies.

        :return: Returns array of currencies.
        """
        method = "getExchangeRates"
        return self.__request(method).get("result")

    def get_currencies(self):
        """
        getCurrencies method
        Use this method to get a list of supported currencies.

        :return: Returns array of currencies.
        """
        method = "getCurrencies"
        return self.__request(method).get("result")
