"""
Generates a realistic, slightly messy online-retail dataset (2023-2024).

Why synthetic? It keeps the project runnable anywhere with no downloads, and the
data has real business patterns baked in (heavy electronics discounting, losses at deep discounts,
delivery delays hurting ratings) so there is a story to find.
Swap in a real dataset later (see docs/CAREER_GUIDE.md).

Run:  python data/generate_data.py
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
OUT = Path(__file__).parent
START, END = pd.Timestamp("2023-01-01"), pd.Timestamp("2024-12-31")

# ---------- products ----------
# category: (n_products, price_low, price_high, cost_ratio)  cost_ratio = unit_cost / list_price
CATS = {
    "Electronics":    (12, 1500, 40000, 0.85),
    "Fashion":        (14, 400, 4000, 0.45),
    "Home & Kitchen": (12, 300, 8000, 0.60),
    "Beauty":         (10, 150, 2500, 0.40),
    "Grocery":        (8, 50, 1200, 0.80),
    "Sports":         (8, 500, 9000, 0.55),
}
rows = []
pid = 1
for cat, (n, lo, hi, ratio) in CATS.items():
    for i in range(n):
        price = round(float(np.exp(rng.uniform(np.log(lo), np.log(hi)))), -1)
        cost = round(price * (ratio + rng.normal(0, 0.03)), 2)
        rows.append((pid, f"{cat.split()[0]} Item {i+1:02d}", cat, cost, price))
        pid += 1
products = pd.DataFrame(rows, columns=["product_id", "product_name", "category", "unit_cost", "list_price"])

# ---------- customers ----------
N_CUST = 3000
cities = {  # city: (weight, avg delivery days)
    "Mumbai": (0.17, 3.0), "Delhi": (0.17, 3.2), "Bengaluru": (0.16, 3.0),
    "Hyderabad": (0.12, 3.4), "Chennai": (0.09, 3.6), "Pune": (0.08, 3.5),
    "Kolkata": (0.07, 4.2), "Jaipur": (0.05, 4.6), "Lucknow": (0.05, 5.0), "Patna": (0.04, 5.6),
}
city_names = list(cities)
city_p = np.array([cities[c][0] for c in city_names]); city_p /= city_p.sum()
channels = {  # channel: (weight, mean repeat orders)
    "Organic": (0.30, 1.5), "Paid Search": (0.25, 0.9), "Social Media": (0.20, 0.7),
    "Referral": (0.10, 2.3), "Email": (0.15, 1.8),
}
ch_names = list(channels)
ch_p = np.array([channels[c][0] for c in ch_names]); ch_p /= ch_p.sum()

signup = START + pd.to_timedelta(rng.integers(0, (END - START).days - 20, N_CUST), unit="D")
customers = pd.DataFrame({
    "customer_id": np.arange(1, N_CUST + 1),
    "signup_date": signup,
    "city": rng.choice(city_names, N_CUST, p=city_p),
    "acquisition_channel": rng.choice(ch_names, N_CUST, p=ch_p),
})

# ---------- orders ----------
month_weight = {1: .9, 2: .85, 3: .95, 4: .9, 5: .95, 6: .9, 7: 1.0, 8: 1.05,
                9: 1.1, 10: 1.6, 11: 1.7, 12: 1.3}   # festive season peak

order_rows = []
for c in customers.itertuples():
    first = c.signup_date + pd.Timedelta(days=int(rng.integers(0, 15)))
    dates = [first]
    n_repeat = rng.poisson(channels[c.acquisition_channel][1])
    d = first
    for _ in range(n_repeat):
        d = d + pd.Timedelta(days=int(rng.exponential(55)) + 7)
        # thin by seasonality so festive months get more orders
        if rng.random() < month_weight[d.month] / 1.7 + 0.25:
            dates.append(d)
    order_rows += [(c.customer_id, x) for x in dates if x <= END]

orders = pd.DataFrame(order_rows, columns=["customer_id", "order_date"]).sort_values("order_date").reset_index(drop=True)
orders.insert(0, "order_id", np.arange(10001, 10001 + len(orders)))
orders = orders.merge(customers[["customer_id", "city"]], on="customer_id")
n = len(orders)

orders["payment_method"] = rng.choice(["UPI", "Credit Card", "Debit Card", "COD", "Net Banking"], n,
                                      p=[.42, .18, .14, .20, .06])
orders["status"] = rng.choice(["Delivered", "Cancelled", "Returned"], n, p=[.92, .05, .03])
orders["promised_days"] = 5
base = orders["city"].map({c: v[1] for c, v in cities.items()})
orders["delivery_days"] = np.clip(np.round(base + rng.gamma(2.0, 0.9, n) - 1.2), 1, 14).astype(int)
orders["ship_date"] = orders["order_date"] + pd.to_timedelta(rng.integers(0, 3, n), unit="D")
orders["delivery_date"] = orders["ship_date"] + pd.to_timedelta(orders["delivery_days"], unit="D")
delay = np.clip(orders["delivery_days"] - orders["promised_days"], 0, None)
orders["rating"] = np.clip(np.round(4.5 - 0.45 * delay + rng.normal(0, 0.7, n)), 1, 5)
orders.loc[orders["status"] == "Cancelled", ["delivery_date", "ship_date", "rating"]] = np.nan
orders.loc[rng.random(n) < 0.30, "rating"] = np.nan          # most people don't leave a rating
orders = orders.drop(columns=["city", "delivery_days"])       # derive these in analysis, like real data

# ---------- order items ----------
items = []
cat_of = products.set_index("product_id")["category"].to_dict()
pids = products["product_id"].to_numpy()
for o in orders.itertuples():
    k = int(rng.choice([1, 2, 3, 4], p=[.5, .3, .15, .05]))
    festive = o.order_date.month in (10, 11)
    for pid_ in rng.choice(pids, k, replace=False):
        cat = cat_of[int(pid_)]
        if cat == "Electronics":
            probs = [.20, .20, .15, .15, .15, .15] if festive else [.50, .20, .12, .10, .05, .03]
        elif festive:
            probs = [.25, .30, .20, .10, .10, .05]
        else:
            probs = [.60, .20, .10, .06, .03, .01]
        disc = int(rng.choice([0, 5, 10, 15, 20, 30], p=probs))
        qty = 1 + int(rng.random() < 0.15 + disc / 100)
        items.append((o.order_id, int(pid_), qty, disc))
order_items = pd.DataFrame(items, columns=["order_id", "product_id", "quantity", "discount_pct"])

# ---------- make it realistically messy ----------
dups = orders.sample(frac=0.01, random_state=1)
orders = pd.concat([orders, dups]).sort_values("order_id").reset_index(drop=True)      # duplicate order rows
mess = {"Bengaluru": ["Bangalore", "bengaluru", "BENGALURU "], "Mumbai": ["mumbai", "Mumbai "],
        "Delhi": ["delhi", "New Delhi"], "Hyderabad": ["hyderabad", "HYDERABAD"]}
customers["city"] = customers["city"].astype(object)
for city, variants in mess.items():
    idx = customers.index[customers["city"] == city]
    pick = rng.choice(idx, int(len(idx) * 0.12), replace=False)
    customers.loc[pick, "city"] = rng.choice(variants, len(pick))
customers.loc[rng.choice(customers.index, 40, replace=False), "city"] = np.nan          # missing cities

products.to_csv(OUT / "products.csv", index=False)
customers.to_csv(OUT / "customers.csv", index=False)
orders.to_csv(OUT / "orders.csv", index=False)
order_items.to_csv(OUT / "order_items.csv", index=False)
print(f"customers={len(customers):,} orders={len(orders):,} items={len(order_items):,} products={len(products)}")
