# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import Libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import pandas as pd
import numpy as np
import random
from faker import Faker
import os

fake = Faker("en_US")

random.seed(42)
np.random.seed(42)
Faker.seed(42)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load Accounts Table
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

accounts = pd.read_csv("data/generated/Accounts.csv")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create Empty List
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

phone_records = []

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create Phone IDs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

phone_id = 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Loop through every account
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

for _, account in accounts.iterrows():

    account_id = account["Account_ID"]

    num_phones = random.choices(
    [2, 3, 4, 5],
    weights=[20, 45, 25, 10],
    k=1
)[0]

    for order in range(1, num_phones + 1):

        phone_number = fake.numerify("##########")

        # Phone Source
        phone_source = random.choices(
            ["Client", "Credit Bureau", "Skip Trace", "Customer Provided"],
            weights=[50,30,15,5],
            k=1
        )[0]

        # Phone Type
        phone_type = random.choices(
            ["Mobile","Home","Work","Landline"],
            weights=[70,10,10,10],
            k=1
        )[0]

        verification_probability = {
            "Client":0.90,
            "Credit Bureau":0.70,
            "Skip Trace":0.50,
            "Customer Provided":0.98
        }

        is_verified = random.random() < verification_probability[phone_source]

        is_dnc = random.random() < 0.02

        phone_status = random.choices(
            ["Active","Disconnected","Wrong Party","Invalid"],
            weights=[85,7,5,3],
            k=1
        )[0]

        date_added = account["Placement_Date"]

        phone_records.append({

            "Phone_ID": phone_id,

            "Account_ID": account_id,

            "Phone_Number": phone_number,

            "Phone_Source": phone_source,

            "Phone_Type": phone_type,

            "Is_Primary": 1 if order == 1 else 0,

            "Is_Verified": int(is_verified),

            "Is_DNC": int(is_dnc),

            "Date_Added": date_added,

            "Phone_Status": phone_status,

            "Preferred_Dial_Order": order

        })

        phone_id += 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Convert to DataFrame
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print(f"Generated {len(phone_records)} phone records.")
phones = pd.DataFrame(phone_records)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

os.makedirs("data/generated", exist_ok=True)

phones.to_csv(
    "data/generated/Phone_Numbers.csv",
    index=False
)

#print(phones.head())

print(len(phones))

print(
    phones.groupby("Account_ID")
          .size()
          .describe()
)

print(
    phones.groupby("Account_ID")["Is_Primary"]
          .sum()
          .value_counts()
)

print(
    phones["Phone_Number"].duplicated().sum()
)

print(
    phones["Phone_Status"]
          .value_counts(normalize=True)
          .round(3)
)