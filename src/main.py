import csv
import sqlite3
conn = sqlite3.connect("data/trucking.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS loads(
        id INTEGER PRIMARY KEY,
        miles INTEGER,
        rate REAL,
        fuel REAL
);
""") 
def load_csv(file_path):
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    return rows
def clean_row(row):
    if row['miles'] <= '0': 
        return None, "Miles is zero"
    for field in ["miles", "rate", "fuel"]:
        if row[field] == "":
            return None, f"empty field: {field}"
    try:                             
        miles = float(row["miles"]) 
        rate = float(row["rate"]) 
        fuel = float(row["fuel"]) 
    except ValueError: 
        return None, "Field is not numeric"   
    return row, None
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
def main():
    input_file = "data/sample_loads.csv"
    inserted = 0
    skipped = 0
    rows = load_csv(input_file)
    cursor.execute("DELETE FROM loads")
    conn.commit
    for row in rows:  
        cleaned_row, error = clean_row(row)
        if error:
            skipped += 1
            print(f"Skipped row with date {row['date']} skipped: {error}")
            continue
        values = (
            cleaned_row["miles"],
            cleaned_row["rate"],
            cleaned_row["fuel"]
        )
        cursor.execute("""
        INSERT INTO loads (
            miles,
            rate,
            fuel
        )  
        VALUES (?, ?, ?)
        """, values)
        inserted += 1   
    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")
    conn.commit()
        
main()
#current status- works great but we have issues with duplicates 
#tomorows objective - change the table to include all our actual fields and start adding calculated metrics

