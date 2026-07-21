# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOVATEL COLLECTIONS FRAMEWORK
# Generate Promise To Pay Table
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import random
import numpy as np
import pandas as pd

from datetime import timedelta

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configuration
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

random.seed(42)
np.random.seed(42)

TODAY = pd.Timestamp("2026-01-31")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load Data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

accounts = pd.read_csv("data/generated/Accounts.csv")

calls = pd.read_csv("data/generated/Call_Interactions.csv")

accounts = accounts[
    [
        "Account_ID",
        "Outstanding_Balance",
        "Collection_Stage"
    ]
]

calls["Call_Date"] = pd.to_datetime(
    calls["Call_Date"]
)

print("Total Calls:", len(calls))

print("Promise_To_Pay Flag:")
print(calls["Promise_To_Pay"].value_counts())

print()

print("Agent Disposition:")
print(calls["Agent_Disposition"].value_counts(dropna=False))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Merge Calls with Balance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

calls = calls.merge(

    accounts,

    on="Account_ID",

    how="left"

)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Keep only Promise To Pay Calls
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ptp_calls = calls[
    calls["Promise_To_Pay"] == 1
].copy()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Only One Promise Per Account
# Keep the Earliest Promise
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ptp_calls = (
    ptp_calls
    .sort_values(["Account_ID", "Call_Date"])
    .drop_duplicates(subset="Account_ID", keep="first")
    .reset_index(drop=True)
)

print("PTP Calls after sorting:", len(ptp_calls))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Begin Generation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
previous_status = {}

promise_records = []

promise_id = 1

for _, row in ptp_calls.iterrows():

    balance = row["Outstanding_Balance"]
    stage = row["Collection_Stage"]
    promise_date = row["Call_Date"]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Promise Due Date
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    promise_due_date = (

        promise_date

        +

        timedelta(

            days=random.randint(1,30)

        )

    )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Promise Strategy
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    balance = row["Outstanding_Balance"]

    if stage == "Pre-Writeoff":

        strategy = random.choices(

                ["Full", "Partial"],

                weights=[80,20],

                k=1

        )[0]

    elif stage == "Primary":

        strategy = random.choices(

            ["Full","Partial","Installment"],

            weights=[40,40,20],

            k=1

        )[0]

    elif stage == "Secondary":

        strategy = random.choices(

            ["Partial","Installment","Settlement"],

            weights=[35,35,30],

            k=1

        )[0]

    else:       # Tertiary / Warehouse

        strategy = random.choices(

            ["Settlement","Installment","Partial"],

            weights=[55,30,15],

            k=1

        )[0]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Promised Amount
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if strategy == "Full":

        promised_amount = balance

    elif strategy == "Partial":

        promised_amount = round(

            balance

            *

            random.uniform(

                0.30,

                0.70

            ),

            2

        )

    elif strategy == "Settlement":

        promised_amount = round(

            balance

            *

            random.uniform(

                0.40,

                0.80

            ),

            2

        )

    else:

        promised_amount = round(

            balance

            *

            random.uniform(

                0.10,

                0.30

            ),

            2

        )
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Promise Status
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    account_id = row["Account_ID"]

    last_status = previous_status.get(account_id)

    if promise_due_date > TODAY:

        promise_status = "Active"

    else:

        if stage == "Pre-Writeoff":
            kept_weight = 85

        elif stage == "Primary":
            kept_weight = 70

        elif stage == "Secondary":
            kept_weight = 50

        elif stage == "Tertiary":
            kept_weight = 30

        else:   # Warehouse
            kept_weight = 15

        if strategy == "Settlement":
            kept_weight += 10

        elif strategy == "Installment":
            kept_weight += 5

        elif strategy == "Full":
            kept_weight -= 10

        if last_status == "Broken":
            kept_weight -= 20

        elif last_status == "Kept":
            kept_weight += 10

        kept_weight = max(5, min(95, kept_weight))

        promise_status = random.choices(

            ["Kept", "Broken"],

            weights=[kept_weight, 100 - kept_weight],

            k=1

        )[0]

    previous_status[account_id] = promise_status

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Append Record
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    promise_records.append({

            "Promise_ID": promise_id,

            "Call_ID": row["Call_ID"],

            "Account_ID": row["Account_ID"],

            "Promise_Date": promise_date.date(),

            "Promise_Due_Date": promise_due_date.date(),

            "Promised_Amount": round(promised_amount,2),

            "Promise_Status": promise_status

        })

    promise_id += 1


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create DataFrame
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

promise_to_pay = pd.DataFrame(promise_records)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Sort Records
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

promise_to_pay = promise_to_pay.sort_values(

    by=[

        "Account_ID",

        "Promise_Date"

    ]

).reset_index(drop=True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Validation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("=" * 50)

print("Promise To Pay Summary")

print("=" * 50)

print(f"Total Promises : {len(promise_to_pay):,}")

print()

print("Promise Status Distribution")

print(

    promise_to_pay["Promise_Status"]

    .value_counts()

)

print()

print("Average Promised Amount")

print(

    round(

        promise_to_pay["Promised_Amount"].mean(),

        2

    )

)

print("=" * 50)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~=
# Export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

os.makedirs(

    "data/generated",

    exist_ok=True

)

promise_to_pay.to_csv(

    "data/generated/Promise_To_Pay.csv",

    index=False

)

print()

print("Promise_To_Pay.csv generated successfully.")

print(promise_to_pay.head(10))

print(promise_to_pay.shape)