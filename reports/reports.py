from config.database import get_connection
import warnings

warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy connectable"
)

def reports_menu():
    while True:
        print("\n--- Reports & Analysis ---")
        print("1. Employee Statistics")
        print("2. Department Salary Analysis")
        print("3. Payroll Summary")
        print("4. Export Payroll to CSV")
        print("0. Back")
        c = input("Choice: ").strip()
        if c == "1": employee_stats()
        elif c == "2": department_salary()
        elif c == "3": payroll_summary()
        elif c == "4": export_csv()
        elif c == "0": break
        else: print("Invalid choice.")

def employee_stats():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*),SUM(status='Active'),SUM(status='Inactive') FROM employees")
    print("Total / Active / Inactive:", cur.fetchone())
    cur.execute(
        '''SELECT COALESCE(d.department_name,'Unassigned'),COUNT(*)
           FROM employees e LEFT JOIN departments d ON e.department_id=d.department_id
           GROUP BY d.department_id,d.department_name ORDER BY COUNT(*) DESC'''
    )
    print("\nEmployees by department:")
    for row in cur.fetchall(): print(row)
    cur.close(); conn.close()

def department_salary():
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        '''SELECT COALESCE(d.department_name,'Unassigned'),COUNT(e.employee_id),
                  ROUND(AVG(e.basic_salary),2),ROUND(MAX(e.basic_salary),2),
                  ROUND(MIN(e.basic_salary),2)
           FROM employees e LEFT JOIN departments d ON e.department_id=d.department_id
           GROUP BY d.department_id,d.department_name'''
    )
    print("Department | Count | Avg | Max | Min")
    for row in cur.fetchall(): print(row)
    cur.close(); conn.close()

def payroll_summary():
    month = input("Month YYYY-MM: ").strip()
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        '''SELECT COUNT(*),COALESCE(SUM(gross_salary),0),
                  COALESCE(SUM(total_deductions),0),COALESCE(SUM(net_salary),0),
                  COALESCE(AVG(net_salary),0)
           FROM payroll
           WHERE DATE_FORMAT(payroll_month,'%Y-%m')=%s''',
        (month,),
    )
    print("Records, Gross Total, Deductions, Net Total, Average Net")
    print(cur.fetchone())
    cur.close(); conn.close()

def export_csv():
    try:
        import pandas as pd
        month = input("Month YYYY-MM (blank = all): ").strip()
        conn = get_connection()
        query = '''SELECT e.employee_code,
                          CONCAT(e.first_name,' ',COALESCE(e.last_name,'')) AS employee_name,
                          d.department_name,p.payroll_month,p.basic_salary,p.hra,p.allowances,
                          p.bonus,p.gross_salary,p.pf,p.tax,p.other_deductions,p.leave_deduction,
                          p.total_deductions,p.net_salary
                   FROM payroll p JOIN employees e ON e.employee_id=p.employee_id
                   LEFT JOIN departments d ON d.department_id=e.department_id'''
        params = ()
        if month:
            query += " WHERE DATE_FORMAT(p.payroll_month,'%Y-%m')=%s"
            params = (month,)
        df = pd.read_sql(query, conn, params=params)
        filename = f"payroll_{month or 'all'}.csv"
        df.to_csv(filename, index=False)
        print(f"Exported {len(df)} rows to {filename}")
        conn.close()
    except Exception as e:
        print("Error:", e)
