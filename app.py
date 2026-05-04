from flask import Flask, render_template, redirect, url_for, request
from src.query import get_recent_loads, daily_summary, get_load_performance, recent_fuel_mpg
from src.main import run_pipeline
from src.load_calculator import calculate_test_load
from src.db import db_connection, create_tables
app = Flask(__name__)
app.secret_key = "dev"
def classify_day(total_profit):
    if total_profit is None:
        return "no-data"
    if total_profit < 200:
        return "bad"
    elif total_profit < 350:
        return "okay"
    elif total_profit < 500:
        return "good"
    else:
        return "great"
@app.route("/run_pipeline", methods=["POST"])
def run_pipeline_route():
    results = run_pipeline(
        loads_file="data/sample_loads.csv",
        fuel_file="data/sample_fuel_purchase.csv"
    )
    return render_template(
        "index.html",
        pipeline_results=results,
        **get_home_data()
    )
@app.route("/calculate_load", methods=["POST"])
def calculate_load():
    miles_text = request.form.get("miles", "").strip()
    rate_text = request.form.get("rate", "").strip()
    if not miles_text or not rate_text:
        return render_template(
            "index.html",
            calc_result=None,
            error="Both miles and rate are required",
            **get_home_data()
    )    
    try:
        miles = float(miles_text)
        rate = float(rate_text)
    except ValueError:
        return render_template(
            "index.html",
            calc_result=None,
            error="Both miles and rate must be valid numbers",
            **get_home_data()
    )   
    if miles <= 0 or rate <= 0:
        return render_template(
            "index.html",
            calc_result=None,
            error="Miles and Rate must be higher then 0",
            **get_home_data()
    )   
    results = calculate_test_load(miles, rate, "rebar")
    return render_template(
        "index.html",
        calc_result=results["metrics"],
        pipeline_results=None,
        **get_home_data()

    )
@app.route("/add/load", methods=["GET", "POST"])
def add_load():
    if request.method == "POST":
        print(request.form)
        return redirect(url_for("home"))
    return render_template(
        "add_load.html",
        error=None,
        **get_home_data()
    )
def get_home_data():
    summary_data = daily_summary()
    date, total_profit, daily_miles, load_count, avg_profit_per_mile = summary_data
    loads_data = get_recent_loads()
    load_performance = get_load_performance()
    if load_performance:
        best_efficiency = max(load_performance, key=lambda row: row["weighted_ppm"])
        best_volume = max(load_performance, key=lambda row: row["total_profit"])
    else:
        best_efficiency = None
        best_volume = None
    raw_profit = total_profit
    day_status = classify_day(raw_profit)
    return {
        "date": date,
        "raw_profit": total_profit,
        "total_profit": raw_profit if raw_profit is not None else 0,
        "daily_miles": daily_miles,
        "load_count": load_count,
        "avg_profit_per_mile": avg_profit_per_mile if avg_profit_per_mile is not None else 0,
        "loads_data": loads_data,
        "load_performance": load_performance,
        "best_efficiency": best_efficiency,
        "best_volume": best_volume,
        "day_status": day_status
    }
@app.route("/")
def home():
    return render_template(
        "index.html",
        calc_result=None,
        pipeline_results=None,
        **get_home_data()
    )
if __name__ == "__main__":
    app.run(debug=True)
