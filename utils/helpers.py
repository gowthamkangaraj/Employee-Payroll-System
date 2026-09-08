from datetime import datetime
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def input_date(prompt, required=True):
    while True:
        value = input(prompt).strip()
        if not value and not required:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.")

def money(value):
    return f"₹{float(value):,.2f}"

def print_title(title):
    print("\n" + "=" * 72)
    print(title.center(72))
    print("=" * 72)
