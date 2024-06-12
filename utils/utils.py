import string
import random

def generate_string(length):
    all_symbols = string.ascii_uppercase + string.digits
    result = ''.join(random.choice(all_symbols) for _ in range(length))
    return result