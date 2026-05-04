import sqlite3
from datetime import datetime
from src.cleaners import clean_row, clean_row_fuel
from src.db import db_connection, create_tables, insert_load, insert_fuel
from src.loaders import load_csv
from src.metrics import load_metrics, calculate_cost_per_gallon
from src.query import recent_fuel_mpg
def process_fuel_file(conn, fuel_file):
    inserted = 0
    duplicates = 0
    validation_errors = 0
    fuel_error_details = []
    print("_" * 90)
    print("Fuel Summary")
    print("_" * 90)
    rows = load_csv(fuel_file)
    last_odometer = None
    for row in rows:    
        cleaned_row_fuel, error = clean_row_fuel(row)
        if error:
            validation_errors += 1
            print(f"Skipped row with date {row['purchase_date']} skipped: {error}")
            fuel_error_details.append({
                "date": row["purchase_date"],
                "reason": error
            })
            continue
        odometer = cleaned_row_fuel["odometer"]
        if last_odometer is not None: 
            odometer_jump = odometer - last_odometer
            if odometer_jump <= 0:    
                validation_errors += 1
                print(f"Skipped row with backwards odometer, purchase date: {row["purchase_date"]}")
                fuel_error_details.append({
                    "date": row["purchase_date"],
                    "reason": "Backwards Odometer"
                })
                continue
            if odometer_jump > 2000:
                validation_errors += 1
                print("Skipped odometer with unrealistic odometer jump")
                fuel_error_details.append({
                    "date": row["purchase_date"],
                    "reason": "Unrealistic Odometer Jump"
                })
                continue
        cleaned_row_fuel = calculate_cost_per_gallon(cleaned_row_fuel)
        last_odometer = cleaned_row_fuel["odometer"]
        try:
            insert_fuel(conn, cleaned_row_fuel)
            inserted += 1
        except sqlite3.IntegrityError:
            duplicates += 1
            print(f"Skipped duplicate: date = {cleaned_row_fuel["purchase_date"]} odometer = {cleaned_row_fuel["odometer"]}")
            continue 
    conn.commit()
    print(f"Inserted: {inserted}")
    print(f"Validation_errors: {validation_errors}")
    print(f"Duplicates: {duplicates}")
    return {
        "inserted": inserted,
        "validation_errors": validation_errors,
        "duplicates": duplicates,
        "error_details": fuel_error_details
    }
def process_loads_file(conn, loads_file):
    inserted = 0
    duplicates = 0
    validation_errors = 0
    load_error_details = []
    print("_" * 90)
    print("Load Summary")
    print("_" * 90)
    rows = load_csv(loads_file)
    fuel_result = recent_fuel_mpg(conn)
    for row in rows:  
        cleaned_row, error = clean_row(row)
        if error:
            validation_errors += 1
            print(f"Skipped row with date {row['date']} skipped: {error}")
            load_error_details.append({
                "date": row["date"],
                "reason": error
            })
            continue
        if fuel_result is None:
            fuel_cost_per_mile = 2.00
            print("WARNING: using placeholder fuel cost per mile = 2.00")
        else:
            fuel_cost_per_mile, fuel_date = fuel_result
            load_date = cleaned_row["date"]
            fuel_dt = datetime.strptime(fuel_date, "%Y-%m-%d").date()
            load_dt = datetime.strptime(load_date, "%Y-%m-%d").date()
            days_gap = (load_dt - fuel_dt).days
            if days_gap > 7:
                fuel_cost_per_mile = 2.00
                print("WARNING: using placeholder fuel cost per mile = 2.00")
        cleaned_row = load_metrics(cleaned_row, fuel_cost_per_mile)
        try:
            insert_load(conn, cleaned_row)
            inserted += 1
        except sqlite3.IntegrityError:
            duplicates += 1
            print(f"Skipped duplicate: date = {cleaned_row["date"]}  load_sequence = {cleaned_row['load_sequence']}")
            continue  
    conn.commit()
    print(f"Inserted: {inserted}")
    print(f"Validation Errors: {validation_errors}")
    print(f"Duplicates: {duplicates}")
    return {
        "inserted": inserted,
        "validation_errors": validation_errors,
        "duplicates": duplicates,
        "error_details": load_error_details
    }
def run_pipeline(loads_file=None, fuel_file=None):
    conn =db_connection()
    create_tables(conn)
    fuel_summary = None
    load_summary = None
    if fuel_file:
        fuel_summary = process_fuel_file(conn, fuel_file)
    if loads_file:
        load_summary = process_loads_file(conn, loads_file)
    conn.close()
    return {
        "fuel_summary": fuel_summary,
        "load_summary": load_summary
    }


