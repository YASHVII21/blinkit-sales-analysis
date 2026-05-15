import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

# ─────────────────────────────────────────
# STEP 1: Load CSV
# ─────────────────────────────────────────
df = pd.read_csv("blinkit data set.csv")

df['Item_Fat_Content'] = df['Item_Fat_Content'].replace({
    'LF': 'Low Fat', 'low fat': 'Low Fat', 'reg': 'Regular'
})
df['Item_Weight'].fillna(df['Item_Weight'].median(), inplace=True)
df['Outlet_Size'].fillna('Unknown', inplace=True)

# Clean column names - remove spaces
df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace(r"[^a-zA-Z0-9_]", "", regex=True)

print("✅ CSV loaded. Columns found:")
print(df.columns.tolist())
print(f"\n✅ Total rows: {len(df)}")

# ─────────────────────────────────────────
# STEP 2: Create Database
# ─────────────────────────────────────────
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123"
)
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS blinkit_db;")
cursor.execute("USE blinkit_db;")
conn.commit()
cursor.close()
conn.close()
print("\n✅ Database 'blinkit_db' created successfully!")

# ─────────────────────────────────────────
# STEP 3: Load data into MySQL
# ─────────────────────────────────────────
engine = create_engine("mysql+mysqlconnector://root:root123@localhost/blinkit_db")
df.to_sql("grocery_sales", con=engine, if_exists="replace", index=False)
print("✅ Data loaded into MySQL table 'grocery_sales'!")
print("\n🚀 Setup complete! Now run analysis.py")
