import pandas as pd
from sqlalchemy import create_engine

# =====================================================
# SQL Server Connection
# =====================================================

server = r"DESKTOP-0U5Q1OP\SQLEXPRESS"
database = "NovaCollectionsDB"

connection_string = (
    f"mssql+pyodbc://@{server}/{database}"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&trusted_connection=yes"
    "&TrustServerCertificate=yes"
)

engine = create_engine(connection_string)

# =====================================================
# Load Tables
# =====================================================

tables = [

    ("Accounts", "data/generated/Accounts.csv"),

    ("Phone_Numbers", "data/generated/Phone_Numbers.csv"),

    ("Call_Interactions", "data/generated/Call_Interactions.csv"),

    ("Promise_To_Pay", "data/generated/Promise_To_Pay.csv"),

    ("Payments", "data/generated/Payments.csv")

]

# =====================================================
# Import
# =====================================================

for table_name, csv_file in tables:

    print(f"Loading {table_name}...")

    df = pd.read_csv(csv_file)

    df.to_sql(
        table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=100
)

    print(f"{len(df):,} rows inserted.")

print("\nAll tables imported successfully.")