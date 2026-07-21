# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOVATEL COLLECTIONS FRAMEWORK
# Generate Call Interactions
# Import libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import pandas as pd
import numpy as np
import random
import os
from datetime import timedelta

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Configuration
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

random.seed(42)
np.random.seed(42)

# Number of days after RPC before another call
RPC_GAP = 7

# Gap after unsuccessful attempts
MIN_GAP = 1
MAX_GAP = 4

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load Data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

accounts = pd.read_csv("data/generated/Accounts.csv")
phones = pd.read_csv("data/generated/Phone_Numbers.csv")

# Convert date columns

accounts["Placement_Date"] = pd.to_datetime(accounts["Placement_Date"])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Call Attempt Ranges
# Based on Collection Stage
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

call_attempts = {

    "Pre-Writeoff": (4, 8),

    "Primary": (8, 15),

    "Secondary": (14, 24),

    "Tertiary": (22, 34),

    "Warehouse": (28, 42)

}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Dial Result Probabilities
# By Collection Stage
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

dial_probability = {

    "Pre-Writeoff": {
        "Right Party Contact": 55,
        "No Answer": 22,
        "Voicemail": 13,
        "Busy": 10
    },

    "Primary": {
        "Right Party Contact": 45,
        "No Answer": 28,
        "Voicemail": 17,
        "Busy": 10
    },

    "Secondary": {
        "Right Party Contact": 33,
        "No Answer": 38,
        "Voicemail": 19,
        "Busy": 10
    },

    "Tertiary": {
        "Right Party Contact": 22,
        "No Answer": 47,
        "Voicemail": 21,
        "Busy": 10
    },

    "Warehouse": {
        "Right Party Contact": 12,
        "No Answer": 55,
        "Voicemail": 23,
        "Busy": 10
    }

}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# RPC Dispositions
# By Collection Stage
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

rpc_disposition_probability = {

    "Pre-Writeoff": {
        "Promise To Pay": 65,
        "Callback Requested": 15,
        "Settlement Requested": 2,
        "General Discussion": 15,
        "Refused To Pay": 3
    },

    "Primary": {
        "Promise To Pay": 50,
        "Callback Requested": 18,
        "Settlement Requested": 5,
        "General Discussion": 17,
        "Refused To Pay": 10
    },

    "Secondary": {
        "Promise To Pay": 32,
        "Callback Requested": 18,
        "Settlement Requested": 15,
        "General Discussion": 18,
        "Refused To Pay": 17
    },

    "Tertiary": {
        "Promise To Pay": 18,
        "Callback Requested": 15,
        "Settlement Requested": 30,
        "General Discussion": 12,
        "Refused To Pay": 25
    },

    "Warehouse": {
        "Promise To Pay": 6,
        "Callback Requested": 8,
        "Settlement Requested": 45,
        "General Discussion": 6,
        "Refused To Pay": 35
    }

}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Call Time Windows
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

call_time_slots = [

    "08:00",

    "09:00",

    "10:00",

    "11:00",

    "13:00",

    "15:00",

    "17:00",

    "19:00"

]

call_time_weights = [

    20,

    15,

    12,

    13,

    12,

    10,

    10,

    8

]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Helper Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def choose_phone(account_phones):

    """
    Select a phone using Preferred Dial Order
    """

    weights = []

    for _, phone in account_phones.iterrows():

        order = phone["Preferred_Dial_Order"]

        if order == 1:

            weights.append(60)

        elif order == 2:

            weights.append(25)

        elif order == 3:

            weights.append(10)

        else:

            weights.append(5)

    return account_phones.sample(
        n=1,
        weights=weights
    ).iloc[0]


def get_dial_result(phone_status, stage):

    if phone_status == "Disconnected":
        return "Disconnected"

    probabilities = dial_probability[stage]

    return random.choices(

        list(probabilities.keys()),

        weights=list(probabilities.values()),

        k=1

    )[0]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Begin Simulation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

call_records = []

call_id = 1

for _, account in accounts.iterrows():

    account_id = account["Account_ID"]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Skip Non-Dialable Accounts
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if account["Bankruptcy_Flag"] == 1:

        continue

    if account["Fraud_Flag"] == 1:

        continue

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Get Eligible Phones
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    account_phones = phones[
        phones["Account_ID"] == account_id
    ]

    account_phones = account_phones[
        ~account_phones["Phone_Status"].isin(
            [
                "Wrong Party",
                "Invalid"
            ]
        )
    ]

    if account_phones.empty:

        continue

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Number of Historical Calls
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    stage = account["Collection_Stage"]

    min_calls, max_calls = call_attempts[stage]

    days_in_inventory = (
        pd.Timestamp.today().normalize()
        - account["Placement_Date"]
    ).days

    base_calls = random.randint(min_calls, max_calls)

    # Older accounts tend to accumulate more historical attempts
    total_calls = min(
        base_calls + (days_in_inventory // 45),
        max_calls
    )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # First Call Date
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    current_call_date = (

        account["Placement_Date"]

        + timedelta(
            days=random.randint(0,3)
        )

    )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Begin Call History
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    for attempt in range(total_calls):
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Select Phone Number
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        selected_phone = choose_phone(account_phones)

        phone_id = selected_phone["Phone_ID"]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Call Time
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        call_time = random.choices(
            call_time_slots,
            weights=call_time_weights,
            k=1
        )[0]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Dial Result
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        dial_result = get_dial_result(
            selected_phone["Phone_Status"],
            stage
        )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Default Values
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        talk_time = 0

        disposition = None

        promise_to_pay = 0

        callback_requested = 0

        settlement_requested = 0

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # If Right Party Contact
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        if dial_result == "Right Party Contact":

            talk_time = random.randint(45, 900)

            probabilities = rpc_disposition_probability[stage]

            disposition = random.choices(

                list(probabilities.keys()),

                weights=list(probabilities.values()),

                k=1

            )[0]

            if disposition == "Promise To Pay":

                promise_to_pay = 1

            elif disposition == "Callback Requested":

                callback_requested = 1

            elif disposition == "Settlement Requested":

                settlement_requested = 1

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Append Call Record
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        call_records.append({

            "Call_ID": call_id,

            "Account_ID": account_id,

            "Phone_ID": phone_id,

            "Call_Date": current_call_date.date(),

            "Call_Time": call_time,

            "Dial_Result": dial_result,

            "Talk_Time_Seconds": talk_time,

            "Agent_Disposition": disposition,

            "Promise_To_Pay": promise_to_pay,

            "Callback_Requested": callback_requested,

            "Settlement_Requested": settlement_requested

        })

        call_id += 1

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Timeline Logic
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        if dial_result == "Right Party Contact":

            current_call_date += timedelta(days=RPC_GAP)

        else:

            current_call_date += timedelta(
                days=random.randint(
                    MIN_GAP,
                    MAX_GAP
                )
            )
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Remove Disconnected Numbers from Future Dialing
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        if dial_result == "Disconnected":

            account_phones = account_phones[
                account_phones["Phone_ID"] != phone_id
            ]

            if account_phones.empty:
                break

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# End of Account Loop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create DataFrame
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

call_interactions = pd.DataFrame(call_records)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Sort Records
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

call_interactions = call_interactions.sort_values(

    by=[
        "Account_ID",
        "Call_Date",
        "Call_Time"
    ]

).reset_index(drop=True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Validation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("=" * 50)

print("Call Interaction Summary")

print("=" * 50)

print(f"Accounts           : {accounts['Account_ID'].nunique()}")

print(f"Phone Numbers      : {phones['Phone_ID'].nunique()}")

print(f"Call Records       : {len(call_interactions):,}")

print()

print("Dial Result Distribution")

print(call_interactions["Dial_Result"].value_counts())

print()

print("Disposition Distribution")

print(

    call_interactions["Agent_Disposition"]

    .fillna("None")

    .value_counts()

)

print()

print("Average Talk Time (RPC Only)")

rpc = call_interactions[
    call_interactions["Dial_Result"] == "Right Party Contact"
]

if len(rpc):

    print(round(rpc["Talk_Time_Seconds"].mean(),2),"seconds")

else:

    print("No RPC generated")

print("=" * 50)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

os.makedirs(
    "data/generated",
    exist_ok=True
)

call_interactions.to_csv(

    "data/generated/Call_Interactions.csv",

    index=False

)

print()

print("Call_Interactions.csv generated successfully.")

print(call_interactions.head(10))

print(call_interactions.shape)