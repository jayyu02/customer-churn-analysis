-- ============================================================
-- Customer Churn Analysis — SQL Queries
-- Database: SQLite  |  Author: Jaya Mundre
-- ============================================================

-- ──────────────────────────────────────────────
-- Q1: Overall churn rate
-- ──────────────────────────────────────────────
SELECT
    COUNT(*)                            AS total_customers,
    SUM(churn)                          AS churned_customers,
    ROUND(SUM(churn)*100.0/COUNT(*),1)  AS churn_rate_pct,
    COUNT(*) - SUM(churn)               AS retained_customers
FROM churn;


-- ──────────────────────────────────────────────
-- Q2: Churn rate by contract type
-- ──────────────────────────────────────────────
SELECT
    contract,
    COUNT(*)                            AS total,
    SUM(churn)                          AS churned,
    ROUND(SUM(churn)*100.0/COUNT(*),1)  AS churn_rate_pct
FROM churn
GROUP BY contract
ORDER BY churn_rate_pct DESC;


-- ──────────────────────────────────────────────
-- Q3: Churn rate by internet service type
-- ──────────────────────────────────────────────
SELECT
    internet_service,
    COUNT(*)                            AS total,
    SUM(churn)                          AS churned,
    ROUND(SUM(churn)*100.0/COUNT(*),1)  AS churn_rate_pct,
    ROUND(AVG(monthly_charges),2)       AS avg_monthly_charge
FROM churn
GROUP BY internet_service
ORDER BY churn_rate_pct DESC;


-- ──────────────────────────────────────────────
-- Q4: Churn rate by tenure group
--     (how long they have been a customer)
-- ──────────────────────────────────────────────
SELECT
    CASE
        WHEN tenure <= 12  THEN '0-12 months (New)'
        WHEN tenure <= 24  THEN '13-24 months'
        WHEN tenure <= 48  THEN '25-48 months'
        ELSE '49+ months (Loyal)'
    END                                 AS tenure_group,
    COUNT(*)                            AS total,
    SUM(churn)                          AS churned,
    ROUND(SUM(churn)*100.0/COUNT(*),1)  AS churn_rate_pct,
    ROUND(AVG(monthly_charges),2)       AS avg_monthly_charge
FROM churn
GROUP BY tenure_group
ORDER BY churn_rate_pct DESC;


-- ──────────────────────────────────────────────
-- Q5: Impact of support calls on churn
-- ──────────────────────────────────────────────
SELECT
    CASE
        WHEN support_calls = 0 THEN '0 calls'
        WHEN support_calls <= 2 THEN '1-2 calls'
        WHEN support_calls <= 4 THEN '3-4 calls'
        ELSE '5+ calls'
    END                                 AS support_band,
    COUNT(*)                            AS total,
    SUM(churn)                          AS churned,
    ROUND(SUM(churn)*100.0/COUNT(*),1)  AS churn_rate_pct
FROM churn
GROUP BY support_band
ORDER BY churn_rate_pct DESC;


-- ──────────────────────────────────────────────
-- Q6: Churn rate by monthly charge band
-- ──────────────────────────────────────────────
SELECT
    CASE
        WHEN monthly_charges < 40  THEN 'Low ($0-40)'
        WHEN monthly_charges < 70  THEN 'Medium ($40-70)'
        WHEN monthly_charges < 100 THEN 'High ($70-100)'
        ELSE 'Very High ($100+)'
    END                                 AS charge_band,
    COUNT(*)                            AS total,
    SUM(churn)                          AS churned,
    ROUND(SUM(churn)*100.0/COUNT(*),1)  AS churn_rate_pct
FROM churn
GROUP BY charge_band
ORDER BY churn_rate_pct DESC;


-- ──────────────────────────────────────────────
-- Q7: Churn rate by number of products
-- ──────────────────────────────────────────────
SELECT
    num_products,
    COUNT(*)                            AS total,
    SUM(churn)                          AS churned,
    ROUND(SUM(churn)*100.0/COUNT(*),1)  AS churn_rate_pct
FROM churn
GROUP BY num_products
ORDER BY num_products;


-- ──────────────────────────────────────────────
-- Q8: Churn by payment method
-- ──────────────────────────────────────────────
SELECT
    payment_method,
    COUNT(*)                            AS total,
    SUM(churn)                          AS churned,
    ROUND(SUM(churn)*100.0/COUNT(*),1)  AS churn_rate_pct
FROM churn
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;


-- ──────────────────────────────────────────────
-- Q9: Average monthly charges — churned vs retained
-- ──────────────────────────────────────────────
SELECT
    CASE WHEN churn=1 THEN 'Churned' ELSE 'Retained' END AS status,
    COUNT(*)                            AS customers,
    ROUND(AVG(monthly_charges),2)       AS avg_monthly_charge,
    ROUND(AVG(tenure),1)                AS avg_tenure_months,
    ROUND(AVG(support_calls),1)         AS avg_support_calls,
    ROUND(AVG(num_products),1)          AS avg_products
FROM churn
GROUP BY status;


-- ──────────────────────────────────────────────
-- Q10: High risk customers
--      (Month-to-Month + 5+ support calls + tenure < 12)
-- ──────────────────────────────────────────────
SELECT
    customer_id,
    contract,
    tenure,
    support_calls,
    monthly_charges,
    churn
FROM churn
WHERE contract     = 'Month-to-Month'
  AND support_calls >= 5
  AND tenure        < 12
ORDER BY support_calls DESC, monthly_charges DESC
LIMIT 15;
