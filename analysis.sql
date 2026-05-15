-- ================================================
-- BLINKIT GROCERY DATA - SQL ANALYSIS
-- Author: Yashvi Solanki
-- ================================================

USE blinkit_db;

-- ─────────────────────────────────────────
-- 1. BASIC DATA OVERVIEW
-- ─────────────────────────────────────────

-- Total number of records
SELECT COUNT(*) AS total_records FROM grocery_sales;

-- Unique item types
SELECT DISTINCT Item_Type FROM grocery_sales ORDER BY Item_Type;

-- Unique outlet types
SELECT DISTINCT Outlet_Type FROM grocery_sales;

-- ─────────────────────────────────────────
-- 2. SALES PERFORMANCE ANALYSIS
-- ─────────────────────────────────────────

-- Total and average sales by outlet type
SELECT 
    Outlet_Type,
    COUNT(*) AS total_items,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(AVG(Sales), 2) AS avg_sales
FROM grocery_sales
GROUP BY Outlet_Type
ORDER BY total_sales DESC;

-- Top 10 best selling item types
SELECT 
    Item_Type,
    COUNT(*) AS item_count,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(AVG(Sales), 2) AS avg_sales
FROM grocery_sales
GROUP BY Item_Type
ORDER BY total_sales DESC
LIMIT 10;

-- Sales by outlet location tier
SELECT 
    Outlet_Location_Type,
    COUNT(*) AS total_items,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(AVG(Sales), 2) AS avg_sales
FROM grocery_sales
GROUP BY Outlet_Location_Type
ORDER BY total_sales DESC;

-- ─────────────────────────────────────────
-- 3. OUTLET PERFORMANCE ANALYSIS
-- ─────────────────────────────────────────

-- Revenue by outlet size
SELECT 
    Outlet_Size,
    COUNT(*) AS total_items,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(AVG(Sales), 2) AS avg_sales
FROM grocery_sales
GROUP BY Outlet_Size
ORDER BY total_sales DESC;

-- Best performing outlets ranked by sales
SELECT 
    Outlet_Identifier,
    Outlet_Type,
    Outlet_Location_Type,
    Outlet_Size,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(AVG(Rating), 2) AS avg_rating
FROM grocery_sales
GROUP BY Outlet_Identifier, Outlet_Type, Outlet_Location_Type, Outlet_Size
ORDER BY total_sales DESC;

-- Outlets established by year and their performance
SELECT 
    Outlet_Establishment_Year,
    COUNT(DISTINCT Outlet_Identifier) AS num_outlets,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(AVG(Sales), 2) AS avg_sales
FROM grocery_sales
GROUP BY Outlet_Establishment_Year
ORDER BY Outlet_Establishment_Year;

-- ─────────────────────────────────────────
-- 4. PRODUCT & PRICING ANALYSIS
-- ─────────────────────────────────────────

-- Average MRP by item type
SELECT 
    Item_Type,
    ROUND(AVG(Item_MRP), 2) AS avg_mrp,
    ROUND(MIN(Item_MRP), 2) AS min_mrp,
    ROUND(MAX(Item_MRP), 2) AS max_mrp,
    ROUND(AVG(Sales), 2) AS avg_sales
FROM grocery_sales
GROUP BY Item_Type
ORDER BY avg_mrp DESC;

-- Fat content distribution and its impact on sales
SELECT 
    Item_Fat_Content,
    COUNT(*) AS item_count,
    ROUND(AVG(Sales), 2) AS avg_sales,
    ROUND(SUM(Sales), 2) AS total_sales
FROM grocery_sales
GROUP BY Item_Fat_Content
ORDER BY total_sales DESC;

-- Price range buckets vs sales performance
SELECT 
    CASE 
        WHEN Item_MRP < 50 THEN 'Budget (< 50)'
        WHEN Item_MRP BETWEEN 50 AND 150 THEN 'Mid-range (50-150)'
        WHEN Item_MRP BETWEEN 150 AND 250 THEN 'Premium (150-250)'
        ELSE 'Luxury (> 250)'
    END AS price_bucket,
    COUNT(*) AS item_count,
    ROUND(AVG(Sales), 2) AS avg_sales,
    ROUND(SUM(Sales), 2) AS total_sales
FROM grocery_sales
GROUP BY price_bucket
ORDER BY total_sales DESC;

-- ─────────────────────────────────────────
-- 5. CUSTOMER RATING ANALYSIS
-- ─────────────────────────────────────────

-- Average rating by outlet type
SELECT 
    Outlet_Type,
    ROUND(AVG(Rating), 2) AS avg_rating,
    COUNT(*) AS total_reviews
FROM grocery_sales
GROUP BY Outlet_Type
ORDER BY avg_rating DESC;

-- Rating distribution
SELECT 
    Rating,
    COUNT(*) AS count
FROM grocery_sales
GROUP BY Rating
ORDER BY Rating DESC;

-- High rated (>4) vs low rated outlets
SELECT 
    Outlet_Identifier,
    Outlet_Type,
    ROUND(AVG(Rating), 2) AS avg_rating,
    ROUND(SUM(Sales), 2) AS total_sales,
    CASE 
        WHEN AVG(Rating) >= 4 THEN 'High Performing'
        WHEN AVG(Rating) BETWEEN 3 AND 4 THEN 'Average'
        ELSE 'Needs Improvement'
    END AS performance_category
FROM grocery_sales
GROUP BY Outlet_Identifier, Outlet_Type
ORDER BY avg_rating DESC;

-- ─────────────────────────────────────────
-- 6. ADVANCED ANALYSIS - WINDOW FUNCTIONS & CTEs
-- ─────────────────────────────────────────

-- Running total of sales by outlet type using window function
SELECT 
    Outlet_Type,
    Item_Type,
    ROUND(SUM(Sales), 2) AS sales,
    ROUND(SUM(SUM(Sales)) OVER (PARTITION BY Outlet_Type ORDER BY Item_Type), 2) AS running_total
FROM grocery_sales
GROUP BY Outlet_Type, Item_Type
ORDER BY Outlet_Type, Item_Type;

-- Rank outlets within each location type by sales using RANK()
SELECT 
    Outlet_Identifier,
    Outlet_Location_Type,
    Outlet_Type,
    ROUND(SUM(Sales), 2) AS total_sales,
    RANK() OVER (PARTITION BY Outlet_Location_Type ORDER BY SUM(Sales) DESC) AS sales_rank
FROM grocery_sales
GROUP BY Outlet_Identifier, Outlet_Location_Type, Outlet_Type
ORDER BY Outlet_Location_Type, sales_rank;

-- CTE: Find outlets performing above average sales
WITH outlet_sales AS (
    SELECT 
        Outlet_Identifier,
        Outlet_Type,
        Outlet_Location_Type,
        ROUND(SUM(Sales), 2) AS total_sales,
        ROUND(AVG(Sales), 2) AS avg_sales
    FROM grocery_sales
    GROUP BY Outlet_Identifier, Outlet_Type, Outlet_Location_Type
),
overall_avg AS (
    SELECT ROUND(AVG(Sales), 2) AS overall_avg_sales FROM grocery_sales
)
SELECT 
    o.Outlet_Identifier,
    o.Outlet_Type,
    o.Outlet_Location_Type,
    o.total_sales,
    oa.overall_avg_sales,
    CASE WHEN o.avg_sales > oa.overall_avg_sales THEN 'Above Average' ELSE 'Below Average' END AS performance
FROM outlet_sales o
CROSS JOIN overall_avg oa
ORDER BY o.total_sales DESC;

-- CTE: Category contribution to total revenue
WITH category_sales AS (
    SELECT 
        Item_Type,
        ROUND(SUM(Sales), 2) AS category_total
    FROM grocery_sales
    GROUP BY Item_Type
),
total AS (
    SELECT ROUND(SUM(Sales), 2) AS grand_total FROM grocery_sales
)
SELECT 
    cs.Item_Type,
    cs.category_total,
    t.grand_total,
    ROUND((cs.category_total / t.grand_total) * 100, 2) AS revenue_contribution_pct
FROM category_sales cs
CROSS JOIN total t
ORDER BY revenue_contribution_pct DESC;
