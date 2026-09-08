from config.database import get_connection

def list_departments():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM departments ORDER BY department_name")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def department_menu():
    while True:
        print("\n--- Department Management ---")
        print("\n" + "-" * 60)
        print("                 DEPARTMENT MANAGEMENT")
        print("-" * 60)
        print("1. Add Department")
        print("2. View Departments")
        print("3. Update Department")
        print("4. Delete Department")
        print("0. Back")
        print("-" * 60)
        choice = input("Choice: ").strip()

        if choice == "1":
            name = input("Department name: ").strip()
            desc = input("Description: ").strip()
            if not name:
                print("Name required.")
                continue
            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO departments (department_name, description) VALUES (%s,%s)",
                    (name, desc),
                )
                conn.commit()
                print("Department added.")
            except Exception as e:
                conn.rollback()
                print("Error:", e)
            finally:
                cur.close()
                conn.close()

        elif choice == "2":
            print("\nID | Department | Description")
            print("-" * 60)
            for r in list_departments():
                print(f"{r['department_id']} | {r['department_name']} | {r['description'] or ''}")

        elif choice == "3":
            try:
                did = int(input("Department ID: "))
                name = input("New name: ").strip()
                desc = input("New description: ").strip()
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE departments SET department_name=%s, description=%s WHERE department_id=%s",
                    (name, desc, did),
                )
                conn.commit()
                print("Updated." if cur.rowcount else "Department not found.")
            except Exception as e:
                print("Error:", e)
            finally:
                if "cur" in locals(): cur.close()
                if "conn" in locals(): conn.close()

        elif choice == "4":
            try:
                did = int(input("Department ID: "))
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM departments WHERE department_id=%s", (did,))
                conn.commit()
                print("Deleted." if cur.rowcount else "Department not found.")
            except Exception as e:
                print("Error:", e)
            finally:
                if "cur" in locals(): cur.close()
                if "conn" in locals(): conn.close()

        elif choice == "0":
            break
        else:
            print("Invalid choice.")
