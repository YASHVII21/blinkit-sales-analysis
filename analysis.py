import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# Connect to MySQL
# ─────────────────────────────────────────
engine = create_engine("mysql+mysqlconnector://root:root123@localhost/blinkit_db")
print("✅ Connected to MySQL - blinkit_db")
print("=" * 60)

plt.rcParams['figure.figsize'] = (10, 5)
sns.set_theme(style="whitegrid")
BLINKIT_GREEN  = "#0C831F"
BLINKIT_YELLOW = "#F9C62B"

# ─────────────────────────────────────────
# 1. Sales by Outlet Type
# ─────────────────────────────────────────
query1 = text("""
    SELECT Outlet_Type,
           ROUND(SUM(Item_Outlet_Sales), 2) AS total_sales,
           ROUND(AVG(Item_Outlet_Sales), 2) AS avg_sales
    FROM grocery_sales
    GROUP BY Outlet_Type
    ORDER BY total_sales DESC
""")
df1 = pd.read_sql(query1, engine)
print("1. Sales by Outlet Type")
print(df1.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].bar(df1['Outlet_Type'], df1['total_sales'], color=BLINKIT_GREEN)
axes[0].set_title('Total Sales by Outlet Type', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Outlet Type')
axes[0].set_ylabel('Total Sales (₹)')
axes[0].tick_params(axis='x', rotation=15)
axes[1].bar(df1['Outlet_Type'], df1['avg_sales'], color=BLINKIT_YELLOW, edgecolor='gray')
axes[1].set_title('Average Sales by Outlet Type', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Outlet Type')
axes[1].set_ylabel('Avg Sales (₹)')
axes[1].tick_params(axis='x', rotation=15)
plt.tight_layout()
plt.savefig('1_sales_by_outlet_type.png', dpi=150)
plt.show()
print("✅ Chart saved: 1_sales_by_outlet_type.png\n")

# ─────────────────────────────────────────
# 2. Top 10 Item Types by Sales
# ─────────────────────────────────────────
query2 = text("""
    SELECT Item_Type,
           ROUND(SUM(Item_Outlet_Sales), 2) AS total_sales,
           COUNT(*) AS item_count
    FROM grocery_sales
    GROUP BY Item_Type
    ORDER BY total_sales DESC
    LIMIT 10
""")
df2 = pd.read_sql(query2, engine)
print("2. Top 10 Item Types by Sales")
print(df2.to_string(index=False))

plt.figure(figsize=(12, 5))
sns.barplot(data=df2, x='total_sales', y='Item_Type', palette='YlGn_r')
plt.title('Top 10 Item Types by Total Sales', fontsize=13, fontweight='bold')
plt.xlabel('Total Sales (₹)')
plt.ylabel('Item Type')
plt.tight_layout()
plt.savefig('2_top_item_types.png', dpi=150)
plt.show()
print("✅ Chart saved: 2_top_item_types.png\n")

# ─────────────────────────────────────────
# 3. Sales by Outlet Location Tier
# ─────────────────────────────────────────
query3 = text("""
    SELECT Outlet_Location_Type,
           ROUND(SUM(Item_Outlet_Sales), 2) AS total_sales,
           COUNT(*) AS item_count
    FROM grocery_sales
    GROUP BY Outlet_Location_Type
    ORDER BY total_sales DESC
""")
df3 = pd.read_sql(query3, engine)
print("3. Sales by Location Tier")
print(df3.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].pie(df3['total_sales'], labels=df3['Outlet_Location_Type'],
            autopct='%1.1f%%', colors=[BLINKIT_GREEN, BLINKIT_YELLOW, '#4CAF50'],
            startangle=140)
axes[0].set_title('Revenue Share by Location Tier', fontsize=13, fontweight='bold')
axes[1].bar(df3['Outlet_Location_Type'], df3['item_count'], color=BLINKIT_GREEN)
axes[1].set_title('Item Count by Location Tier', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Location Tier')
axes[1].set_ylabel('Number of Items')
plt.tight_layout()
plt.savefig('3_sales_by_location.png', dpi=150)
plt.show()
print("✅ Chart saved: 3_sales_by_location.png\n")

# ─────────────────────────────────────────
# 4. Price Bucket Analysis
# ─────────────────────────────────────────
query4 = text("""
    SELECT 
        CASE 
            WHEN Item_MRP < 50 THEN 'Budget (<50)'
            WHEN Item_MRP BETWEEN 50 AND 150 THEN 'Mid-range (50-150)'
            WHEN Item_MRP BETWEEN 150 AND 250 THEN 'Premium (150-250)'
            ELSE 'Luxury (>250)'
        END AS price_bucket,
        COUNT(*) AS item_count,
        ROUND(AVG(Item_Outlet_Sales), 2) AS avg_sales,
        ROUND(SUM(Item_Outlet_Sales), 2) AS total_sales
    FROM grocery_sales
    GROUP BY price_bucket
    ORDER BY total_sales DESC
""")
df4 = pd.read_sql(query4, engine)
print("4. Price Bucket Analysis")
print(df4.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].bar(df4['price_bucket'], df4['total_sales'], color=BLINKIT_YELLOW, edgecolor='gray')
axes[0].set_title('Total Sales by Price Bucket', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Price Range')
axes[0].set_ylabel('Total Sales (₹)')
axes[0].tick_params(axis='x', rotation=10)
for bar in axes[0].patches:
    axes[0].annotate(f'₹{bar.get_height()/1e6:.1f}M',
                     xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                     ha='center', va='bottom', fontsize=9)
axes[1].bar(df4['price_bucket'], df4['avg_sales'], color=BLINKIT_GREEN)
axes[1].set_title('Avg Sales by Price Bucket', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Price Range')
axes[1].set_ylabel('Avg Sales (₹)')
axes[1].tick_params(axis='x', rotation=10)
for bar in axes[1].patches:
    axes[1].annotate(f'₹{bar.get_height():.0f}',
                     xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                     ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig('4_price_bucket_analysis.png', dpi=150)
plt.show()
print("✅ Chart saved: 4_price_bucket_analysis.png\n")

# ─────────────────────────────────────────
# 5. Fat Content vs Sales
# ─────────────────────────────────────────
query5 = text("""
    SELECT Item_Fat_Content,
           COUNT(*) AS item_count,
           ROUND(AVG(Item_Outlet_Sales), 2) AS avg_sales,
           ROUND(SUM(Item_Outlet_Sales), 2) AS total_sales
    FROM grocery_sales
    GROUP BY Item_Fat_Content
    ORDER BY total_sales DESC
""")
df5 = pd.read_sql(query5, engine)
print("5. Fat Content vs Sales")
print(df5.to_string(index=False))

plt.figure(figsize=(8, 5))
sns.barplot(data=df5, x='Item_Fat_Content', y='avg_sales', palette='Greens_d')
plt.title('Average Sales by Fat Content', fontsize=13, fontweight='bold')
plt.xlabel('Fat Content')
plt.ylabel('Avg Sales (₹)')
plt.tight_layout()
plt.savefig('5_fat_content_sales.png', dpi=150)
plt.show()
print("✅ Chart saved: 5_fat_content_sales.png\n")

# ─────────────────────────────────────────
# 6. Outlet Establishment Year Trend
# ─────────────────────────────────────────
query6 = text("""
    SELECT Outlet_Establishment_Year,
           ROUND(SUM(Item_Outlet_Sales), 2) AS total_sales,
           COUNT(DISTINCT Outlet_Identifier) AS num_outlets
    FROM grocery_sales
    GROUP BY Outlet_Establishment_Year
    ORDER BY Outlet_Establishment_Year
""")
df6 = pd.read_sql(query6, engine)
print("6. Sales Trend by Outlet Establishment Year")
print(df6.to_string(index=False))

fig, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(df6['Outlet_Establishment_Year'], df6['total_sales'],
         color=BLINKIT_GREEN, marker='o', linewidth=2, label='Total Sales')
ax1.set_xlabel('Establishment Year')
ax1.set_ylabel('Total Sales (₹)', color=BLINKIT_GREEN)
ax2 = ax1.twinx()
ax2.bar(df6['Outlet_Establishment_Year'], df6['num_outlets'],
        alpha=0.3, color=BLINKIT_YELLOW, label='No. of Outlets')
ax2.set_ylabel('Number of Outlets', color='gray')
plt.title('Sales Trend by Outlet Establishment Year', fontsize=13, fontweight='bold')
fig.tight_layout()
plt.savefig('6_establishment_year_trend.png', dpi=150)
plt.show()
print("✅ Chart saved: 6_establishment_year_trend.png\n")

# ─────────────────────────────────────────
# 7. CTE: Category Revenue Contribution
# ─────────────────────────────────────────
query7 = text("""
    WITH category_sales AS (
        SELECT Item_Type,
               ROUND(SUM(Item_Outlet_Sales), 2) AS category_total
        FROM grocery_sales
        GROUP BY Item_Type
    ),
    total AS (
        SELECT ROUND(SUM(Item_Outlet_Sales), 2) AS grand_total FROM grocery_sales
    )
    SELECT cs.Item_Type,
           cs.category_total,
           ROUND((cs.category_total / t.grand_total) * 100, 2) AS revenue_pct
    FROM category_sales cs
    CROSS JOIN total t
    ORDER BY revenue_pct DESC
    LIMIT 8
""")
df7 = pd.read_sql(query7, engine)
print("7. Category Revenue Contribution %")
print(df7.to_string(index=False))

plt.figure(figsize=(10, 5))
sns.barplot(data=df7, x='revenue_pct', y='Item_Type', palette='YlGn_r')
plt.title('Category Revenue Contribution (%)', fontsize=13, fontweight='bold')
plt.xlabel('Revenue Contribution (%)')
plt.ylabel('Item Type')
plt.tight_layout()
plt.savefig('7_category_contribution.png', dpi=150)
plt.show()
print("✅ Chart saved: 7_category_contribution.png\n")

# ─────────────────────────────────────────
# 8. Outlet Size Performance
# ─────────────────────────────────────────
query8 = text("""
    SELECT Outlet_Size,
           ROUND(SUM(Item_Outlet_Sales), 2) AS total_sales,
           COUNT(*) AS item_count
    FROM grocery_sales
    WHERE Outlet_Size IS NOT NULL AND Outlet_Size != ''
    GROUP BY Outlet_Size
    ORDER BY total_sales DESC
""")
df8 = pd.read_sql(query8, engine)
print("8. Outlet Size Performance")
print(df8.to_string(index=False))

plt.figure(figsize=(8, 5))
plt.bar(df8['Outlet_Size'], df8['total_sales'], color=BLINKIT_GREEN)
plt.title('Total Sales by Outlet Size', fontsize=13, fontweight='bold')
plt.xlabel('Outlet Size')
plt.ylabel('Total Sales (₹)')
plt.tight_layout()
plt.savefig('8_outlet_size_performance.png', dpi=150)
plt.show()
print("✅ Chart saved: 8_outlet_size_performance.png\n")

# ─────────────────────────────────────────
# 9. Window Function: Rank outlets by sales within each location
# ─────────────────────────────────────────
query9 = text("""
    SELECT 
        Outlet_Identifier,
        Outlet_Location_Type,
        Outlet_Type,
        ROUND(SUM(Item_Outlet_Sales), 2) AS total_sales,
        RANK() OVER (PARTITION BY Outlet_Location_Type ORDER BY SUM(Item_Outlet_Sales) DESC) AS sales_rank
    FROM grocery_sales
    GROUP BY Outlet_Identifier, Outlet_Location_Type, Outlet_Type
    ORDER BY Outlet_Location_Type, sales_rank
""")
df9 = pd.read_sql(query9, engine)
print("9. Outlet Rankings within each Location Tier (Window Function)")
print(df9.to_string(index=False))

# ─────────────────────────────────────────
# 10. CTE: Above vs Below Average Outlets
# ─────────────────────────────────────────
query10 = text("""
    WITH outlet_sales AS (
        SELECT 
            Outlet_Identifier,
            Outlet_Type,
            Outlet_Location_Type,
            ROUND(AVG(Item_Outlet_Sales), 2) AS avg_sales
        FROM grocery_sales
        GROUP BY Outlet_Identifier, Outlet_Type, Outlet_Location_Type
    ),
    overall_avg AS (
        SELECT ROUND(AVG(Item_Outlet_Sales), 2) AS overall_avg FROM grocery_sales
    )
    SELECT 
        o.Outlet_Identifier,
        o.Outlet_Type,
        o.avg_sales,
        oa.overall_avg,
        CASE WHEN o.avg_sales > oa.overall_avg THEN 'Above Average' ELSE 'Below Average' END AS performance
    FROM outlet_sales o
    CROSS JOIN overall_avg oa
    ORDER BY o.avg_sales DESC
""")
df10 = pd.read_sql(query10, engine)
print("\n10. Outlet Performance vs Overall Average (CTE)")
print(df10.to_string(index=False))

above = len(df10[df10['performance'] == 'Above Average'])
below = len(df10[df10['performance'] == 'Below Average'])
plt.figure(figsize=(6, 5))
plt.bar(['Above Average', 'Below Average'], [above, below],
        color=[BLINKIT_GREEN, '#e74c3c'])
plt.title('Outlets: Above vs Below Average Sales', fontsize=13, fontweight='bold')
plt.ylabel('Number of Outlets')
plt.tight_layout()
plt.savefig('9_outlet_performance.png', dpi=150)
plt.show()
print("✅ Chart saved: 9_outlet_performance.png\n")

# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
print("=" * 60)
print("🎉 ALL ANALYSIS COMPLETE!")
print("=" * 60)

with engine.connect() as conn:
    total_sales = conn.execute(text("SELECT ROUND(SUM(Item_Outlet_Sales),2) FROM grocery_sales")).scalar()
    total_items = conn.execute(text("SELECT COUNT(*) FROM grocery_sales")).scalar()
    top_outlet  = conn.execute(text("""
        SELECT Outlet_Type FROM grocery_sales 
        GROUP BY Outlet_Type ORDER BY SUM(Item_Outlet_Sales) DESC LIMIT 1
    """)).scalar()
    top_item = conn.execute(text("""
        SELECT Item_Type FROM grocery_sales 
        GROUP BY Item_Type ORDER BY SUM(Item_Outlet_Sales) DESC LIMIT 1
    """)).scalar()
    overall_avg = conn.execute(text("SELECT ROUND(AVG(Item_Outlet_Sales),2) FROM grocery_sales")).scalar()

print(f"\n  💰 Total Revenue Analysed : ₹{total_sales:,}")
print(f"  📦 Total Records          : {total_items:,}")
print(f"  🏪 Best Outlet Type       : {top_outlet}")
print(f"  🛒 Best Selling Category  : {top_item}")
print(f"  📊 Overall Avg Sale Value : ₹{overall_avg}")
# Add at the very end of analysis.py

summary = pd.DataFrame({
    'Metric': [
        'Total Revenue',
        'Total Records',
        'Overall Avg Sale Value',
        'Best Outlet Type',
        'Best Selling Category',
        'Top Location Tier'
    ],
    'Value': [
        f'₹{total_sales:,}',
        f'{total_items:,}',
        f'₹{overall_avg}',
        top_outlet,
        top_item,
        'Tier 3'
    ]
})

summary.to_csv('business_summary.csv', index=False)
print("✅ Summary exported: business_summary.csv")
