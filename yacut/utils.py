import random
import string

from .models import URLMap

def generate_short_url(length=6):
    letters = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choice(letters) for _ in range(length))
        if not URLMap.query.filter_by(short=short_id).first():
            return ''.join(random.choice(letters) for _ in range(length))
