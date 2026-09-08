from config.database import get_connection
from utils.helpers import input_date

def leave_menu():
    while True:
        print("\n--- Leave Management ---")
        print("1. Apply Leave")
        print("2. View Leaves")
        print("3. Approve/Reject Leave")
        print("0. Back")
        c = input("Choice: ").strip()
        if c == "1": apply_leave()
        elif c == "2": view_leaves()
        elif c == "3": change_status()
        elif c == "0": break
        else: print("Invalid choice.")

def employee_id(code):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT employee_id FROM employees WHERE employee_code=%s", (code,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row[0] if row else None

def apply_leave():
    eid = employee_id(input("Employee code: ").strip())
    if not eid:
        print("Employee not found.")
        return
    typ = {"1":"Casual","2":"Sick","3":"Earned","4":"Unpaid"}.get(
        input("1 Casual  2 Sick  3 Earned  4 Unpaid: ").strip()
    )
    if not typ:
        print("Invalid leave type.")
        return
    start = input_date("Start date: ")
    end = input_date("End date: ")
    if end < start:
        print("End date cannot be before start date.")
        return
    reason = input("Reason: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO leaves(employee_id,leave_type,start_date,end_date,reason)
           VALUES(%s,%s,%s,%s,%s)''',
        (eid, typ, start, end, reason),
    )
    conn.commit()
    print("Leave applied.")
    cur.close(); conn.close()

def view_leaves():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''SELECT l.leave_id,e.employee_code,
                  CONCAT(e.first_name,' ',COALESCE(e.last_name,'')),
                  l.leave_type,l.start_date,l.end_date,l.reason,l.status
           FROM leaves l JOIN employees e ON e.employee_id=l.employee_id
           ORDER BY l.created_at DESC'''
    )
    rows = cur.fetchall()
    for row in rows:
        print(row)
    if not rows:
        print("No leave records.")
    cur.close(); conn.close()

def change_status():
    try:
        lid = int(input("Leave ID: "))
        status = input("Status (Approved/Rejected): ").strip().title()
        if status not in ("Approved", "Rejected"):
            print("Invalid status.")
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE leaves SET status=%s WHERE leave_id=%s", (status, lid))
        conn.commit()
        print("Updated." if cur.rowcount else "Leave not found.")
    except Exception as e:
        print("Error:", e)
    finally:
        if "cur" in locals(): cur.close()
        if "conn" in locals(): conn.close()
