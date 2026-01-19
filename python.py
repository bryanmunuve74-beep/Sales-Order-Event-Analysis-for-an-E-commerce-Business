import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv(r"D:\New folder\full.csv")
pd.set_option('display.max_columns', None)
print(df)


funnel_counts = (
    df.groupby('event_type')['customer_id']
      .nunique()
      .sort_index()
)
print(funnel_counts)

conversion_rates = funnel_counts / funnel_counts.shift(1)
print(conversion_rates)
plt.figure()
funnel_counts.plot(kind='bar')
plt.title('Sales Funnel – Customers per Stage')
plt.xlabel('Stage')
plt.ylabel('Unique Customers')
plt.tight_layout()
plt.show()


# Leakage by sales rep
leakage_by_rep = (
   df.groupby('sales_rep')['final_price']
      .sum()
      .sort_values(ascending=False)
)

leakage_by_rep
plt.figure()
leakage_by_rep.plot(kind='bar')
plt.title('Revenue Leakage by Sales Rep')
plt.xlabel('Sales Rep')
plt.ylabel('Revenue Lost')
plt.tight_layout()
plt.show()
### B. Lost Revenue from Dropped Deals

lost_deals = df[df['deal_status'] == 'dropped']
lost_revenue = lost_deals['final_price'].sum()

print("LOST REVENUE:", lost_revenue)

# Calculate delay between stages
df['event_date'] = pd.to_datetime(df['event_date'])
df['expected_date'] = df['event_date'] + pd.Timedelta(days=3)
df['next_event_date'] = pd.to_datetime(df['expected_date'])

df['delay_days'] = (df['next_event_date'] - df['event_date']).dt.days

df = df.sort_values(['customer_id', 'event_date'])

df['next_event_date'] = df.groupby('customer_id')['event_date'].shift(-1)
df['delay_days'] = (df['next_event_date'] - df['event_date']).dt.days

avg_delay = df.groupby('event_type')['delay_days'].mean()
print("avg delay:", avg_delay)
## 6. NumPy-Based Optimization Scenarios

### A. Identify Extreme Discounts


threshold = np.percentile(df['discount'], 90)

df['high_discount_flag'] = np.where(df['discount'] > threshold, 1, 0)

print("Threshold:", threshold)

high_discount_impact = df[df['high_discount_flag'] == 1]['discount'].sum()
print("High Discount Impact:", high_discount_impact)

### B. Revenue Recovery Simulation


# Simulate optimized pricing (5% improvement)
df['optimized_price'] = df['list_price'] * 0.95

df['recovered_revenue'] = (
    df['optimized_price'] - df['final_price']
).clip(lower=0)

recovered_total = df['recovered_revenue'].sum()
print("Recovered Total:", recovered_total)




