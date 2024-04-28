import random
import string
def generate_receipt_number():
    receipt_number = ''.join(random.choices(string.digits, k=12))
    return receipt_number

