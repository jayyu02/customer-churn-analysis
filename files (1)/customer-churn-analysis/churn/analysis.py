"""
Customer Churn Analysis
=======================
Author : Jaya Mundre
Tools  : Python, pandas, matplotlib, seaborn, scikit-learn, SQLite
Dataset: data/churn.csv (1,000 customers)

Run:
    python analysis.py
Outputs saved to outputs/ and models/
"""

import sqlite3, os, warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, roc_auc_score, roc_curve)

warnings.filterwarnings('ignore')
os.makedirs('outputs', exist_ok=True)
os.makedirs('models',  exist_ok=True)

# ── style ─────────────────────────────────────────────────────────────────────
BLUE   = '#2E75B6'
RED    = '#C00000'
GREEN  = '#70AD47'
ORANGE = '#ED7D31'
PURPLE = '#7030A0'
GRAY   = '#808080'

plt.rcParams.update({
    'figure.facecolor':'white','axes.facecolor':'white',
    'axes.spines.top':False,'axes.spines.right':False,
    'axes.grid':True,'grid.alpha':0.3,'grid.linestyle':'--',
    'font.family':'DejaVu Sans','axes.titlesize':13,
    'axes.titleweight':'bold','axes.labelsize':11,
})

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD DATA → SQLITE
# ─────────────────────────────────────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv('data/churn.csv')
conn = sqlite3.connect(':memory:')
df.to_sql('churn', conn, index=False, if_exists='replace')
print(f"  {len(df):,} customers loaded  |  Churn rate: {df.churn.mean()*100:.1f}%")

def q(sql): return pd.read_sql_query(sql, conn)

# ─────────────────────────────────────────────────────────────────────────────
# 2. SQL QUERIES
# ─────────────────────────────────────────────────────────────────────────────
kpi = q("""
    SELECT COUNT(*) total, SUM(churn) churned,
           ROUND(SUM(churn)*100.0/COUNT(*),1) rate
    FROM churn
""").iloc[0]

contract = q("""
    SELECT contract, COUNT(*) total, SUM(churn) churned,
           ROUND(SUM(churn)*100.0/COUNT(*),1) churn_rate
    FROM churn GROUP BY contract ORDER BY churn_rate DESC
""")

internet = q("""
    SELECT internet_service, COUNT(*) total, SUM(churn) churned,
           ROUND(SUM(churn)*100.0/COUNT(*),1) churn_rate
    FROM churn GROUP BY internet_service ORDER BY churn_rate DESC
""")

tenure_grp = q("""
    SELECT
        CASE WHEN tenure<=12 THEN '0-12 mo (New)'
             WHEN tenure<=24 THEN '13-24 mo'
             WHEN tenure<=48 THEN '25-48 mo'
             ELSE '49+ mo (Loyal)' END AS tenure_group,
        ROUND(SUM(churn)*100.0/COUNT(*),1) churn_rate
    FROM churn GROUP BY tenure_group ORDER BY churn_rate DESC
""")

support = q("""
    SELECT
        CASE WHEN support_calls=0 THEN '0 calls'
             WHEN support_calls<=2 THEN '1-2 calls'
             WHEN support_calls<=4 THEN '3-4 calls'
             ELSE '5+ calls' END AS support_band,
        ROUND(SUM(churn)*100.0/COUNT(*),1) churn_rate,
        COUNT(*) total
    FROM churn GROUP BY support_band ORDER BY churn_rate DESC
""")

comparison = q("""
    SELECT CASE WHEN churn=1 THEN 'Churned' ELSE 'Retained' END status,
           ROUND(AVG(monthly_charges),2) avg_charge,
           ROUND(AVG(tenure),1) avg_tenure,
           ROUND(AVG(support_calls),1) avg_calls,
           ROUND(AVG(num_products),1) avg_products
    FROM churn GROUP BY status
""")

payment = q("""
    SELECT payment_method,
           ROUND(SUM(churn)*100.0/COUNT(*),1) churn_rate
    FROM churn GROUP BY payment_method ORDER BY churn_rate DESC
""")

print("\n── KEY METRICS ─────────────────────────────────────────")
print(f"  Total customers : {int(kpi.total):,}")
print(f"  Churned         : {int(kpi.churned):,}")
print(f"  Churn rate      : {kpi.rate}%")
print("\n── CHURN BY CONTRACT ───────────────────────────────────")
print(contract.to_string(index=False))
print("\n── CHURNED vs RETAINED ─────────────────────────────────")
print(comparison.to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────────
# 3. CHARTS
# ─────────────────────────────────────────────────────────────────────────────

# Chart 1 — Churn distribution (pie)
fig, ax = plt.subplots(figsize=(6,5))
vals   = [int(kpi.churned), int(kpi.total - kpi.churned)]
labels = [f'Churned\n{kpi.rate}%', f'Retained\n{100-kpi.rate}%']
ax.pie(vals, labels=labels, colors=[RED, GREEN],
       autopct='%1.1f%%', startangle=140,
       wedgeprops={'linewidth':1,'edgecolor':'white'})
ax.set_title('Overall Churn Rate')
plt.tight_layout()
plt.savefig('outputs/01_churn_overview.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nSaved: outputs/01_churn_overview.png")

# Chart 2 — Churn by contract type (bar)
fig, ax = plt.subplots(figsize=(7,4))
colors = [RED if r > 30 else ORANGE if r > 15 else GREEN
          for r in contract.churn_rate]
bars = ax.bar(contract.contract, contract.churn_rate, color=colors, width=0.5)
ax.bar_label(bars, labels=[f"{v}%" for v in contract.churn_rate],
             padding=4, fontsize=11)
ax.set_title('Churn Rate by Contract Type')
ax.set_ylabel('Churn Rate (%)')
ax.set_ylim(0, max(contract.churn_rate)*1.2)
plt.tight_layout()
plt.savefig('outputs/02_churn_by_contract.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/02_churn_by_contract.png")

# Chart 3 — Churn by tenure group (bar)
fig, ax = plt.subplots(figsize=(8,4))
order  = ['0-12 mo (New)','13-24 mo','25-48 mo','49+ mo (Loyal)']
tg     = tenure_grp.set_index('tenure_group').reindex(order).reset_index()
colors = [RED, ORANGE, BLUE, GREEN]
bars   = ax.bar(tg.tenure_group, tg.churn_rate, color=colors, width=0.5)
ax.bar_label(bars, labels=[f"{v}%" for v in tg.churn_rate],
             padding=4, fontsize=11)
ax.set_title('Churn Rate by Customer Tenure')
ax.set_ylabel('Churn Rate (%)')
ax.set_ylim(0, max(tg.churn_rate)*1.2)
plt.tight_layout()
plt.savefig('outputs/03_churn_by_tenure.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/03_churn_by_tenure.png")

# Chart 4 — Churn by support calls (bar)
fig, ax = plt.subplots(figsize=(7,4))
s_order = ['0 calls','1-2 calls','3-4 calls','5+ calls']
sp      = support.set_index('support_band').reindex(s_order).reset_index()
bars    = ax.bar(sp.support_band, sp.churn_rate,
                 color=[GREEN, BLUE, ORANGE, RED], width=0.5)
ax.bar_label(bars, labels=[f"{v}%" for v in sp.churn_rate],
             padding=4, fontsize=11)
ax.set_title('Churn Rate by Support Calls Made')
ax.set_ylabel('Churn Rate (%)')
ax.set_ylim(0, max(sp.churn_rate)*1.2)
plt.tight_layout()
plt.savefig('outputs/04_churn_by_support.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/04_churn_by_support.png")

# Chart 5 — Churned vs Retained comparison (grouped bar)
fig, ax = plt.subplots(figsize=(8,4))
metrics = ['avg_charge','avg_tenure','avg_calls','avg_products']
labels  = ['Avg Monthly\nCharge ($)','Avg Tenure\n(months)',
           'Avg Support\nCalls','Avg Products']
x   = np.arange(len(metrics))
w   = 0.3
ch  = comparison[comparison.status=='Churned'].iloc[0]
re  = comparison[comparison.status=='Retained'].iloc[0]
ax.bar(x-w/2, [ch[m] for m in metrics], width=w, label='Churned',  color=RED)
ax.bar(x+w/2, [re[m] for m in metrics], width=w, label='Retained', color=GREEN)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_title('Churned vs Retained — Key Differences')
ax.legend()
plt.tight_layout()
plt.savefig('outputs/05_churned_vs_retained.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/05_churned_vs_retained.png")

# Chart 6 — Correlation heatmap
fig, ax = plt.subplots(figsize=(8,6))
num_cols = ['tenure','monthly_charges','total_charges',
            'num_products','support_calls','senior_citizen',
            'partner','online_security','tech_support','churn']
corr = df[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
            cmap='RdYlGn', center=0, ax=ax,
            linewidths=0.5, annot_kws={'size':9})
ax.set_title('Feature Correlation Heatmap')
plt.tight_layout()
plt.savefig('outputs/06_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/06_correlation_heatmap.png")

# ─────────────────────────────────────────────────────────────────────────────
# 4. MACHINE LEARNING — PREDICT CHURN
# ─────────────────────────────────────────────────────────────────────────────
print("\n── MACHINE LEARNING ────────────────────────────────────")

# encode categorical columns
df_ml = df.copy()
le    = LabelEncoder()
for col in ['gender','contract','payment_method','internet_service']:
    df_ml[col] = le.fit_transform(df_ml[col])
df_ml.drop('customer_id', axis=1, inplace=True)

X = df_ml.drop('churn', axis=1)
y = df_ml['churn']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Logistic Regression
lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train, y_train)
lr_pred = lr.predict(X_test)
lr_acc  = accuracy_score(y_test, lr_pred)
lr_auc  = roc_auc_score(y_test, lr.predict_proba(X_test)[:,1])

# Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_acc  = accuracy_score(y_test, rf_pred)
rf_auc  = roc_auc_score(y_test, rf.predict_proba(X_test)[:,1])

print(f"  Logistic Regression  — Accuracy: {lr_acc*100:.1f}%  AUC: {lr_auc:.3f}")
print(f"  Random Forest        — Accuracy: {rf_acc*100:.1f}%  AUC: {rf_auc:.3f}")

# Chart 7 — Feature Importance (Random Forest)
fi = pd.Series(rf.feature_importances_, index=X.columns)
fi = fi.sort_values(ascending=True).tail(10)
fig, ax = plt.subplots(figsize=(8,5))
bars = ax.barh(fi.index, fi.values,
               color=[RED if v > fi.values.mean() else BLUE for v in fi.values])
ax.set_title('Top 10 Features Predicting Churn (Random Forest)')
ax.set_xlabel('Importance Score')
for i, v in enumerate(fi.values):
    ax.text(v+0.001, i, f'{v:.3f}', va='center', fontsize=9)
plt.tight_layout()
plt.savefig('outputs/07_feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/07_feature_importance.png")

# Chart 8 — ROC Curve (both models)
fig, ax = plt.subplots(figsize=(6,5))
for model, name, color in [
    (lr, f'Logistic Regression (AUC={lr_auc:.2f})', BLUE),
    (rf, f'Random Forest (AUC={rf_auc:.2f})',        RED)]:
    fpr, tpr, _ = roc_curve(y_test, model.predict_proba(X_test)[:,1])
    ax.plot(fpr, tpr, color=color, linewidth=2, label=name)
ax.plot([0,1],[0,1], 'k--', linewidth=1, label='Random baseline')
ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
ax.set_title('ROC Curve — Model Comparison')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('outputs/08_roc_curve.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/08_roc_curve.png")

# Chart 9 — Confusion Matrix (Random Forest)
fig, ax = plt.subplots(figsize=(5,4))
cm = confusion_matrix(y_test, rf_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
            xticklabels=['Predicted\nRetained','Predicted\nChurned'],
            yticklabels=['Actual\nRetained','Actual\nChurned'])
ax.set_title(f'Confusion Matrix — Random Forest\nAccuracy: {rf_acc*100:.1f}%')
plt.tight_layout()
plt.savefig('outputs/09_confusion_matrix.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: outputs/09_confusion_matrix.png")

print(f"\n All charts saved to outputs/")
print(f" Best model: Random Forest — {rf_acc*100:.1f}% accuracy, AUC {rf_auc:.3f}")
conn.close()
