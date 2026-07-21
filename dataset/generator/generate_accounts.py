# Import libraries

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configuration
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

fake = Faker("en_US")

random.seed(42)
np.random.seed(42)
Faker.seed(42)

# ---------------------------------------
# Daily Inventory Configuration
# ---------------------------------------

MIN_DAILY_INVENTORY = 500
MAX_DAILY_INVENTORY = 1000

# ---------------------------------------
# Simulation Period
# ---------------------------------------

SIMULATION_START = datetime(2026, 1, 1)
SIMULATION_END = datetime(2026, 1, 31)

# Used later for Age calculations
TODAY = SIMULATION_END

# ---------------------------------------
# Business Calendar
# ---------------------------------------

business_days = pd.date_range(
    start=SIMULATION_START,
    end=SIMULATION_END,
    freq="B"      # Business Days only (Mon-Fri)
)

# -----------------------------------------------------
# Existing Portfolio + January 2026 New Placements
# -----------------------------------------------------

EXISTING_ACCOUNTS = 12000

daily_inventory = []

# Existing inventory
historical_start = datetime(2024, 7, 1)
historical_end = datetime(2025, 12, 31)

for _ in range(EXISTING_ACCOUNTS):

    random_days = random.randint(
        0,
        (historical_end - historical_start).days
    )

    placement_date = historical_start + timedelta(days=random_days)

    daily_inventory.append(placement_date)

# January 2026 new inventory
for day in business_days:

    accounts_today = random.randint(
        120,
        180
    )

    daily_inventory.extend(
        [day] * accounts_today
    )

random.shuffle(daily_inventory)

NUM_ACCOUNTS = len(daily_inventory)

print(f"Business Days : {len(business_days)}")
print(f"Accounts Generated : {NUM_ACCOUNTS:,}")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# State-City Mapping
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

state_city_map = {
    "California": ["Los Angeles", "San Diego", "San Jose", "Sacramento"],
    "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
    "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
    "New York": ["New York", "Buffalo", "Albany", "Rochester"],
    "Illinois": ["Chicago", "Springfield", "Naperville"],
    "Georgia": ["Atlanta", "Savannah", "Augusta"],
    "Arizona": ["Phoenix", "Tucson", "Mesa"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati"],
    "North Carolina": ["Charlotte", "Raleigh", "Greensboro"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown"]
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Account Identity
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

accounts = pd.DataFrame()

accounts["Account_ID"] = range(1, NUM_ACCOUNTS + 1)

accounts["Account_Number"] = [
    f"NVT{str(i).zfill(8)}"
    for i in range(1, NUM_ACCOUNTS + 1)
]

accounts["Customer_First_Name"] = [
    fake.first_name()
    for _ in range(NUM_ACCOUNTS)
]

accounts["Customer_Last_Name"] = [
    fake.last_name()
    for _ in range(NUM_ACCOUNTS)
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate State, City and Zip Code
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

states = []
cities = []
zip_codes = []

for _ in range(NUM_ACCOUNTS):

    state = random.choice(list(state_city_map.keys()))
    city = random.choice(state_city_map[state])

    states.append(state)
    cities.append(city)

    zip_codes.append(fake.postcode())

accounts["State"] = states
accounts["City"] = cities
accounts["Zip_Code"] = zip_codes

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Outstanding Balance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

balance_ranges = [
    (100, 500),
    (500, 1000),
    (1000, 2500),
    (2500, 5000),
    (5000, 10000),
    (10000, 20000)
]

stage_balance_weights = {

    "Pre-Writeoff": [0.05, 0.10, 0.20, 0.25, 0.25, 0.15],

    "Primary":      [0.08, 0.15, 0.27, 0.25, 0.17, 0.08],

    "Secondary":    [0.15, 0.22, 0.30, 0.20, 0.10, 0.03],

    "Tertiary":     [0.25, 0.28, 0.25, 0.15, 0.06, 0.01],

    "Warehouse":    [0.35, 0.30, 0.20, 0.10, 0.04, 0.01]

}

balances = []

for placement_date in daily_inventory:

    days_in_inventory = (TODAY - placement_date).days

    if days_in_inventory <= 45:
        stage = "Pre-Writeoff"

    elif days_in_inventory <= 225:
        stage = "Primary"

    elif days_in_inventory <= 405:
        stage = "Secondary"

    elif days_in_inventory <= 585:
        stage = "Tertiary"

    else:
        stage = "Warehouse"

    selected_range = random.choices(

        balance_ranges,

        weights=stage_balance_weights[stage],

        k=1

    )[0]

    balance = round(

        random.uniform(selected_range[0], selected_range[1]),

        2

    )

    balances.append(balance)

accounts["Original_Balance"] = balances

accounts["Outstanding_Balance"] = accounts["Original_Balance"]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Generate Credit Score
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

credit_scores = np.random.normal(
    loc=640,
    scale=70,
    size=NUM_ACCOUNTS
)

credit_scores = np.clip(
    credit_scores,
    350,
    850
)

accounts["Credit_Score"] = credit_scores.astype(int)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Placement Date
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

placement_dates = []

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Placement Date
# Based on Daily Inventory
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

accounts["Placement_Date"] = [
    placement_date.date()
    for placement_date in daily_inventory
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Charge-Off Date
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

charge_off_dates = []

for placement_date in accounts["Placement_Date"]:

    placement_date = pd.to_datetime(placement_date)

    # Client sends inventory within 1–45 days after charge-off
    charge_off_date = placement_date - timedelta(
        days=random.randint(1, 45)
    )

    charge_off_dates.append(charge_off_date.date())

accounts["Charge_Off_Date"] = charge_off_dates

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Collection Stage
# Based on Placement Age
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

collection_stage = []

for placement_date in accounts["Placement_Date"]:

    placement_date = pd.to_datetime(placement_date)

    days_in_inventory = (TODAY - placement_date).days

    if days_in_inventory <= 45:
        collection_stage.append("Pre-Writeoff")

    elif days_in_inventory <= 225:
        collection_stage.append("Primary")

    elif days_in_inventory <= 405:
        collection_stage.append("Secondary")

    elif days_in_inventory <= 585:
        collection_stage.append("Tertiary")

    else:
        collection_stage.append("Warehouse")

accounts["Collection_Stage"] = collection_stage

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Days Past Due
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

dpd = []

for stage in accounts["Collection_Stage"]:

    if stage == "Pre-Writeoff":
        dpd.append(random.randint(30, 89))

    elif stage == "Primary":
        dpd.append(random.randint(90, 180))

    elif stage == "Secondary":
        dpd.append(random.randint(181, 360))

    elif stage == "Tertiary":
        dpd.append(random.randint(361, 540))

    else:  # Warehouse
        dpd.append(random.randint(541, 720))

accounts["Days_Past_Due"] = dpd

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Last Payment Date
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

last_payment_dates = []

for placement in accounts["Placement_Date"]:

    if random.random() < 0.35:

        last_payment_dates.append(pd.NaT)

    else:

        payment = placement + timedelta(
            days=random.randint(5,300)
        )

        if payment > TODAY.date():
            payment = TODAY.date()

        last_payment_dates.append(payment)

accounts["Last_Payment_Date"] = last_payment_dates

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Account Tenure
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

accounts["Account_Tenure_Months"] = (
    (
        pd.to_datetime(TODAY)
        - pd.to_datetime(accounts["Charge_Off_Date"])
    ).dt.days // 30
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Account Status
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

accounts["Account_Status"] = "Active"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Bankruptcy Flag
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

accounts["Bankruptcy_Flag"] = np.random.choice(
    [0,1],
    size=NUM_ACCOUNTS,
    p=[0.98,0.02]
)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate Fraud Flag
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

accounts["Fraud_Flag"] = np.random.choice(
    [0,1],
    size=NUM_ACCOUNTS,
    p=[0.99,0.01]
)


#print(accounts["Credit_Score"].describe())

#print(accounts["Outstanding_Balance"].describe())
#print(
#    pd.cut(
#        accounts["Outstanding_Balance"],
#        bins=[0,500,1000,2500,5000,10000,20000]
#    ).value_counts().sort_index()
#)

#print(
#    accounts.groupby("Collection_Stage")["Days_Past_Due"].describe()
#)
#print(accounts["Collection_Stage"].value_counts())
print(accounts.head(10))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Export to CSV
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os

print(os.getcwd())

accounts.to_csv(
    "data/generated/Accounts.csv",
    index=False
)

print("Accounts.csv generated successfully!")

print(accounts.columns.tolist())

print(accounts.shape)
print(accounts.head())