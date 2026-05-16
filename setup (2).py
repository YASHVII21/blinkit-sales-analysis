import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

# Load and clean the dataset
df = pd.read_csv("blinkit data set.csv")

df['Item_Fat_Content'] = df['Item_Fat_Content'].replace({
    'LF': 'Low Fat', 'low fat': 'Low Fat', 'reg': 'Regular'
})
df['Item_Weight'].fillna(df['Item_Weight'].median(), inplace=True)
df['Outlet_Size'].fillna('Unknown', inplace=True)

df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace(r"[^a-zA-Z0-9_]", "", regex=True)

print("CSV loaded. Columns:")
print(df.columns.tolist())
print(f"\nTotal rows: {len(df)}")

# Create database
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
print("\nDatabase 'blinkit_db' ready")

# Load data into MySQL
engine = create_engine("mysql+mysqlconnector://root:root123@localhost/blinkit_db")
df.to_sql("grocery_sales", con=engine, if_exists="replace", index=False)
print("Data loaded into 'grocery_sales'")
print("Setup done. Run analysis.py next.")
