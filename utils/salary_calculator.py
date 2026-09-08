def calculate_salary(basic, hra_rate=0.40, allowances=0, bonus=0,
                     pf_rate=0.12, tax=0, other_deductions=0,
                     leave_days=0, working_days=26):
    basic = float(basic)
    hra = basic * hra_rate
    gross = basic + hra + float(allowances) + float(bonus)
    pf = basic * pf_rate
    per_day = gross / working_days if working_days else 0
    leave_deduction = per_day * max(0, int(leave_days))
    total_deductions = pf + float(tax) + float(other_deductions) + leave_deduction
    return {
        "basic": basic,
        "hra": hra,
        "allowances": float(allowances),
        "bonus": float(bonus),
        "gross": gross,
        "pf": pf,
        "tax": float(tax),
        "other_deductions": float(other_deductions),
        "leave_deduction": leave_deduction,
        "total_deductions": total_deductions,
        "net": max(0, gross - total_deductions),
    }
