flask data entry refactor 

step 1: new route in app.py 
@app.route("add/load", methods=["GET", "POST"])
def add_load():

step 2: GET request:
load_sequence shall be calculated by the app
date
load_type
miles
rate

step 3: post request:backend recieves form data:

date = request.form.get("date")
load_type = request.form.get("load_type")
miles = request.form.get("miles")
rate = request.form.get("rate")

step 4 generate load_sequence:
create a query that generates the load sequence for that date 

SELECT MAX(load_sequence)
FROM loads
WHERE date = ?
next_sequence = max_sequence + 1
if no loads next_sequence = 1 

Step 5: Create a row dictionary to clean up my data:

row = {
    "date": date,
    "load_type": load_type
    "load_sequence": next_sequence,
    "miles": miles,
    "rate": rate
}

step 6: use a db helper to insert clean data 

insert_load(conn, cleaned_row)

step 7: redirect
return redirect(url_for("home"))

step 8: error handling if validation fails: stay on form show error message and no inserts