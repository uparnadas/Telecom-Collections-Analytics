# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOVATEL COLLECTIONS FRAMEWORK
# Generate Payments Table
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

accounts = pd.read_csv(
    "data/generated/Accounts.csv"
)

calls = pd.read_csv(
    "data/generated/Call_Interactions.csv"
)

ptp = pd.read_csv(
    "data/generated/Promise_To_Pay.csv"
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Date Conversion
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

calls["Call_Date"] = pd.to_datetime(
    calls["Call_Date"]
)

ptp["Promise_Date"] = pd.to_datetime(
    ptp["Promise_Date"]
)

ptp["Promise_Due_Date"] = pd.to_datetime(
    ptp["Promise_Due_Date"]
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Payment Working Copy
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

payment_accounts = accounts[
    [
        "Account_ID",
        "Outstanding_Balance",
        "Collection_Stage"
    ]
].copy()

calls = calls.merge(

    accounts,

    on="Account_ID",

    how="left"

)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Payment Methods
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

payment_methods = [

    "Online Portal",

    "ACH",

    "Card",

    "Bank Transfer"

]

payment_method_weights = [

    40,

    30,

    20,

    10

]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Begin Generation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

payment_records = []

payment_id = 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ --------
# Generate Payments from Promise To Pay
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ============================================================
# Generate Payments Account by Account
# ============================================================

for _, account in payment_accounts.iterrows():

    account_id = account["Account_ID"]

    remaining_balance = account["Outstanding_Balance"]

    stage = account["Collection_Stage"]

    stage_payment_factor = {

        "Pre-Writeoff": {
            "kept":[0.85,0.95,1.00],
            "broken":(0.30,0.60),
            "direct_payment":0.18
        },

        "Primary": {
            "kept":[0.70,0.85,1.00],
            "broken":(0.20,0.50),
            "direct_payment":0.12
        },

        "Secondary": {
            "kept":[0.60,0.75,0.90],
            "broken":(0.15,0.40),
            "direct_payment":0.08
        },

        "Tertiary": {
            "kept":[0.50,0.65,0.80],
            "broken":(0.10,0.30),
            "direct_payment":0.05
        },

        "Warehouse": {
            "kept":[0.40,0.55,0.70],
            "broken":(0.05,0.20),
            "direct_payment":0.03
        }

    }

    # ---------------------------------------------
    # All promises for this account
    # ---------------------------------------------

    account_promises = ptp[
        ptp["Account_ID"] == account_id
    ].sort_values("Promise_Date")

    # ---------------------------------------------
    # Payments from kept promises
    # ---------------------------------------------

    for _, promise in account_promises.iterrows():

        status = promise["Promise_Status"]

        if status == "Active":
                continue

        elif status == "Broken":

        # 80% never pay
        # 20% eventually make a small payment

            if random.random() < 0.80:
                continue

        payment_factor = random.uniform(
            *stage_payment_factor[stage]["broken"]
        )

    else:
        # Kept

        payment_factor = random.choice(
            stage_payment_factor[stage]["kept"]
        )

        if remaining_balance <= 0:
            break

        num_payments = random.choices(
            [1,2,3],
            weights=[70,20,10],
            k=1
        )[0]

        if status == "Kept":

            payment_date = (
                promise["Promise_Due_Date"]
                +
                timedelta(days=random.randint(-1,2))
            )
            # Never allow payment before the promise date
            payment_date = max(
                 payment_date,
                 promise["Promise_Date"]
            )

        else:

            payment_date = (
                promise["Promise_Due_Date"]
                +
                timedelta(days=random.randint(10,45))
            )

        for payment_no in range(num_payments):

            if remaining_balance <= 0:
                break

            if payment_no == num_payments - 1:

                target_amount = promise["Promised_Amount"] * payment_factor

                payment_amount = min(
                    remaining_balance,
                    target_amount
                )

            else:

                payment_amount = round(

                    min(
                        remaining_balance,
                        promise["Promised_Amount"]
                    )

                    *

                    random.uniform(0.25,0.60),

                    2

                )

            remaining_balance -= payment_amount

            payment_method = random.choices(

                payment_methods,

                weights=payment_method_weights,

                k=1

            )[0]

            payment_date += timedelta(
                days=random.randint(0,15)
            )

            payment_records.append({

                "Payment_ID": payment_id,

                "Account_ID": account_id,

                "Promise_ID": promise["Promise_ID"],

                "Payment_Date": payment_date.date(),

                "Payment_Amount": round(payment_amount,2),

                "Payment_Method": payment_method

            })

            payment_id += 1

    # ---------------------------------------------
    # Direct Payments
    # ---------------------------------------------

    if remaining_balance > 0:

        account_calls = calls[

            (calls["Account_ID"] == account_id)

            &

            (calls["Dial_Result"] == "Right Party Contact")

            &

            (~calls["Call_ID"].isin(account_promises["Call_ID"]))

        ]

        for _, call in account_calls.iterrows():

            if remaining_balance <= 0:
                break

            if random.random() > stage_payment_factor[stage]["direct_payment"]:
                continue

            payment_amount = round(

                remaining_balance

                *

                random.uniform(0.15,0.40),

                2

            )

            remaining_balance -= payment_amount

            payment_method = random.choices(

                payment_methods,

                weights=payment_method_weights,

                k=1

            )[0]

            payment_records.append({

                "Payment_ID": payment_id,

                "Account_ID": account_id,

                "Promise_ID": np.nan,

                "Payment_Date": (
                    call["Call_Date"]
                    +
                    timedelta(days=random.randint(0,7))
                ).date(),

                "Payment_Amount": round(payment_amount,2),

                "Payment_Method": payment_method

            })

            payment_id += 1

# Keep the original Accounts table unchanged.
# remaining_balance is used only during payment generation.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create DataFrame
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

payments = pd.DataFrame(payment_records)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Sort Records
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

payments = payments.sort_values(

    by=[

        "Account_ID",

        "Payment_Date"

    ]

).reset_index(drop=True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Validation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("=" * 60)

print("PAYMENTS SUMMARY")

print("=" * 60)

print(f"Total Payments : {len(payments):,}")

print()

print("Payment Methods")

print(

    payments["Payment_Method"]

    .value_counts()

)

print()

print("Average Payment")

print(

    round(

        payments["Payment_Amount"].mean(),

        2

    )

)

print()

print("Payments with Promise")

print(

    payments["Promise_ID"]

    .notna()

    .sum()

)

print()

print("Direct Payments")

print(

    payments["Promise_ID"]

    .isna()

    .sum()

)

print("=" * 60)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

os.makedirs(

    "data/generated",

    exist_ok=True

)

# accounts.to_csv(
#     "data/generated/Accounts.csv",
#     index=False
# )

payments.to_csv(

    "data/generated/Payments.csv",

    index=False

)

print()

print("Payments.csv generated successfully.")

print()

print(payments.head(10))