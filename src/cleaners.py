from datetime import datetime
def clean_date(date_str):
    date_str = date_str.strip()
    if date_str == "":
        return None, f"invalid date: {date_str}"
    try:
        cleaned_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None, f"invalid date: {date_str}"
    if cleaned_date.year < 2020:
        return None, "Date year is too old. Check the year"
    if cleaned_date.year > 2030:
        return None, "Date year is too far in the future. Check the year"
    return cleaned_date.isoformat(), None
def clean_row(row):
    errors = []
    cleaned_date, error = clean_date(row["date"])
    if error:
        errors.append(error)
    row["date"] = cleaned_date
    load_type = row["load_type"].strip().lower()
    if load_type == "":
        errors.append("load_type is empty")
    valid_types = {"rebar", "scrap", "container"}
    if load_type not in valid_types:
        errors.append(f"invalid load_type: {load_type}")
    row["load_type"] = load_type
    if row["load_sequence"] == "":
        errors.append("load sequence is empty")
    if row['rate'] == "":
        errors.append("rate is empty")
    for field in ["miles", "rate"]:
        if row[field] == "":
            errors.append(f"empty field: {field}")
    try:                             
        miles = float(row["miles"]) 
        rate = float(row["rate"]) 
        load_sequence = int(row["load_sequence"])
    except ValueError: 
        errors.append("Field is not numeric")  
    if miles <= 0: 
        errors.append("Miles must be greater then 0") 
    row["miles"] = miles
    row["rate"] = rate
    row["load_sequence"] = load_sequence
    return row, errors
def clean_load(row):
    errors = []
    cleaned_date, error = clean_date(row["date"])
    if error:
        errors.append(error)
    row["date"] = cleaned_date
    load_type = row["load_type"].strip().lower()
    if load_type == "":
        errors.append("load_type is empty")
    valid_types = {"rebar", "scrap", "container"}
    if load_type not in valid_types:
        errors.append(f"invalid load_type: {load_type}")
    row["load_type"] = load_type
    if row['rate'] == "":
        errors.append("rate is empty")
    for field in ["miles", "rate"]:
        if row[field] == "":
            errors.append(f"empty field: {field}")
    try:                             
        miles = float(row["miles"]) 
        rate = float(row["rate"]) 
    except ValueError: 
        errors.append("Field is not numeric")  
    if miles <= 0: 
        errors.append("Miles must be greater then 0") 
    row["miles"] = miles
    row["rate"] = rate
    return row, errors
def clean_row_fuel(row):
    errors = []
    cleaned_date, error = clean_date(row["purchase_date"])
    if error:
        errors.append(error)
    row["purchase_date"] = cleaned_date
    if None in row:
        errors.append("Row has extra columns")
    total_cost = row.get("total_cost")
    if total_cost == None:
        errors.append("Total cost is empty")  
    total_cost = str(total_cost).strip()
    if total_cost == "":
        errors.append("Total cost is empty")
    gallons = row.get("gallons")
    if gallons == None:
        errors.append("Gallons are empty")
    gallons = str(gallons).strip()    
    if gallons == "":
        errors.append("Gallons is empty")
    
    odometer = row.get("odometer")
    if odometer == None:
        errors.append("Odometer cannot be None")
    odometer = str(odometer).strip()
    if odometer == "":
        errors.append("Odometer is empty")
    try:
        total_cost = float(total_cost) 
    except ValueError:
        errors.append(f"Total cost is not numeric: {total_cost}")
    try:
        gallons = float(gallons) 
    except ValueError:
        errors.append(f"Gallons is not numeric: {gallons}")
    try:
        odometer = float(odometer)
    except ValueError:
        errors.append(f"Odometer is not numeric: {odometer}")
    if not odometer.is_integer():
        errors.append(f"Odometer must be a whole number: {odometer}")
    odometer = int(odometer)
    if gallons <= 0:
        errors.append("Gallons must be greater than 0") 
    if total_cost <= 0:
        errors.append("Total cost must be more than 0")
    row["gallons"] = gallons
    row["total_cost"] = total_cost
    row["odometer"] = odometer
    return row, errors
def clean_expense(expense_name, monthly_cost):
    errors = []
    if not expense_name or not expense_name.strip().lower:
        errors.append("Expense name is required.")
    else:
        expense_name = expense_name.strip().lower()
    try:
        monthly_cost = float(monthly_cost)
    except (TypeError, ValueError):
        errors.append("Monthly cost must be a number.")
        monthly_cost = None
    if monthly_cost is not None and monthly_cost <= 0:
        errors.append("Monthly cost must be greater than 0.")
    return expense_name, monthly_cost, errors