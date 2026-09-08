from config.database import get_connection
from utils.salary_calculator import calculate_salary
from utils.helpers import money

def payroll_menu():
    while True:
        print("\n--- Payroll Management ---")
        print("1. Generate Payroll")
        print("2. View Monthly Payroll")
        print("3. Employee Salary History")
        print("4. View Payroll Record")
        print("0. Back")
        c = input("Choice: ").strip()
        if c == "1": generate()
        elif c == "2": monthly()
        elif c == "3": history()
        elif c == "4": record()
        elif c == "0": break
        else: print("Invalid choice.")

def get_emp(code):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM employees WHERE employee_code=%s AND status='Active'", (code,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row

def generate():
    code = input("Employee code: ").strip()
    emp = get_emp(code)
    if not emp:
        print("Active employee not found.")
        return

    month = input("Payroll month YYYY-MM-01: ").strip()
    try:
        bonus = float(input("Bonus [0]: ") or 0)
        allowances = float(input("Allowances [0]: ") or 0)
        tax = float(input("Tax [0]: ") or 0)
        other = float(input("Other deductions [0]: ") or 0)
        leave_days = int(input("Unpaid leave days [0]: ") or 0)

        salary = calculate_salary(
            emp["basic_salary"],
            allowances=allowances,
            bonus=bonus,
            tax=tax,
            other_deductions=other,
            leave_days=leave_days,
        )

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO payroll
            (employee_id,payroll_month,basic_salary,hra,allowances,bonus,gross_salary,
             pf,tax,other_deductions,leave_deduction,total_deductions,net_salary)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
            basic_salary=VALUES(basic_salary),hra=VALUES(hra),allowances=VALUES(allowances),
            bonus=VALUES(bonus),gross_salary=VALUES(gross_salary),pf=VALUES(pf),
            tax=VALUES(tax),other_deductions=VALUES(other_deductions),
            leave_deduction=VALUES(leave_deduction),
            total_deductions=VALUES(total_deductions),net_salary=VALUES(net_salary)''',
            (emp["employee_id"], month, salary["basic"], salary["hra"],
             salary["allowances"], salary["bonus"], salary["gross"], salary["pf"],
             salary["tax"], salary["other_deductions"], salary["leave_deduction"],
             salary["total_deductions"], salary["net"]),
        )
        conn.commit()
        print(f"Payroll generated. Net salary: {money(salary['net'])}")
    except Exception as e:
        if "conn" in locals(): conn.rollback()
        print("Error:", e)
    finally:
        if "cur" in locals(): cur.close()
        if "conn" in locals(): conn.close()

def monthly():
    month = input("Month YYYY-MM: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''SELECT e.employee_code,
                  CONCAT(e.first_name,' ',COALESCE(e.last_name,'')),
                  p.gross_salary,p.total_deductions,p.net_salary
           FROM payroll p JOIN employees e ON e.employee_id=p.employee_id
           WHERE DATE_FORMAT(p.payroll_month,'%Y-%m')=%s
           ORDER BY e.employee_code''',
        (month,),
    )
    rows = cur.fetchall()
    print("\nCode | Name | Gross | Deductions | Net")
    print("-" * 75)
    for row in rows:
        print(f"{row[0]} | {row[1].strip()} | {money(row[2])} | {money(row[3])} | {money(row[4])}")
    if not rows:
        print("No payroll records.")
    cur.close(); conn.close()

def history():
    code = input("Employee code: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''SELECT p.payroll_month,p.gross_salary,p.total_deductions,p.net_salary
           FROM payroll p JOIN employees e ON e.employee_id=p.employee_id
           WHERE e.employee_code=%s ORDER BY p.payroll_month''',
        (code,),
    )
    rows = cur.fetchall()
    for row in rows:
        print(row[0], money(row[1]), money(row[2]), money(row[3]))
    if not rows:
        print("No salary history.")
    cur.close(); conn.close()

def record():
    try:
        pid = int(input("Payroll ID: "))
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            '''SELECT p.*,e.employee_code,
                      CONCAT(e.first_name,' ',COALESCE(e.last_name,'')) AS employee_name
               FROM payroll p JOIN employees e ON e.employee_id=p.employee_id
               WHERE p.payroll_id=%s''',
            (pid,),
        )
        row = cur.fetchone()
        if not row:
            print("Record not found.")
            return
        for key, value in row.items():
            print(f"{key.replace('_',' ').title():22}: {value}")
    except Exception as e:
        print("Error:", e)
    finally:
        if "cur" in locals(): cur.close()
        if "conn" in locals(): conn.close()
