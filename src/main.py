import csv
import sqlite3
from cleaners import clean_row, clean_row_fuel, clean_date
from db import db_connection, create_tables, insert_load, insert_fuel
from loaders import load_csv
from metrics import load_metrics, calculate_cost_per_gallon
from query import recent_fuel_mpg
def main():
    conn =db_connection()
    create_tables(conn)
    cursor = conn.cursor()
    input_file = "data/sample_fuel_purchase.csv"
    inserted = 0
    skipped = 0
    print("_" * 90)
    print("Fuel Summary")
    print("_" * 90)
    rows = load_csv(input_file)
    last_odometer = None
    for row in rows:    
        cleaned_row_fuel, error = clean_row_fuel(row)
        if error:
            skipped += 1
            print(f"Skipped row with date {row['purchase_date']} skipped: {error}")
            continue
        if last_odometer is not None and cleaned_row_fuel["odometer"] < last_odometer:
            skipped += 1
            print(f"Skipped row with backwards odometer, purchase date: {row["purchase_date"]}")
            continue
        last_odometer = cleaned_row_fuel["odometer"]
        cleaned_row_fuel = calculate_cost_per_gallon(cleaned_row_fuel)
        try:
            insert_fuel(conn, cleaned_row_fuel)
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1
            print(f"Skipped duplicate: date = {cleaned_row["purchase_date"]}")
            continue 
    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")
    input_file = "data/sample_loads.csv"
    inserted = 0
    skipped = 0
    print("_" * 90)
    print("Load Summary")
    print("_" * 90)
    rows = load_csv(input_file)
    fuel_cost_per_mile = recent_fuel_mpg(cursor)
    for row in rows:  
        cleaned_row, error = clean_row(row)
        if error:
            skipped += 1
            print(f"Skipped row with date {row['date']} skipped: {error}")
            continue
        cleaned_row = load_metrics(cleaned_row, fuel_cost_per_mile)
        try:
            insert_load(conn, cleaned_row)
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1
            print(f"Skipped duplicate: date = {cleaned_row["date"]}  load_sequence = {cleaned_row['load_sequence']}")
            continue  
    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")
    conn.commit()   
     
main()
#current status: CSV -> validation -> SQlite insert -> database querys 
#next step clean the fuel calculation usage so the variable names and insert call match the actual return type


