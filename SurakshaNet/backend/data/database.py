import sqlite3
import os
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "surakshanet.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS areas (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        weight REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historical_observations (
        area_id TEXT,
        signal_id TEXT,
        baseline_mean REAL NOT NULL,
        baseline_std REAL NOT NULL,
        PRIMARY KEY (area_id, signal_id),
        FOREIGN KEY (area_id) REFERENCES areas(id),
        FOREIGN KEY (signal_id) REFERENCES signals(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS current_metrics (
        area_id TEXT,
        signal_id TEXT,
        observed_value REAL NOT NULL,
        population_count INTEGER NOT NULL,
        PRIMARY KEY (area_id, signal_id),
        FOREIGN KEY (area_id) REFERENCES areas(id),
        FOREIGN KEY (signal_id) REFERENCES signals(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS privacy_audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        area_id TEXT,
        signal_id TEXT,
        raw_count REAL,
        noise_added REAL,
        noised_count REAL,
        epsilon REAL,
        sensitivity REAL,
        status TEXT,
        FOREIGN KEY (area_id) REFERENCES areas(id),
        FOREIGN KEY (signal_id) REFERENCES signals(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS active_scenario (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    """)

    conn.commit()

    # Seed core meta tables
    seed_areas_and_signals(conn)
    seed_baselines(conn)
    
    # Set default scenario to "Normal"
    cursor.execute("INSERT OR REPLACE INTO active_scenario (id, name) VALUES (1, 'Normal')")
    conn.commit()

    # Initialize current metrics with Normal scenario data
    apply_scenario("Normal", conn)
    conn.close()

def seed_areas_and_signals(conn):
    cursor = conn.cursor()
    
    areas = [
        ("cda_sector_1", "CDA Sector 1"),
        ("cda_sector_5", "CDA Sector 5"),
        ("cda_sector_9", "CDA Sector 9"),
        ("cuttack_rural", "Cuttack Rural"),
        ("barang", "Barang"),
        ("small_village", "Small Village")
    ]
    cursor.executemany("INSERT OR REPLACE INTO areas (id, name) VALUES (?, ?)", areas)

    signals = [
        # Clinic signals (Total 40%)
        ("fever", "Fever Cases", "clinic", 0.15),
        ("respiratory", "Respiratory Symptoms", "clinic", 0.15),
        ("gastrointestinal", "Gastrointestinal Symptoms", "clinic", 0.10),
        # Water Quality signals (Total 30%)
        ("water_turbidity", "Water Turbidity", "water", 0.10),
        ("water_ph", "Water pH", "water", 0.10),
        ("water_contamination", "Contamination Index", "water", 0.10),
        # Pharmacy signals (Total 20%)
        ("ors_demand", "ORS Demand", "pharmacy", 0.10),
        ("fever_meds", "Fever Medication Demand", "pharmacy", 0.10),
        # Environmental signals (Total 10%)
        ("rainfall", "Rainfall", "environment", 0.05),
        ("stagnant_water", "Stagnant Water Index", "environment", 0.05)
    ]
    cursor.executemany("INSERT OR REPLACE INTO signals (id, name, category, weight) VALUES (?, ?, ?, ?)", signals)
    conn.commit()

def seed_baselines(conn):
    cursor = conn.cursor()
    
    # Generate reasonable baselines for each area and signal
    areas = ["cda_sector_1", "cda_sector_5", "cda_sector_9", "cuttack_rural", "barang", "small_village"]
    signals_data = {
        "fever": (12.0, 2.5),
        "respiratory": (15.0, 3.0),
        "gastrointestinal": (8.0, 1.8),
        "water_turbidity": (2.1, 0.4),
        "water_ph": (7.2, 0.2),
        "water_contamination": (10.0, 2.0),
        "ors_demand": (5.0, 1.0),
        "fever_meds": (14.0, 2.8),
        "rainfall": (15.0, 4.0),
        "stagnant_water": (12.0, 2.2)
    }

    # Small village has smaller baseline for human cases
    small_village_signals = {
        "fever": (1.2, 0.4),
        "respiratory": (1.5, 0.5),
        "gastrointestinal": (0.8, 0.3),
        "water_turbidity": (2.1, 0.4),
        "water_ph": (7.2, 0.2),
        "water_contamination": (10.0, 2.0),
        "ors_demand": (0.5, 0.15),
        "fever_meds": (1.4, 0.4),
        "rainfall": (15.0, 4.0),
        "stagnant_water": (12.0, 2.2)
    }

    for area in areas:
        s_data = small_village_signals if area == "small_village" else signals_data
        for sig_id, (mean, std) in s_data.items():
            cursor.execute("""
            INSERT OR REPLACE INTO historical_observations (area_id, signal_id, baseline_mean, baseline_std)
            VALUES (?, ?, ?, ?)
            """, (area, sig_id, mean, std))
    conn.commit()

def apply_scenario(scenario_name, conn=None):
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    
    cursor = conn.cursor()
    cursor.execute("UPDATE active_scenario SET name = ? WHERE id = 1", (scenario_name,))

    # Base populations
    populations = {
        "cda_sector_1": 1500,
        "cda_sector_5": 2000,
        "cda_sector_9": 1800,
        "cuttack_rural": 3000,
        "barang": 1200,
        "small_village": 6  # Small group to trigger suppression
    }

    # Retrieve all baselines
    cursor.execute("SELECT area_id, signal_id, baseline_mean, baseline_std FROM historical_observations")
    baselines = cursor.fetchall()

    for area_id, signal_id, mean, std in baselines:
        pop = populations.get(area_id, 1000)
        
        # Scenario rules
        value = random.normalvariate(mean, std * 0.1) # Default small noise around mean
        value = max(0.1, value) # Avoid negative values

        if scenario_name == "Normal":
            # Keep everything close to baseline
            pass

        elif scenario_name == "Single Source Spike":
            # Clinic cases in CDA Sector 9 spike, others normal
            if area_id == "cda_sector_9" and signal_id in ["fever", "gastrointestinal"]:
                value = mean * 3.5 # Massive isolated spike
                
        elif scenario_name == "Gastrointestinal Cluster":
            # Water, Clinic GI, Pharmacy, Rainfall in CDA Sector 9 all spike
            if area_id == "cda_sector_9":
                if signal_id == "gastrointestinal":
                    value = mean * 3.4  # +240%
                elif signal_id == "water_contamination":
                    value = mean * 2.9  # +190%
                elif signal_id == "ors_demand":
                    value = mean * 2.5  # +150%
                elif signal_id == "rainfall":
                    value = mean * 1.8  # +80%
                elif signal_id == "fever":
                    value = mean * 1.5  # Elevated but not main spike
                elif signal_id == "stagnant_water":
                    value = mean * 1.6

        elif scenario_name == "Rural Under-Reporting":
            # Water contaminated, rain high, but clinic reports in Cuttack Rural are near zero/very low
            if area_id == "cuttack_rural":
                if signal_id in ["water_contamination", "water_turbidity"]:
                    value = mean * 2.9
                elif signal_id == "rainfall":
                    value = mean * 1.9
                elif signal_id in ["fever", "gastrointestinal", "respiratory"]:
                    value = mean * 0.2  # extremely low reporting

        elif scenario_name == "Small Group":
            # Small Village has an anomaly but small population count (6)
            if area_id == "small_village":
                if signal_id == "gastrointestinal":
                    value = mean * 5.0 # Giant relative anomaly but small count

        # Enforce reasonable bounds
        if signal_id == "water_ph":
            # ph bounds
            value = min(14.0, max(0.0, value))
            
        cursor.execute("""
        INSERT OR REPLACE INTO current_metrics (area_id, signal_id, observed_value, population_count)
        VALUES (?, ?, ?, ?)
        """, (area_id, signal_id, value, pop))

    conn.commit()
    if should_close:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
