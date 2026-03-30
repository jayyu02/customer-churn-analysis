# Customer Churn Analysis

**Tools:** Python · SQL (SQLite) · pandas · scikit-learn · matplotlib · seaborn
**Dataset:** 1,000 customers · 17 features · telecom industry
**Models:** Logistic Regression · Random Forest
**Author:** Jaya Mundre · [LinkedIn](https://www.linkedin.com/in/jaya-mundre-238848299) · [GitHub](https://github.com/jayyu02)

---

## Project Overview

Customer churn means a customer stops using a service. Losing customers is expensive — it costs 5x more to acquire a new customer than to retain an existing one. This project uses **SQL to explore churn patterns** and **machine learning to predict which customers are likely to leave** — so the business can act before they do.

---

## Key Findings

| Insight | Finding |
|---|---|
| Overall churn rate | **34%** of customers churned |
| Highest risk contract | **Month-to-Month** — 45.6% churn rate vs 18.9% for annual contracts |
| Tenure effect | **New customers (0–12 months)** churn the most |
| Support calls signal | Customers with **5+ support calls** have dramatically higher churn |
| Best ML model | **Logistic Regression — 73.5% accuracy** |
| Top churn predictor | **Contract type** is the #1 feature predicting churn |

---

## Machine Learning Models

| Model | Accuracy | AUC Score |
|---|---|---|
| Logistic Regression | **73.5%** | **0.716** |
| Random Forest | 70.5% | 0.674 |

---

## Business Recommendations

1. **Offer discounts to Month-to-Month customers** to switch to annual contracts — this alone could cut churn by 50%+
2. **Trigger proactive outreach after the 3rd support call** — customers calling repeatedly are at high risk
3. **Focus retention efforts on the first 12 months** — new customers churn the most

---

## Connect
- LinkedIn: [linkedin.com/in/jaya-mundre-238848299](https://www.linkedin.com/in/jaya-mundre-238848299)
- Project 1: [Superstore Sales Analysis](https://github.com/jayyu02/superstore-sales-analysis)
