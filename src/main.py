import csv
from datetime import datetime
import sqlite3
conn = sqlite3.connect("data/trucking.db")
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS loads")###reset table
cursor.execute("""
CREATE TABLE IF NOT EXISTS loads(
        id INTEGER PRIMARY KEY,
        date TEXT,
        load_type TEXT,
        load_sequence INTEGER, 
        miles INTEGER,
        rate REAL,
        UNIQUE(date, load_sequence)
);
""") 
def load_csv(file_path):
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    return rows
def clean_row(row):
    date_str = row["date"].strip()
    if date_str == "":
        return None, f"invalid date: {date_str}"
    try:
        cleaned_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return None, f"invalid date: {date_str}"
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
    if row['miles'] <= '0': 
        return None, "Miles is zero"
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
    return row, None
def calculate_metrics(row):
    miles = float(row["miles"]) 
    rate = float(row["rate"])  
    rate_per_mile = rate/miles 
    row["rate_per_mile"] = rate_per_mile
    return row 
def main():
    input_file = "data/sample_loads.csv"
    inserted = 0
    skipped = 0
    rows = load_csv(input_file)
    for row in rows:  
        cleaned_row, error = clean_row(row)
        if error:
            skipped += 1
            print(f"Skipped row with date {row['date']} skipped: {error}")
            continue
        values = (
            cleaned_row["date"],
            cleaned_row["load_type"],
            cleaned_row["load_sequence"],
            cleaned_row["miles"],
            cleaned_row["rate"]
        )
        try:
            cursor.execute("""
            INSERT INTO loads (
                date,
                load_type,
                load_sequence,
                miles,
                rate
            )  
            VALUES (?, ?, ?, ?, ?)
            """, values)
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1
            print(f"Skipped duplicate: date = {cleaned_row["date"]}  load_sequence = {cleaned_row['load_sequence']}")
            continue    
    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")
    conn.commit()
        
main()
#current status: CSV -> validation -> SQlite insert not working need to add load_sequence 
#known issue: duplicate rows on reruns (no uniqueness constriants yet)
#tommorows objective validate load sequence update sql inserts to match new columns
#next step: redesign schema with real fields + metrics


