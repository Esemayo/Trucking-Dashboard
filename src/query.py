import sqlite3
from metrics import calculate_fuel_metrics
conn = sqlite3.connect("data/trucking.db")
cursor = conn.cursor()
cursor.execute("""
SELECT date, load_type, load_sequence, miles, rate, rate_per_mile, profit_per_mile 
FROM loads
ORDER BY (profit_per_mile) DESC;
""")
rows = cursor.fetchall()
print("---All Loads---")
for row in rows:
    date, load_type, load_sequence, miles, rate, rate_per_mile, profit_per_mile = row
    if profit_per_mile > 0.30:
        status = "Profit"
    elif profit_per_mile >=0:
        status = "Barely" 
    else:
        status = "Loss"
    print(f"Date: {date:<12} |load_type: {load_type:<10} |seq: {load_sequence:<3} |miles: {miles:<5.0f} |rate: {rate:<5.0f} |rate/mi: {rate_per_mile:<5.2f} |profit/mi : {profit_per_mile:<5.2f} | {status}")
cursor.execute("""
SELECT
    load_type,
    AVG(profit_per_mile),
    SUM(profit_per_mile * miles),
    COUNT(*)
FROM loads
GROUP BY load_type
ORDER BY SUM(profit_per_mile * miles) DESC, AVG(profit_per_mile) DESC, COUNT(*) DESC;
""")
rows = cursor.fetchall()
print("_" * 70)
print("Type         Average Profit/Mi     Total Profit        Load count")
print("_" * 70)
for row in rows:
    load_type, avg_profit, sum_profit, count = row
    print(f"{load_type:<10} |  {avg_profit:<14.2f} |  {sum_profit:>10.2f} | {count:>12}")
print("_" * 70)
print("Date         Miles/Day             Total profit/day    Avg Profit/mile/day")
print("_" * 70)
cursor.execute("""
SELECT
    date,
    SUM(miles),
    SUM(profit_per_mile * miles),
    SUM(profit_per_mile * miles) / SUM(miles)
FROM loads
GROUP BY date
ORDER BY SUM(profit_per_mile * miles);
""")
rows = cursor.fetchall()
for row in rows:
    date, miles, sum_profit, avg_profit_per_mile = row
    print(f"{date:<10}  | {miles:<9}| {sum_profit:>16.2f} | {avg_profit_per_mile:>16.2f}")
def recent_fuel_mpg(cursor):
    cursor.execute("""
    SELECT purchase_date, gallons, odometer, cost_per_gallon
    FROM fuel_purchases
    ORDER BY purchase_date DESC, odometer DESC
    LIMIT 2;
    """)
    rows = cursor.fetchall()
    if len(rows) < 2:
        print("Not enough fuel data to claculate MPG")
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
recent_fuel_mpg(cursor)
#next step- use fuel cost per mile to calculate cost per mile and move metrics in query.py to metrics.py 