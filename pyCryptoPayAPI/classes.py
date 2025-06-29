from abc import ABC


class CrypoPayBase(ABC):
    """Base class for CryptoPay API classes."""
    def __init__(self, data):
        self.deserialize(data)

    def deserialize(self, data):
        """Deserialize the data into the class attributes."""
        for key, value in data.items():
            setattr(self, key, value)
            # if hasattr( self, key):
                # if isinstance(getattr(self, key), list):
                #     # If the attribute is a list, append the value
                #     getattr(self, key).append(value)
                # else:
                #     # Otherwise, set the attribute directly
                #     setattr(self, key, value)

    def __repr__(self):
        """Return a string representation of the class."""
        class_name = self.__class__.__name__
        attributes = ', '.join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"{class_name}({attributes})"


class Me(CrypoPayBase):
    """Class representing the current user."""
    def __init__(self, data):
        super().__init__(data)


class Invoice(CrypoPayBase):
    """Class representing a single invoice."""
    def __init__(self, data):
        self.invoice_id = None          # Unique ID for this invoice.
        self.hash = None                # Hash of the invoice.
        self.currency_type = None       # Type of the price, can be “crypto” or “fiat”.
        self.asset = None               # Cryptocurrency code if currency_type is "crypto".
        self.fiat = None                # Fiat currency code if currency_type is "fiat".
        self.amount = None              # Amount of the invoice.
        self.paid_asset = None          # Cryptocurrency alphabetic code for paid invoice.
        self.paid_amount = None         # Amount of the paid invoice.
        self.paid_fiat_rate = None      # Rate of the paid asset valued in fiat currency.
        self.accepted_assets = None     # List of assets which can be used to pay the invoice.
        self.fee_asset = None           # Asset of service fees charged when the invoice was paid.
        self.fee_amount = None          # Amount of service fees charged when the invoice was paid.
        self.fee_in_usd = None          # Amount in USD of service fees charged when the invoice was paid.
        self.pay_url = None             # Deprecated URL for paying the invoice.
        self.bot_invoice_url = None     # URL to pay the invoice via bot.
        self.mini_app_invoice_url = None# URL to pay the invoice via Mini App.
        self.web_app_invoice_url = None # URL to pay the invoice via Web App.
        self.description = None         # Description for this invoice.
        self.status = None              # Status of the transfer, can be “active”, “paid” or “expired”.
        self.swap_to = None             # The asset that will be attempted to be swapped into after payment.
        self.is_swapped = None          # Indicates whether the swap was successful.
        self.swapped_uid = None         # Unique identifier of the swap if is_swapped is true.
        self.swapped_to = None          # Asset into which the swap was made if is_swapped is true.
        self.swapped_rate = None        # Exchange rate at which the swap was executed if is_swapped is true.
        self.swapped_output = None      # Amount received as a result of the swap if is_swapped is true.
        self.swapped_usd_amount = None  # Resulting swap
        self.swapped_usd_rate = None    # USD exchange rate of the currency from swapped_to if is_swapped is true.
        self.created_at = None          # Date the invoice was created in ISO 8601 format.
        self.paid_usd_rate = None       # Price of the asset in USD if status is “paid”.
        self.usd_rate = None            # Deprecated price of the asset in USD.
        self.allow_comments = None      # True, if the user can add comment to the payment.
        self.allow_anonymous = None     # True, if the user can pay the invoice anonymously.
        self.expiration_date = None     # Date the invoice expires in ISO 8601 format.
        self.paid_at = None             # Date the invoice was paid in ISO 8601 format.
        self.paid_anonymously = None    # True, if the invoice was paid anonymously.
        self.comment = None             # Comment to the payment from the user.
        self.hidden_message = None      # Text of the hidden message for this invoice.
        self.payload = None             # Previously provided data for this invoice.
        self.paid_btn_name = None       # Label of the button, can be “viewItem”, “openChannel”, “openBot” or “callback”.
        self.paid_btn_url = None        # URL opened using the button.
        super().__init__(data)


class Transfer(CrypoPayBase):
    """Class representing a single transfer."""
    def __init__(self, data):
        self.transfer_id = None       # Unique ID for this transfer.
        self.spend_id = None          # Unique UTF-8 string.
        self.user_id = None           # Telegram user ID the transfer was sent to.
        self.asset = None             # Cryptocurrency alphabetic code.
        self.amount = None            # Amount of the transfer in float.
        self.status = None            # Status of the transfer, can only be “completed”.
        self.completed_at = None      # Date the transfer was completed in ISO 8601 format.
        self.comment = None           # Optional comment for this transfer.
        super().__init__(data)


class Check(CrypoPayBase):
    """Class representing a single check."""
    def __init__(self, data):
        self.check_id = None          # Unique ID for this check.
        self.hash = None              # Hash of the check.
        self.asset = None             # Cryptocurrency alphabetic code.
        self.amount = None            # Amount of the check in float.
        self.bot_check_url = None     # URL to activate the check.
        self.status = None            # Status of the check, can be “active” or “activated”.
        self.created_at = None        # Date the check was created in ISO 8601 format.
        self.activated_at = None      # Date the check was activated in ISO 8601 format.
        super().__init__(data)


class Balance(CrypoPayBase):
    """Class representing a single balance."""
    def __init__(self, data):
        self.currency_code = None # Cryptocurrency alphabetic code. Currently, can be “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC” (and “JET” for testnet).
        self.available = None     # Total available amount in float.
        self.onhold = None        # Unavailable amount currently is on hold in float.
        super().__init__(data)


class ExchangeRate(CrypoPayBase):
    """Class representing a single exchange rate."""
    def __init__(self, data):
        self.is_valid = None      # True, if the received rate is up-to-date.
        self.is_crypto = None     # True, if the source is the cryptocurrency.
        self.is_fiat = None       # True, if the source is the fiat currency.
        self.source = None        # Cryptocurrency alphabetic code.
        self.target = None        # Fiat currency code.
        self.rate = None          # The current rate of the source asset valued in the target currency.
        super().__init__(data)


class AppStats(CrypoPayBase):
    """Class representing application statistics."""
    def __init__(self, data):
        self.volume = None                # Total volume of paid invoices in USD.
        self.conversion = None            # Conversion of all created invoices.
        self.unique_users_count = None    # The unique number of users who have paid the invoice.
        self.created_invoice_count = None # Total created invoice count.
        self.paid_invoice_count = None    # Total paid invoice count.
        self.start_at = None              # The date on which the statistics calculation was started in ISO 8601 format.
        self.end_at = None                # The date on which the statistics calculation was ended in ISO 8601 format.
        super().__init__(data)


class Currency(CrypoPayBase):
    """Class representing a single currency (not officially declared in API)."""
    def __init__(self, data):
        self.is_blockchain = None    # True, if the currency is a blockchain asset.
        self.is_stablecoin = None    # True, if the currency is a stablecoin.
        self.is_fiat = None          # True, if the currency is a fiat currency.
        self.name = None             # Name of the currency.
        self.code = None             # Code of the currency.
        self.url = None              # URL of the currency's website.
        self.decimals = None         # Number of decimals for the currency.
        super().__init__(data)
