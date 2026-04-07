from flask import Flask, render_template
from src.query import get_recent_loads, daily_summary
app = Flask(__name__)

@app.route("/")
def home():
    summary_data = daily_summary()
    date, total_profit, daily_miles, load_count, avg_profit_per_mile = summary_data
    loads_data = get_recent_loads()
    return render_template(
        "index.html",
        date=date,  
        total_profit=total_profit,
        daily_miles=daily_miles,
        load_count=load_count,
        avg_profit_per_mile=avg_profit_per_mile,
        loads_data=loads_data
    )
if __name__ == "__main__":
    app.run(debug=True)
#next step refactor query.py into clean functions that return data no prints no top-level execution
#next step zebra rows on table status color coding header styling