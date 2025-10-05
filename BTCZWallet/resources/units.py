
from decimal import Decimal
import base64

from nacl.secret import SecretBox
from nacl import utils


class Units():
    def __init__(self):
        super().__init__()


    def get_secret_key_bytes(self, secret_b64: str):
        return base64.urlsafe_b64decode(secret_b64)[:32]
    
    
    def encrypt_data(self, secret_b64, params: str) -> str:
        key = self.get_secret_key_bytes(secret_b64)
        box = SecretBox(key)
        nonce = utils.random(SecretBox.NONCE_SIZE)
        encrypted = box.encrypt(params.encode(), nonce)
        return base64.urlsafe_b64encode(encrypted).decode()
    

    def decrypt_data(self, secret_b64, ciphertext_b64: str) -> str:
        key = self.get_secret_key_bytes(secret_b64)
        box = SecretBox(key)
        encrypted = base64.urlsafe_b64decode(ciphertext_b64)
        return box.decrypt(encrypted).decode()

    
    def format_balance(self, value):
        value = Decimal(value)
        formatted_value = f"{value:.8f}"
        integer_part, decimal_part = formatted_value.split('.')
        if len(integer_part) > 4:
            digits_to_remove = len(integer_part) - 4
            formatted_decimal = decimal_part[:-digits_to_remove]
        else:
            formatted_decimal = decimal_part
        formatted_balance = f"{integer_part}.{formatted_decimal}"
        return formatted_balance
    

    def format_price(self, price):
        price = Decimal(price)

        if price > Decimal('0.00000001') and price < Decimal('0.0000001'):
            return f"{price:.10f}"
        elif price > Decimal('0.0000001') and price < Decimal('0.000001'):
            return f"{price:.9f}"
        elif price > Decimal('0.000001') and price < Decimal('0.00001'):
            return f"{price:.8f}"
        elif price > Decimal('0.00001') and price < Decimal('0.0001'):
            return f"{price:.7f}"
        elif price > Decimal('0.0001') and price < Decimal('0.001'):
            return f"{price:.6f}"
        elif price > Decimal('0.001') and price < Decimal('0.01'):
            return f"{price:.5f}"
        elif price > Decimal('0.01') and price < Decimal('0.1'):
            return f"{price:.4f}"
        elif price > Decimal('0.1') and price < Decimal('1'):
            return f"{price:.3f}"
        elif price > Decimal('1') and price < Decimal('10'):
            return f"{price:.2f}"
        elif price > Decimal('10') and price < Decimal('100'):
            return f"{price:.1f}"
        else:
            return f"{price:.0f}"