# %% [markdown]
# # Retail Sales, Profit & Customer Retention Analysis
# **Business question:** Where is this online store making and losing money, who are its
# best customers, and what should the business change next quarter?
#
# Sections: 1 Clean data · 2 KPIs · 3 Revenue trend · 4 Categories · 5 Discounts ·
# 6 Acquisition channels · 7 RFM segments · 8 Cohort retention · 9 Delivery vs ratings
#
# Tip: this file uses `# %%` cell markers, so VS Code and Jupytext open it as a notebook.

# %%
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                      # remove this line when running in a notebook
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

try:
    ROOT = Path(__file__).resolve().parent
except NameError:                          # running inside a notebook
    ROOT = Path.cwd()
DATA, CHARTS, TABLES = ROOT / "data", ROOT / "outputs/charts", ROOT / "outputs/tables"
CHARTS.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", font_scale=1.0)
ACCENT, MUTED, ALERT = "#1f6f78", "#9db4b7", "#d6452b"
findings = {}


def save(fig, name):
    fig.tight_layout()
    fig.savefig(CHARTS / f"{name}.png", dpi=150)
    plt.close(fig)


def inr(x):
    return f"₹{x/1e5:,.1f}L" if abs(x) < 1e7 else f"₹{x/1e7:,.2f}Cr"


# %% [markdown]
# ## 1. Load and clean the data
# Real data is messy. Issues found and fixed here: duplicate order rows, inconsistent city
# names, missing cities, and cancelled/returned orders that must not count as revenue.

# %%
customers = pd.read_csv(DATA / "customers.csv", parse_dates=["signup_date"])
products = pd.read_csv(DATA / "products.csv")
orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date", "ship_date", "delivery_date"])
items = pd.read_csv(DATA / "order_items.csv")

issues = {
    "duplicate_order_rows": int(orders.duplicated("order_id").sum()),
    "missing_city": int(customers["city"].isna().sum()),
    "city_spellings_before": int(customers["city"].nunique()),
    "cancelled_orders": int((orders["status"] == "Cancelled").sum()),
    "returned_orders": int((orders["status"] == "Returned").sum()),
}

orders = orders.drop_duplicates("order_id").copy()

city_fix = {"Bangalore": "Bengaluru", "New Delhi": "Delhi"}
customers["city"] = (customers["city"].str.strip().str.title()
                     .replace(city_fix).fillna("Unknown"))
issues["city_spellings_after"] = int(customers["city"].nunique())
findings["data_quality"] = issues

# line-item economics
items = items.merge(products, on="product_id")
items["gross"] = items["list_price"] * items["quantity"]
items["revenue"] = items["gross"] * (1 - items["discount_pct"] / 100)
items["cost"] = items["unit_cost"] * items["quantity"]
items["profit"] = items["revenue"] - items["cost"]

orders["delivery_days"] = (orders["delivery_date"] - orders["order_date"]).dt.days
orders["delay_days"] = (orders["delivery_days"] - orders["promised_days"]).clip(lower=0)

# Revenue counts only Delivered orders.
good = orders.loc[orders["status"] == "Delivered", ["order_id", "customer_id", "order_date"]]
sales = (items.merge(good, on="order_id")
              .merge(customers[["customer_id", "city", "acquisition_channel"]], on="customer_id"))
sales["month"] = sales["order_date"].dt.to_period("M").dt.to_timestamp()

# %% [markdown]
# ## 2. Headline KPIs

# %%
order_totals = sales.groupby("order_id")["revenue"].sum()
k = {
    "revenue": float(sales["revenue"].sum()),
    "profit": float(sales["profit"].sum()),
    "orders": int(order_totals.size),
    "customers": int(sales["customer_id"].nunique()),
    "aov": float(order_totals.mean()),
}
k["margin_pct"] = k["profit"] / k["revenue"] * 100
per_cust = sales.groupby("customer_id")["order_id"].nunique()
k["repeat_rate_pct"] = float((per_cust >= 2).mean() * 100)
findings["kpis"] = k
print({a: round(b, 2) for a, b in k.items()})

# %% [markdown]
# ## 3. Revenue trend and seasonality

# %%
monthly = sales.groupby("month").agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
monthly["is_festive"] = monthly.index.month.isin([10, 11])
monthly.to_csv(TABLES / "monthly_revenue.csv")

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.bar(monthly.index, monthly["revenue"] / 1e5, width=22,
       color=np.where(monthly["is_festive"], ALERT, ACCENT))
ax.set_title("Monthly revenue: festive months (Oct–Nov) in red")
ax.set_ylabel("Revenue (₹ lakh)")
save(fig, "01_monthly_revenue")

yr = sales.assign(year=sales["order_date"].dt.year)
by_year = yr.groupby("year")["revenue"].sum()
fest = yr[yr["order_date"].dt.month.isin([10, 11])].groupby("year")["revenue"].sum()
findings["revenue_by_year"] = {int(y): float(v) for y, v in by_year.items()}
findings["festive_share_pct"] = {int(y): float(fest[y] / by_year[y] * 100) for y in by_year.index}
findings["yoy_growth_pct"] = float((by_year[2024] / by_year[2023] - 1) * 100)

# %% [markdown]
# ## 4. Category performance: revenue is not profit

# %%
cat = sales.groupby("category").agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
cat["margin_pct"] = cat["profit"] / cat["revenue"] * 100
cat = cat.sort_values("revenue", ascending=False)
cat.to_csv(TABLES / "category_performance.csv")

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
axes[0].barh(cat.index[::-1], cat["revenue"][::-1] / 1e5, color=ACCENT)
axes[0].set_title("Revenue by category (₹ lakh)")
axes[1].barh(cat.index[::-1], cat["margin_pct"][::-1],
             color=[ALERT if m < 10 else ACCENT for m in cat["margin_pct"][::-1]])
axes[1].set_title("Profit margin by category (%)")
save(fig, "02_category_revenue_vs_margin")
findings["categories"] = {c: {"revenue": float(r.revenue), "margin_pct": float(r.margin_pct)}
                          for c, r in cat.iterrows()}

# %% [markdown]
# ## 5. Discounts: who is paying for the sale?

# %%
disc = sales.groupby("discount_pct").agg(revenue=("revenue", "sum"), profit=("profit", "sum"),
                                         lines=("order_id", "size"))
disc["margin_pct"] = disc["profit"] / disc["revenue"] * 100
disc.to_csv(TABLES / "discount_impact.csv")

pivot = (sales.groupby(["category", "discount_pct"])[["profit", "revenue"]].sum()
              .assign(m=lambda d: d["profit"] / d["revenue"] * 100)["m"].unstack())
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.heatmap(pivot, annot=True, fmt=".0f", cmap="RdYlGn", center=0, ax=ax,
            cbar_kws={"label": "Profit margin %"})
ax.set_title("Profit margin % by category and discount level")
ax.set_xlabel("Discount %")
ax.set_ylabel("")
save(fig, "03_discount_margin_heatmap")

loss = sales[sales["profit"] < 0]
findings["loss_making"] = {
    "lines": int(len(loss)),
    "share_of_lines_pct": float(len(loss) / len(sales) * 100),
    "total_loss": float(-loss["profit"].sum()),
    "by_category": {c: float(v) for c, v in (-loss.groupby("category")["profit"].sum()).sort_values(ascending=False).items()},
}
findings["margin_by_discount"] = {int(d): float(v) for d, v in disc["margin_pct"].items()}

# %% [markdown]
# ## 6. Acquisition channels: who brings customers that come back?

# %%
orders_per_cust = sales.groupby(["customer_id", "acquisition_channel"])["order_id"].nunique().reset_index()
chan = orders_per_cust.groupby("acquisition_channel").agg(
    customers=("customer_id", "nunique"),
    avg_orders=("order_id", "mean"),
    repeat_rate_pct=("order_id", lambda s: (s >= 2).mean() * 100))
chan["revenue_per_customer"] = (sales.groupby("acquisition_channel")["revenue"].sum()
                                / sales.groupby("acquisition_channel")["customer_id"].nunique())
chan = chan.sort_values("revenue_per_customer", ascending=False)
chan.to_csv(TABLES / "channel_performance.csv")

fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(chan.index[::-1], chan["revenue_per_customer"][::-1], color=ACCENT)
ax.set_title("Revenue per customer by acquisition channel (₹)")
save(fig, "04_channel_revenue_per_customer")
findings["channels"] = {c: {"repeat_rate_pct": float(r.repeat_rate_pct),
                            "revenue_per_customer": float(r.revenue_per_customer)}
                        for c, r in chan.iterrows()}

# %% [markdown]
# ## 7. RFM segmentation: who deserves which campaign?
# Recency (days since last order), Frequency (orders), Monetary (revenue). Each scored 1–5.

# %%
snapshot = sales["order_date"].max() + pd.Timedelta(days=1)
rfm = sales.groupby("customer_id").agg(
    recency=("order_date", lambda s: (snapshot - s.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("revenue", "sum"))
rfm["R"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)      # recent = high
rfm["F"] = rfm["frequency"].clip(upper=5)
rfm["M"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)


def segment(r):
    if r.R >= 4 and r.F >= 3 and r.M >= 4: return "Champions"
    if r.F >= 3: return "Loyal"
    if r.R <= 2 and r.F == 2: return "At risk"
    if r.R >= 4 and r.F == 1: return "New customers"
    if r.R <= 2: return "Hibernating"
    return "Needs attention"


rfm["segment"] = rfm.apply(segment, axis=1)
seg = rfm.groupby("segment").agg(customers=("monetary", "size"), revenue=("monetary", "sum"),
                                 avg_orders=("frequency", "mean"))
seg["customer_share_pct"] = seg["customers"] / seg["customers"].sum() * 100
seg["revenue_share_pct"] = seg["revenue"] / seg["revenue"].sum() * 100
seg = seg.sort_values("revenue", ascending=False)
seg.to_csv(TABLES / "rfm_segments.csv")
rfm.to_csv(TABLES / "rfm_customers.csv")

fig, ax = plt.subplots(figsize=(9, 4.5))
x = np.arange(len(seg))
ax.bar(x - 0.2, seg["customer_share_pct"], 0.4, label="% of customers", color=MUTED)
ax.bar(x + 0.2, seg["revenue_share_pct"], 0.4, label="% of revenue", color=ACCENT)
ax.set_xticks(x, seg.index, rotation=20)
ax.set_title("RFM segments: share of customers vs share of revenue")
ax.legend()
save(fig, "05_rfm_segments")
findings["rfm"] = {s: {"customer_share_pct": float(r.customer_share_pct),
                       "revenue_share_pct": float(r.revenue_share_pct)} for s, r in seg.iterrows()}

# %% [markdown]
# ## 8. Cohort retention: do customers come back?

# %%
first = sales.groupby("customer_id")["month"].min().rename("cohort")
act = sales.merge(first, on="customer_id")[["customer_id", "cohort", "month"]].drop_duplicates()
act["period"] = ((act["month"].dt.year - act["cohort"].dt.year) * 12
                 + (act["month"].dt.month - act["cohort"].dt.month))
cohort = act.groupby(["cohort", "period"])["customer_id"].nunique().unstack(fill_value=0)
retention = cohort.div(cohort[0], axis=0) * 100
shown = retention.loc[:, :6]
shown.to_csv(TABLES / "cohort_retention.csv")

fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(shown.where(shown > 0), annot=True, fmt=".0f", cmap="Blues", ax=ax,
            yticklabels=[d.strftime("%b %Y") for d in shown.index],
            cbar_kws={"label": "% of cohort still ordering"})
ax.set_title("Monthly cohort retention (months since first order)")
ax.set_xlabel("Months since first order")
ax.set_ylabel("First-order month")
save(fig, "06_cohort_retention")
findings["avg_retention_pct"] = {int(p): float(retention[p][retention[p] > 0].mean())
                                 for p in range(1, 4)}

# %% [markdown]
# ## 9. Delivery speed vs customer rating

# %%
rated = orders[(orders["status"] == "Delivered") & orders["rating"].notna()].copy()
rated["delay_bucket"] = pd.cut(rated["delay_days"], [-1, 0, 2, 4, 99],
                               labels=["On time", "1–2 days late", "3–4 days late", "5+ days late"])
dly = rated.groupby("delay_bucket", observed=True)["rating"].agg(["mean", "size"])
dly.to_csv(TABLES / "delay_vs_rating.csv")

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(dly.index.astype(str), dly["mean"], color=[ACCENT, MUTED, "#e0a43a", ALERT])
ax.set_ylim(1, 5)
ax.set_title("Average rating by delivery delay")
ax.set_ylabel("Avg rating (1–5)")
save(fig, "07_delay_vs_rating")

city_ops = (orders.merge(customers[["customer_id", "city"]], on="customer_id")
                  .query("status == 'Delivered'")
                  .groupby("city").agg(avg_delivery_days=("delivery_days", "mean"),
                                       avg_rating=("rating", "mean"), orders=("order_id", "size"))
                  .sort_values("avg_delivery_days"))
city_ops.to_csv(TABLES / "city_delivery.csv")
findings["delay_vs_rating"] = {str(i): float(r["mean"]) for i, r in dly.iterrows()}
findings["slowest_cities"] = {c: {"days": float(r.avg_delivery_days), "rating": float(r.avg_rating)}
                              for c, r in city_ops.tail(3).iterrows()}
findings["fastest_cities"] = {c: {"days": float(r.avg_delivery_days), "rating": float(r.avg_rating)}
                              for c, r in city_ops.head(3).iterrows()}

# %%
with open(ROOT / "outputs/findings.json", "w") as f:
    json.dump(findings, f, indent=2, default=float)
print(json.dumps(findings, indent=2, default=float))
