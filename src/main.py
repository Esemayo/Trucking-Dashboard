import csv
def load_csv(file_path):
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    return rows
def clean_row(row):
    if row['miles'] == '0': 
        return None
    if row['miles'] == '' or row['rate'] == '' or row['fuel'] == '':
        return None
    try:                             
        miles = float(row["miles"]) 
        rate = float(row["rate"]) 
        fuel = float(row["fuel"]) 
    except ValueError: 
        return None     
    return row
def calculate_metrics(row):
    miles = float(row["miles"]) 
    rate = float(row["rate"]) 
    fuel = float(row["fuel"]) 
    rate_per_mile = rate/miles 
    fuel_cost_per_mile = fuel/miles 
    net_after_fuel = rate-fuel
    row["rate_per_mile"] = rate_per_mile
    row["fuel_cost_per_mile"] = fuel_cost_per_mile  
    row["net_after_fuel"] = net_after_fuel
    return row 
def write_csv(file_path, rows):
    fieldnames = rows[0].keys()
    with open(file_path, mode='w') as file: 
        writer = csv.DictWriter(file, fieldnames) 
        writer.writeheader() 
        writer.writerows(rows)
    pass
def main():
    input_file = "data/sample_loads_messy.csv"
    output_file = "data/processed_loads.csv"
    processed_rows =[]
    rows = load_csv(input_file)
    for row in rows:
        cleaned = clean_row(row)
        if not cleaned:
            continue
        processed = calculate_metrics(cleaned)
        processed_rows.append(processed)
    write_csv(output_file, processed_rows)
main()
