import re
from django.core.exceptions import ValidationError

def validate_email(email):
    email_regex = r'^[a-z0-9]+@[a-z0-9]+\.[a-z]{2,3}$'
    if not re.match(email_regex, email):
        raise ValidationError("Invalid Email format. Email must be in lowercase, contain one '@', and one '.', and have a valid extension.")

def validate_password(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one numeric digit.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character.")
