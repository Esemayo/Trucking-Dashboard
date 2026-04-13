import sqlite3
from src.metrics import calculate_fuel_metrics
def get_recent_loads():
    conn = sqlite3.connect("data/trucking.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT date, load_type, load_sequence, miles, rate, profit_per_mile 
    FROM loads
    ORDER BY date DESC, load_sequence DESC
    LIMIT 10;
    """)
    rows = cursor.fetchall()
    loads_data = []
    for row in rows:
        date, load_type, load_sequence, miles, rate, profit_per_mile = row
        if profit_per_mile > 0.30:
            status = "Profit"
        elif profit_per_mile >=0:
            status = "Barely" 
        else:
            status = "Loss"
        loads_data.append({
            "date": date,
            "load_type": load_type,
            "load_sequence": load_sequence,
            "miles": miles,
            "rate": rate,
            "ppm": profit_per_mile,
            "status": status
        })
    conn.close()
    return loads_data
def get_load_performance():
    conn = sqlite3.connect("data/trucking.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        load_type,
        AVG(profit_per_mile),
        SUM(profit_per_mile * miles),
        SUM(profit_per_mile * miles) / SUM(miles),
        SUM(miles)
    FROM loads
    GROUP BY load_type
    ORDER BY SUM(profit_per_mile * miles) DESC, AVG(profit_per_mile) DESC;
    """)
    rows = cursor.fetchall()
    performance_data = []
    for row in rows:
        load_type, avg_profit, total_profit, weighted_ppm, total_miles = row
        performance_data.append({
            "load_type": load_type,
            "avg_profit": avg_profit,
            "total_profit": total_profit,
            "weighted_ppm": weighted_ppm,
            "total_miles": total_miles
        })
    conn.close()
    return performance_data
def daily_summary():
    conn = sqlite3.connect("data/trucking.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        date,
        SUM(profit_per_mile * miles),
        SUM(miles),
        COUNT(*),
        SUM(profit_per_mile * miles) / SUM(miles)
    FROM loads
    WHERE date = (SELECT MAX(date)FROM loads);
    """)
    row = cursor.fetchone()
    return row
def recent_fuel_mpg(cursor):
    conn = sqlite3.connect("data/trucking.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        purchase_date,
        gallons,
        odometer,
        cost_per_gallon
    FROM fuel_purchases
    ORDER BY purchase_date DESC, odometer DESC
    LIMIT 2;
    """)
    rows = cursor.fetchall()
    if len(rows) < 2:
        print("Not enough fuel data to calculate MPG")
        return
    current = rows[0]
    previous = rows[1]
    current_purchase_date, current_gallons, current_odometer, current_cost_per_gallon = current
    previous_purchase_date, previous_gallons, previous_odometer, previous_cost_per_gallon = previous
    if current_odometer <= previous_odometer:
        print("Invalid odometer sequence for MPG calculations")
        return
    miles_driven, mpg, fuel_cost_per_mile = calculate_fuel_metrics(
        current_odometer,
        previous_odometer,
        current_gallons,
        current_cost_per_gallon
    )
    return fuel_cost_per_mile

