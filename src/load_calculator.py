from src.cleaners import clean_row
from src.metrics import load_metrics
from datetime import date
def calculate_test_load(miles, rate, load_type):
    test_load = {
        "date": date.today().isoformat(),
        "load_type": load_type,
        "load_sequence": 1,
        "miles": miles,
        "rate": rate
    }
    cleaned_row, error = clean_row(test_load)
    fuel_cost_per_mile = 0.65
    if error:
        return {
            "success": False,
            "error": error,
            "metrics": None
        }
    metrics = load_metrics(cleaned_row, fuel_cost_per_mile)
    estimated_fuel_cost = cleaned_row["miles"] * fuel_cost_per_mile
    estimated_driver_pay = 200
    decision_profit = cleaned_row["rate"] - estimated_fuel_cost - estimated_driver_pay
    decision_rpm = decision_profit / cleaned_row["miles"]
    metrics["estimated_fuel_cost"] = estimated_fuel_cost
    metrics["estimated_driver_pay"] = estimated_driver_pay
    metrics["decision_profit"] = decision_profit
    metrics["decision_rpm"] = decision_rpm
    return {
        "success": True,
        "error": None,
        "metrics": metrics
    }


