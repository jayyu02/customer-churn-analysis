import pandas as pd
import numpy as np
import random
random.seed(42)
np.random.seed(42)

n = 1000
tenure       = np.random.randint(1, 72, n)
age          = np.random.randint(18, 70, n)
monthly_charge = np.random.uniform(20, 120, n).round(2)
total_charge = (monthly_charge * tenure * np.random.uniform(0.85,1.05,n)).round(2)
num_products = np.random.randint(1, 5, n)
support_calls= np.random.randint(0, 10, n)
contract     = np.random.choice(['Month-to-Month','One Year','Two Year'], n, p=[0.55,0.25,0.20])
payment      = np.random.choice(['Electronic Check','Mailed Check','Bank Transfer','Credit Card'], n)
internet     = np.random.choice(['DSL','Fiber Optic','No'], n, p=[0.35,0.45,0.20])
gender       = np.random.choice(['Male','Female'], n)
senior       = np.random.choice([0,1], n, p=[0.84,0.16])
partner      = np.random.choice([0,1], n)
dependents   = np.random.choice([0,1], n)
paperless    = np.random.choice([0,1], n)
online_sec   = np.random.choice([0,1], n)
tech_support = np.random.choice([0,1], n)

# churn probability based on real-world signals
churn_prob = (
    0.05
    + (contract == 'Month-to-Month') * 0.25
    + (support_calls > 4) * 0.20
    + (tenure < 12) * 0.15
    + (monthly_charge > 80) * 0.10
    + (internet == 'Fiber Optic') * 0.08
    + (online_sec == 0) * 0.05
    + (tech_support == 0) * 0.05
    - (tenure > 36) * 0.10
    - (num_products > 2) * 0.08
    - (partner == 1) * 0.05
)
churn_prob = np.clip(churn_prob, 0.02, 0.95)
churn = (np.random.uniform(0,1,n) < churn_prob).astype(int)

df = pd.DataFrame({
    'customer_id':    [f'CUST-{1000+i}' for i in range(n)],
    'gender':         gender,
    'senior_citizen': senior,
    'partner':        partner,
    'dependents':     dependents,
    'tenure':         tenure,
    'age':            age,
    'contract':       contract,
    'payment_method': payment,
    'internet_service':internet,
    'paperless_billing':paperless,
    'online_security': online_sec,
    'tech_support':    tech_support,
    'num_products':    num_products,
    'support_calls':   support_calls,
    'monthly_charges': monthly_charge,
    'total_charges':   total_charge,
    'churn':           churn,
})

df.to_csv('data/churn.csv', index=False)
print(f"Generated {len(df)} rows  |  Churn rate: {df.churn.mean()*100:.1f}%")
print(df.head(3).to_string())
