from flask import Flask, render_template
from src.query import get_recent_loads, daily_summary, get_load_performance, recent_fuel_mpg
app = Flask(__name__)
@app.route("/")
def classify_day(total_profit):
    if total_profit < 200:
        return "bad"
    elif total_profit < 350:
        return "okay"
    elif total_profit < 500:
        return "good"
    else:
        return "great"
def home():
    summary_data = daily_summary()
    date, total_profit, daily_miles, load_count, avg_profit_per_mile = summary_data
    loads_data = get_recent_loads()
    load_performance = get_load_performance()
    best_efficiency = max(load_performance, key=lambda row: row["weighted_ppm"])
    best_volume = max(load_performance, key=lambda row: row["total_profit"])
    return render_template(
        "index.html",
        date=date,  
        total_profit=total_profit,
        daily_miles=daily_miles,
        load_count=load_count,
        avg_profit_per_mile=avg_profit_per_mile,
        loads_data=loads_data,
        load_performance = load_performance,
        best_efficiency = best_efficiency["load_type"],
        best_volume = best_volume["load_type"],
        day_status = classify_day(total_profit)
    )
if __name__ == "__main__":
    app.run(debug=True)
    