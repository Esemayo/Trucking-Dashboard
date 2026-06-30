from flask import Flask, render_template, redirect, url_for, request
from src.query import get_recent_loads, daily_summary, get_load_performance, recent_fuel_mpg, get_next_load_sequence, total_expense, get_all_expenses
from src.main import run_pipeline
from src.load_calculator import calculate_test_load
from src.db import db_connection, create_tables, insert_load, insert_fuel,create_expense_table, insert_expense
from src.cleaners import clean_row, clean_row_fuel, clean_expense, clean_load
from src.metrics import load_metrics, get_fuel_cost_per_mile, calculate_cost_per_gallon, get_fixed_cost_per_mile, multi_load_metrics
import sqlite3
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
    loads_per_day_text = request.form.get("loads_per_day", "").strip()
    conn = db_connection()
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
        loads_per_day = int(loads_per_day_text)
    except ValueError:
        return render_template(
            "index.html",
            calc_result=None,
            error="Both miles and rate must be valid numbers",
            **get_home_data()
    )
    if miles <= 0 or rate <= 0 or loads_per_day <= 0:
        return render_template(
            "index.html",
            calc_result=None,
            error="Miles and Rate must be higher then 0",
            **get_home_data()
    )   
    fixed_cpm = get_fixed_cost_per_mile(conn)
    results = calculate_test_load(miles, rate, "rebar", fixed_cpm, loads_per_day)
    return render_template(
        "index.html",
        calc_result=results["metrics"],
        pipeline_results=None,
        **get_home_data()
    )
@app.route("/add/load", methods=["GET", "POST"])
def add_load():
    successful_entry = None
    if request.method == "POST":
        date = request.form.get("date")
        load_type = request.form.get("load_type")
        miles = request.form.get("miles")
        rate = request.form.get("rate")
        conn = db_connection()
        form_data = {
            "date": date,
            "load_type": load_type,
            "miles": miles,
            "rate": rate
        }
        row = {
            "date": date,
            "load_type": load_type,
            "miles": miles,
            "rate": rate
        }
        cleaned_row, errors = clean_load(row)
        if errors:
            print("Error:", errors)
            return render_template(
                "add_load.html",
                errors=errors,
                form_data=form_data,
                successful_entry=None,
                **get_home_data()
            )
        cleaned_row["load_sequence"] = get_next_load_sequence(conn, cleaned_row["date"])
        fuel_cost_per_mile = get_fuel_cost_per_mile(
            conn,
            cleaned_row["date"]
        )
        fixed_cpm = get_fixed_cost_per_mile(conn)
        cleaned_row = load_metrics(cleaned_row, fuel_cost_per_mile, fixed_cpm)
        try:
            insert_load(conn, cleaned_row)
            conn.commit()
            successful_entry = cleaned_row
        except sqlite3.IntegrityError:
            return render_template(
                "add_load.html",
                error=["Load entry already exists"],
                form_data=form_data,
                successful_entry=None,
                **get_home_data()
            )
        finally:
            conn.close()
    return render_template(
        "add_load.html",
        error=None,
        form_data={},
        successful_entry=successful_entry,
        **get_home_data()
    )
@app.route("/loads")
def loads():
    loads_data = get_recent_loads()
    return render_template("loads.html", loads_data=loads_data)
@app.route("/add/fuel", methods=["GET", "POST"])
def add_fuel():
    successful_entry = None
    if request.method=="POST":
        purchase_date = request.form.get("purchase_date")
        gallons = request.form.get("gallons")
        total_cost = request.form.get("total_cost")
        odometer = request.form.get("odometer")
        form_data = {
            "purchase_date": purchase_date,
            "gallons": gallons,
            "total_cost": total_cost,
            "odometer": odometer
        }
        row = {
            "purchase_date": purchase_date,
            "gallons": gallons,
            "total_cost": total_cost,
            "odometer": odometer
        }
        cleaned_row_fuel, error = clean_row_fuel(row)
        successful_entry = cleaned_row_fuel
        if error:
            print("Error:", error)
            return render_template(
                "add_fuel.html",
                form_data=form_data,
                error=error,
                successful_entry=None,
                **get_home_data()
            )
        cleaned_row_fuel = calculate_cost_per_gallon(cleaned_row_fuel)
        conn = db_connection()
        try:
            insert_fuel(conn, cleaned_row_fuel)
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template(
                "add_fuel.html",
                error=["Fuel entry already exists"],
                form_data=form_data,
                successful_entry=None,
                **get_home_data()
            )
        finally:
            conn.close()
    return render_template(
        "add_fuel.html",
        error=None,
        form_data={},
        successful_entry=successful_entry,
        **get_home_data()
    )
@app.route("/set/expenses", methods=["GET", "POST"])
def set_expenses():
    if request.method=="POST":
        expense_name = request.form.get("expense_name")
        monthly_cost = request.form.get("monthly_cost")
        expense_name, monthly_cost, errors = clean_expense(
            expense_name,
            monthly_cost
        ) 
        form_data = {
            "expense_name": expense_name,
            "monthly_cost": monthly_cost
        }
        if errors:
            return render_template(
                "set_expenses.html",
                error=errors[0],
                form_data=form_data,
                **get_home_data()
            )
        conn = db_connection()
        try:
            create_expense_table(conn)
            insert_expense(conn, expense_name, monthly_cost)
            return redirect(url_for("set_expenses"))
        except sqlite3.IntegrityError:
            expenses = get_all_expenses(conn)
            total_monthly_cost = total_expense(conn)
            conn.close()
            return render_template(
                "set_expenses.html",
                error="Expense was repeated",
                expenses=expenses,
                total_monthly_cost=total_monthly_cost,
                form_data=form_data,
                **get_home_data()
                )
    conn = db_connection()
    expenses = get_all_expenses(conn)
    total_monthly_cost = total_expense(conn)
    conn.close()
    return render_template(
        "set_expenses.html",
        error=None,
        expenses=expenses,
        total_monthly_cost=total_monthly_cost,
        form_data={}
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
    
