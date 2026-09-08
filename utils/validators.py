import re

def required(prompt, field):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print(f"{field} cannot be empty.")

def valid_email(prompt):
    while True:
        value = input(prompt).strip()
        if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
            return value
        print("Enter a valid email.")

def valid_salary(prompt):
    while True:
        try:
            value = float(input(prompt).strip())
            if value >= 0:
                return value
        except ValueError:
            pass
        print("Enter a valid non-negative salary.")

def optional(prompt):
    return input(prompt).strip() or None
