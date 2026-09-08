from config.database import get_connection
from utils.validators import required, valid_email, valid_salary, optional
from utils.helpers import input_date, money

def employee_menu():
    while True:
        print("\n" + "-" * 60)
        print("                  EMPLOYEE MANAGEMENT")
        print("-" * 60)
        print("1. Add Employee")
        print("2. View Employee")
        print("3. View All Employees")
        print("4. Update Employee")
        print("5. Delete Employee")
        print("6. Search Employee")
        print("0. Back")
        print("-" * 60)
        c = input("Choice: ").strip()
        if c == "1": add_employee()
        elif c == "2": view_employee()
        elif c == "3": view_all()
        elif c == "4": update_employee()
        elif c == "5": delete_employee()
        elif c == "6": search_employee()
        elif c == "0": break
        else: print("Invalid choice.")

def add_employee():
    code = required("Employee code: ", "Employee code")
    first = required("First name: ", "First name")
    last = optional("Last name: ")
    email = valid_email("Email: ")
    phone = optional("Phone: ")
    gender = optional("Gender: ")
    dob = input_date("Date of birth (YYYY-MM-DD, optional): ", False)
    address = optional("Address: ")
    dept = optional("Department ID (optional): ")
    designation = required("Designation: ", "Designation")
    joining = input_date("Joining date (YYYY-MM-DD): ")
    salary = valid_salary("Basic salary: ")

    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO employees
            (employee_code, first_name, last_name, email, phone, gender, date_of_birth,
             address, department_id, designation, joining_date, basic_salary)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (code, first, last, email, phone, gender, dob, address,
             int(dept) if dept else None, designation, joining, salary),
        )
        conn.commit()
        print("Employee added successfully.")
    except Exception as e:
        if conn: conn.rollback()
        print("Error:", e)
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_employee(key):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        '''SELECT e.*, d.department_name FROM employees e
           LEFT JOIN departments d ON e.department_id=d.department_id
           WHERE e.employee_id=%s OR e.employee_code=%s''',
        (key, key),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def show_employee(row):
    if not row:
        print("Employee not found.")
        return
    for key, value in row.items():
        if key == "basic_salary":
            value = money(value)
        print(f"{key.replace('_',' ').title():20}: {value}")

def view_employee():
    show_employee(get_employee(input("Employee ID/code: ").strip()))

def view_all():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''SELECT e.employee_code, CONCAT(e.first_name,' ',COALESCE(e.last_name,'')),
                  d.department_name, e.designation, e.basic_salary, e.status
           FROM employees e LEFT JOIN departments d ON e.department_id=d.department_id
           ORDER BY e.employee_id'''
    )
    rows = cur.fetchall()
    print("\nCode | Name | Department | Designation | Salary | Status")
    print("-" * 100)
    for r in rows:
        print(f"{r[0]} | {r[1].strip()} | {r[2] or '-'} | {r[3]} | {money(r[4])} | {r[5]}")
    if not rows:
        print("No employees.")
    cur.close()
    conn.close()

def update_employee():
    code = input("Employee code: ").strip()
    row = get_employee(code)
    if not row:
        print("Employee not found.")
        return

    first = input(f"First name [{row['first_name']}]: ").strip() or row["first_name"]
    last = input(f"Last name [{row['last_name'] or ''}]: ").strip() or row["last_name"]
    email = input(f"Email [{row['email']}]: ").strip() or row["email"]
    phone = input(f"Phone [{row['phone'] or ''}]: ").strip() or row["phone"]
    address=input(f"Address[{row['address']or''}]:").strip() or row["address"]
    designation = input(f"Designation [{row['designation']}]: ").strip() or row["designation"]
    status = input(f"Status Active/Inactive [{row['status']}]: ").strip() or row["status"]

    try:
        text = input(f"Basic salary [{row['basic_salary']}]: ").strip()
        salary = float(text) if text else float(row["basic_salary"])
        if salary < 0:
            raise ValueError("Salary cannot be negative.")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            '''UPDATE employees SET first_name=%s,last_name=%s,email=%s,phone=%s,
               address=%s,designation=%s,status=%s,basic_salary=%s WHERE employee_code=%s''',
            (first, last, email, phone, address, designation, status, salary, code),
        )
        conn.commit()
        print("Employee updated.")
    except Exception as e:
        if "conn" in locals(): conn.rollback()
        print("Error:", e)
    finally:
        if "cur" in locals(): cur.close()
        if "conn" in locals(): conn.close()

def delete_employee():
    code = input("Employee code: ").strip()
    if input("Type DELETE to confirm: ") != "DELETE":
        print("Cancelled.")
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM employees WHERE employee_code=%s", (code,))
    conn.commit()
    print("Deleted." if cur.rowcount else "Employee not found.")
    cur.close()
    conn.close()

def search_employee():
    term = input("Search name/email/code/designation: ").strip()
    like = f"%{term}%"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''SELECT e.employee_code, CONCAT(e.first_name,' ',COALESCE(e.last_name,'')),
                  d.department_name,e.designation,e.email,e.status
           FROM employees e LEFT JOIN departments d ON e.department_id=d.department_id
           WHERE e.employee_code LIKE %s OR e.first_name LIKE %s OR e.last_name LIKE %s
              OR e.email LIKE %s OR e.designation LIKE %s''',
        (like, like, like, like, like),
    )
    rows = cur.fetchall()
    for row in rows:
        print(row)
    if not rows:
        print("No employees found.")
    cur.close()
    conn.close()
