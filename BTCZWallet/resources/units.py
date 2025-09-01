
from decimal import Decimal


class Units():
    def __init__(self):
        super().__init__()

    
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