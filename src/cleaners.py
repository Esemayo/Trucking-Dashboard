from datetime import datetime
def clean_date(date_str):
    date_str = date_str.strip()
    if date_str == "":
        return None, f"invalid date: {date_str}"
    try:
        cleaned_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        return cleaned_date, None
    except ValueError:
        return None, f"invalid date: {date_str}"
def clean_row(row):
    cleaned_date, error = clean_date(row["date"])
    if error:
        return None, error
    row["date"] = cleaned_date
    load_type = row["load_type"].strip().lower()
    if load_type == "":
        return None, "load_type is empty"
    valid_types = {"rebar", "scrap", "container"}
    if load_type not in valid_types:
        return None, f"invalid load_type: {load_type}"
    row["load_type"] = load_type
    if row["load_sequence"] == "":
        return None, "load sequence is empty"
    if row['rate'] == "":
        return None, "rate is empty"
    for field in ["miles", "rate"]:
        if row[field] == "":
            return None, f"empty field: {field}"
    try:                             
        miles = float(row["miles"]) 
        rate = float(row["rate"]) 
        load_sequence = int(row["load_sequence"])
    except ValueError: 
        return None, "Field is not numeric"  
    if miles <= 0: 
        return None, "Miles must be greater then 0" 
    row["miles"] = miles
    row["rate"] = rate
    row["load_sequence"] = load_sequence
    return row, None
def clean_row_fuel(row):
    cleaned_date, error = clean_date(row["purchase_date"])
    if error:
        return None, error
    row["purchase_date"] = cleaned_date
    if None in row:
        return None, "Row has extra columns"
    total_cost = row.get("total_cost")
    if total_cost == None:
        return None, "Total cost is empty"  
    total_cost = str(total_cost).strip()
    if total_cost == "":
        return None, "Total cost is empty"
    gallons = row.get("gallons")
    if gallons == None:
        return None, "Gallons are empty"
    gallons = str(gallons).strip()    
    if gallons == "":
        return None, "Gallons is empty"
    
    odometer = row.get("odometer")
    if odometer == None:
        return None, "Odometer cannot be None"
    odometer = str(odometer).strip()
    if odometer == "":
        return None, "Odometer is empty"
    try:
        total_cost = float(total_cost) 
    except ValueError:
        return None, f"Total cost is not numeric: {total_cost}"
    try:
        gallons = float(gallons) 
    except ValueError:
        return None, f"Gallons is not numeric: {gallons}"
    try:
        odometer = float(odometer)
    except ValueError:
        return None, f"Odometer is not numeric: {odometer}"
    if not odometer.is_integer():
        return None, f"Odometer must be a whole number: {odometer}"
    odometer = int(odometer)
    if gallons <= 0:
        return None, "Gallons must be greater than 0" 
    if total_cost <= 0:
        return None, "Total cost must be more than 0"
    row["gallons"] = gallons
    row["total_cost"] = total_cost
    row["odometer"] = odometer
    return row, None