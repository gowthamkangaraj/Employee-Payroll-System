from config.database import get_connection
from utils.helpers import input_date

def attendance_menu():
    while True:
        print("\n--- Attendance Management ---")
        print("1. Mark Attendance")
        print("2. View Employee Attendance")
        print("3. Monthly Summary")
        print("0. Back")
        c = input("Choice: ").strip()
        if c == "1": mark()
        elif c == "2": view()
        elif c == "3": summary()
        elif c == "0": break
        else: print("Invalid choice.")

def mark():
    code = input("Employee code: ").strip()
    date = input_date("Date (YYYY-MM-DD): ")
    status = {"1":"Present","2":"Absent","3":"Half Day","4":"Leave"}.get(
        input("1 Present  2 Absent  3 Half Day  4 Leave: ").strip()
    )
    if not status:
        print("Invalid status.")
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT employee_id FROM employees WHERE employee_code=%s", (code,))
    row = cur.fetchone()
    if not row:
        print("Employee not found.")
        cur.close(); conn.close()
        return

    try:
        cur.execute(
            '''INSERT INTO attendance(employee_id,attendance_date,status)
               VALUES(%s,%s,%s)
               ON DUPLICATE KEY UPDATE status=VALUES(status)''',
            (row[0], date, status),
        )
        conn.commit()
        print("Attendance saved.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    cur.close()
    conn.close()

def view():
    code = input("Employee code: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''SELECT a.attendance_date,a.status
           FROM attendance a
           JOIN employees e ON e.employee_id=a.employee_id
           WHERE e.employee_code=%s
           ORDER BY a.attendance_date DESC''',
        (code,),
    )
    rows = cur.fetchall()
    for row in rows:
        print(row[0], row[1])
    if not rows:
        print("No attendance records.")
    cur.close()
    conn.close()

def summary():
    code = input("Employee code: ").strip()
    month = input("Month YYYY-MM: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''SELECT a.status,COUNT(*)
           FROM attendance a JOIN employees e ON e.employee_id=a.employee_id
           WHERE e.employee_code=%s AND DATE_FORMAT(a.attendance_date,'%%Y-%%m')=%s
           GROUP BY a.status''',
        (code, month),
    )
    print(f"\nAttendance summary for {month}")
    for row in cur.fetchall():
        print(f"{row[0]:10} : {row[1]}")
    cur.close()
    conn.close()
