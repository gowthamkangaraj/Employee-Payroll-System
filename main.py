from config.database import get_connection
from services.employee_service import employee_menu
from services.department_service import department_menu
from services.attendance_service import attendance_menu
from services.leave_service import leave_menu
from services.payroll_service import payroll_menu
from reports.reports import reports_menu
from utils.helpers import hash_password, print_title

def setup_admin():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM admins")
    if cur.fetchone()[0] == 0:
        print("\nFirst run: create administrator account.")
        username = input("Admin username: ").strip()
        password = input("Admin password: ")
        if username and password:
            cur.execute(
                "INSERT INTO admins(username,password_hash) VALUES(%s,%s)",
                (username, hash_password(password)),
            )
            conn.commit()
            print("Admin account created.")
    cur.close()
    conn.close()

def login():
    print_title("ADMIN LOGIN")
    username = input("Username: ").strip()
    password = input("Password: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM admins WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row and row[0] == hash_password(password):
        print("Login successful.")
        return True
    print("Invalid username or password.")
    return False

def main():
    try:
        setup_admin()
        if not login():
            return
        while True:

            print("\n" + "=" * 60)
            print("        EMPLOYEE MANAGEMENT & PAYROLL SYSTEM")
            print("=" * 60)
            print("\n" + "-" * 60)
            print("                    MAIN MENU")
            print("-" * 60)
            print("1. Employee Management")
            print("2. Department Management")
            print("3. Attendance Management")
            print("4. Leave Management")
            print("5. Payroll Management")
            print("6. Reports & Analysis")
            print("0. Logout")
            print("-" * 60)
            choice = input("Enter choice: ").strip()

            if choice == "1": employee_menu()
            elif choice == "2": department_menu()
            elif choice == "3": attendance_menu()
            elif choice == "4": leave_menu()
            elif choice == "5": payroll_menu()
            elif choice == "6": reports_menu()
            elif choice == "0":
                print("Logged out.")
                break
            else:
                print("Invalid choice.")
    except Exception as e:
        print("\nCould not start application.")
        print("Check MySQL, .env settings, and schema.sql.")
        print("Details:", e)

if __name__ == "__main__":
    main()
