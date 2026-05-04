import sqlite3
def db_connection():
    return sqlite3.connect("data/trucking.db")
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS loads;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loads(
            id INTEGER PRIMARY KEY,
            date TEXT,
            load_type TEXT,
            load_sequence INTEGER, 
            miles INTEGER,
            rate REAL,
            rate_per_mile,
            net_profit_per_mile,
            UNIQUE(date, load_sequence)
    );
    """) 
    print("Creating Tables")
    cursor.execute("DROP TABLE IF EXISTS fuel_purchases;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fuel_purchases(
                fuel_id INTEGER PRIMARY KEY,
                purchase_date TEXT,
                gallons REAL,
                total_cost REAL,
                odometer INTEGER,
                cost_per_gallon REAL,
                UNIQUE(purchase_date, odometer)
    );
    """)
def insert_load(conn, row):
    cursor = conn.cursor()
    values = (
            row["date"],
            row["load_type"],
            row["load_sequence"],
            row["miles"],
            row["rate"],
            row["rate_per_mile"],
            row["net_profit_per_mile"]
    )
    cursor.execute("""
    INSERT INTO loads (
        date,
        load_type,
        load_sequence,
        miles,
        rate,
        rate_per_mile,
        net_profit_per_mile
    )  
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, values)
def insert_fuel(conn, row):
    cursor = conn.cursor()
    values = (
            row["purchase_date"],
            row["gallons"],
            row["total_cost"],
            row["odometer"],
            row["cost_per_gallon"]
        )
    cursor.execute("""
    INSERT INTO fuel_purchases (
        purchase_date,
        gallons,
        total_cost,
        odometer,
        cost_per_gallon

    )  
    VALUES (?, ?, ?, ?, ?)
    """, values)
