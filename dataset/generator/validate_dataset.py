# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOVATEL COLLECTIONS FRAMEWORK
# DATASET VALIDATION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import pandas as pd

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOAD DATA
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

accounts = pd.read_csv("data/generated/Accounts.csv")
phones = pd.read_csv("data/generated/Phone_Numbers.csv")
calls = pd.read_csv("data/generated/Call_Interactions.csv")
ptp = pd.read_csv("data/generated/Promise_To_Pay.csv")
payments = pd.read_csv("data/generated/Payments.csv")

accounts["Placement_Date"] = pd.to_datetime(accounts["Placement_Date"])
accounts["Charge_Off_Date"] = pd.to_datetime(accounts["Charge_Off_Date"])
accounts["Last_Payment_Date"] = pd.to_datetime(accounts["Last_Payment_Date"])

calls["Call_Date"] = pd.to_datetime(calls["Call_Date"])

ptp["Promise_Date"] = pd.to_datetime(ptp["Promise_Date"])
ptp["Promise_Due_Date"] = pd.to_datetime(ptp["Promise_Due_Date"])

payments["Payment_Date"] = pd.to_datetime(payments["Payment_Date"])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# VALIDATION UTILITIES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

passed = 0
failed = 0

def validate(name, condition):

    global passed
    global failed

    if condition:
        print(f"[PASS] {name}")
        passed += 1
    else:
        print(f"[FAIL] {name}")
        failed += 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ACCOUNTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\n========== ACCOUNTS ==========")

validate(
    "Unique Account_ID",
    accounts["Account_ID"].is_unique
)

validate(
    "Unique Account_Number",
    accounts["Account_Number"].is_unique
)

validate(
    "Positive Original Balance",
    (accounts["Original_Balance"] > 0).all()
)

validate(
    "Outstanding Balance >= 0",
    (accounts["Outstanding_Balance"] >= 0).all()
)

validate(
    "Outstanding <= Original Balance",
    (
        accounts["Outstanding_Balance"]
        <=
        accounts["Original_Balance"]
    ).all()
)

validate(
    "Credit Score Between 300-850",
    accounts["Credit_Score"].between(300,850).all()
)

validate(
    "Placement After Charge Off",
    (accounts["Placement_Date"] >= accounts["Charge_Off_Date"]).all()
)

validate(
    "Positive Days Past Due",
    (accounts["Days_Past_Due"] > 0).all()
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PHONE NUMBERS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\n========== PHONE NUMBERS ==========")

validate(
    "Unique Phone_ID",
    phones["Phone_ID"].is_unique
)

validate(
    "All Account_ID Exist",
    phones["Account_ID"].isin(accounts["Account_ID"]).all()
)

primary = phones.groupby("Account_ID")["Is_Primary"].sum()

validate(
    "One Primary Phone Per Account",
    (primary == 1).all()
)

validate(
    "Every Account Has Phone",
    phones["Account_ID"].nunique() == accounts["Account_ID"].nunique()
)

duplicate_order = phones.duplicated(
    subset=["Account_ID","Preferred_Dial_Order"]
).sum()

validate(
    "Unique Dial Order Per Account",
    duplicate_order == 0
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CALL INTERACTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\n========== CALL INTERACTIONS ==========")

validate(
    "Unique Call_ID",
    calls["Call_ID"].is_unique
)

validate(
    "Call Account Exists",
    calls["Account_ID"].isin(accounts["Account_ID"]).all()
)

validate(
    "Call Phone Exists",
    calls["Phone_ID"].isin(phones["Phone_ID"]).all()
)

merged = calls.merge(
    accounts[["Account_ID","Placement_Date"]],
    on="Account_ID"
)

validate(
    "Call Date After Placement",
    (merged["Call_Date"] >= merged["Placement_Date"]).all()
)

non_rpc = calls[calls["Dial_Result"] != "Right Party Contact"]

validate(
    "Talk Time Zero For Non RPC",
    (non_rpc["Talk_Time_Seconds"] == 0).all()
)

validate(
    "Disposition Null For Non RPC",
    non_rpc["Agent_Disposition"].isna().all()
)

ptp_check = calls[
    calls["Promise_To_Pay"] == 1
]

validate(
    "PTP Flag Matches Disposition",
    (ptp_check["Agent_Disposition"] == "Promise To Pay").all()
)

callback_check = calls[
    calls["Callback_Requested"] == 1
]

validate(
    "Callback Flag Matches Disposition",
    (callback_check["Agent_Disposition"] == "Callback Requested").all()
)

settlement_check = calls[
    calls["Settlement_Requested"] == 1
]

validate(
    "Settlement Flag Matches Disposition",
    (settlement_check["Agent_Disposition"] == "Settlement Requested").all()
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PROMISE TO PAY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\n========== PROMISE TO PAY ==========")

validate(
    "Unique Promise_ID",
    ptp["Promise_ID"].is_unique
)

validate(
    "Promise Account Exists",
    ptp["Account_ID"].isin(accounts["Account_ID"]).all()
)

validate(
    "Promise Call Exists",
    ptp["Call_ID"].isin(calls["Call_ID"]).all()
)

promise_merge = ptp.merge(
    calls[
        [
            "Call_ID",
            "Call_Date"
        ]
    ],
    on="Call_ID"
)

validate(
    "Promise After Call",
    (promise_merge["Promise_Date"] >= promise_merge["Call_Date"]).all()
)

validate(
    "Promise Due After Promise Date",
    (
        ptp["Promise_Due_Date"] >
        ptp["Promise_Date"]
    ).all()
)

validate(
    "Positive Promised Amount",
    (ptp["Promised_Amount"] > 0).all()
)

validate(
    "Accounts Have Multiple Promises",
    ptp.groupby("Account_ID").size().max() > 1
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PAYMENTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\n========== PAYMENTS ==========")

validate(
    "Unique Payment_ID",
    payments["Payment_ID"].is_unique
)

validate(
    "Payment Account Exists",
    payments["Account_ID"].isin(accounts["Account_ID"]).all()
)

payment_ptp = payments[
    payments["Promise_ID"].notna()
]

validate(
    "Promise_ID Exists",
    payment_ptp["Promise_ID"].isin(
        ptp["Promise_ID"]
    ).all()
)

payment_merge = payment_ptp.merge(
    ptp[
        [
            "Promise_ID",
            "Promise_Date",
            "Promise_Due_Date"
        ]
    ],
    on="Promise_ID"
)

failed_payments = payment_merge[
    payment_merge["Payment_Date"] < payment_merge["Promise_Date"]
]

print(f"Failed Records: {len(failed_payments)}")

print(
    failed_payments[
        [
            "Promise_ID",
            "Account_ID",
            "Promise_Date",
            "Promise_Due_Date",
            "Payment_Date"
        ]
    ].head(20)
)
validate(
    "Payment On/After Promise Date",
    (
        payment_merge["Payment_Date"] >=
        payment_merge["Promise_Date"]
    ).all()
)

validate(
    "Positive Payment Amount",
    (payments["Payment_Amount"] > 0).all()
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FINANCIAL VALIDATION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Original Balance = Outstanding Balance + Payments
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# payment_totals = (
#     payments
#     .groupby("Account_ID")["Payment_Amount"]
#     .sum()
#     .reset_index()
# )

# financial_check = accounts.merge(
#     payment_totals,
#     on="Account_ID",
#     how="left"
# )

# financial_check["Payment_Amount"] = (
#     financial_check["Payment_Amount"]
#     .fillna(0)
# )

# financial_check["Difference"] = (
#     financial_check["Original_Balance"]
#     - (
#         financial_check["Outstanding_Balance"]
#         + financial_check["Payment_Amount"]
#     )
# ).round(2)

# validate(
#     "Original Balance = Outstanding Balance + Payments",
#     (financial_check["Difference"] == 0).all()
# )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SUMMARY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("\n" + "="*60)

print("NOVATEL DATASET VALIDATION")

print("="*60)

print(f"Passed : {passed}")

print(f"Failed : {failed}")

print(f"Total  : {passed+failed}")

if failed == 0:
    print("\nDATASET READY FOR SQL SERVER")
else:
    print("\nPLEASE FIX FAILED VALIDATIONS")

print("="*60)