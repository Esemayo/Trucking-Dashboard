from src.query import recent_fuel_mpg, total_expense
from src.cleaners import clean_row
from src.db import db_connection
from datetime import datetime
import sqlite3
def load_metrics(row, fuel_cost_per_mile, fixed_cpm):
    miles = row["miles"] 
    rate = row["rate"]
    total_cost_per_mile = fixed_cpm + fuel_cost_per_mile
    rate_per_mile = rate/miles
    net_profit_per_mile = rate_per_mile - total_cost_per_mile 
    row["rate_per_mile"] = rate_per_mile
    row["net_profit_per_mile"] = net_profit_per_mile
    return row 
def multi_load_metrics(total_rate, total_miles, fuel_cost_per_mile, fixed_cpm):
     total_cost_per_mile = fixed_cpm + fuel_cost_per_mile
     rate_per_mile = total_rate/total_miles
     net_profit_per_mile = rate_per_mile - total_cost_per_mile
     return {
          "rate_per_mile": rate_per_mile,
          "net_profit_per_mile": net_profit_per_mile,
          "total_miles": total_miles,
          "total_rate": total_rate
     }
def calculate_cost_per_gallon(row):
    total_cost = row["total_cost"]
    gallons = row["gallons"]
    cost_per_gallon = total_cost / gallons
    row["cost_per_gallon"] = cost_per_gallon
    return row
def get_fuel_cost_per_mile(conn, load_date):
    fuel_result = recent_fuel_mpg(conn)
    if fuel_result is None:
            fuel_cost_per_mile = 2.00
            print("WARNING: using placeholder fuel cost per mile = 2.00")
            return fuel_cost_per_mile
    fuel_cost_per_mile, fuel_date = fuel_result
    fuel_dt = datetime.strptime(fuel_date, "%Y-%m-%d").date()
    load_dt = datetime.strptime(load_date, "%Y-%m-%d").date()
    days_gap = (load_dt - fuel_dt).days
    if days_gap > 7:
        fuel_cost_per_mile = 2.00
        print("WARNING: using placeholder fuel cost per mile = 2.00")
    return fuel_cost_per_mile
def get_fixed_cost_per_mile(conn):
    total_monthly_cost = total_expense(conn)
    if total_monthly_cost is None:
         return 0 
    default_monthly_miles = 4000
    monthly_miles = default_monthly_miles
    if monthly_miles <= 0:
         return 0 
    fixed_cpm = total_monthly_cost / monthly_miles
    return fixed_cpm
