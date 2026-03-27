import sqlite3
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
print("Type         Average Profit/Mi     Total Profit           Load count")
print("_" * 70)
for row in rows:
    load_type, avg_profit, sum_profit, count = row
    print(f"{load_type:<10} | avg profit/mi: {avg_profit:.2f} | Total Profit {sum_profit:.2f} |Load_Count: {count}")
