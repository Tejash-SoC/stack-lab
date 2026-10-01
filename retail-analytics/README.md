# Retail Sales, Profit & Customer Retention Analysis

**Tools:** Python (pandas, seaborn), SQL (SQLite: CTEs, window functions), Power BI/Tableau (dashboard guide in `docs/`)

> **About the data:** this is a *simulated* online-retail dataset (3,000 customers, ~6,000 orders,
> 2023–2024, amounts in ₹) created by `data/generate_data.py`. It is deliberately messy (duplicates,
> inconsistent city names, missing values) so the cleaning work is real. The findings below describe
> this simulated business, not a real company.

## Business question
Where does this store make and lose money, which customers are worth keeping, and what should it
change next quarter?

## Key findings

| # | Finding | Evidence |
|---|---|---|
| 1 | **Electronics is 73% of revenue but only an 8% margin.** Beauty, Fashion and Sports are 2.6%, 8.5% and 5.9% of revenue at 43–58% margins. | `02_category_revenue_vs_margin.png` |
| 2 | **Deep discounts destroy profit.** Margin falls from 25% (no discount) to 2% at 20% off and **−16% at 30% off**. Electronics at 30% off loses 21% on every sale. | `03_discount_margin_heatmap.png` |
| 3 | **315 order lines (3.3%) were sold below cost, losing about ₹4.4 lakh.** 99.8% of that loss is Electronics. | `loss_making` in `findings.json` |
| 4 | **Referral and Email customers come back; Social and Paid don't.** Repeat rate: Referral 75%, Email 72%, Organic 60%, Paid Search 46%, Social 35%. Social customers are worth about 40% less per head than Email customers (₹9,963 vs ₹16,619). | `04_channel_revenue_per_customer.png` |
| 5 | **Champions are 7% of customers but 19% of revenue.** Champions + Loyal are 23% of customers and 41% of revenue. 1,234 repeat customers have been silent for 90+ days. | `05_rfm_segments.png`, SQL query 08 |
| 6 | **Retention drops fast.** On average only ~20% of a monthly cohort orders again in month 1 and ~13% in month 3. | `06_cohort_retention.png` |
| 7 | **Late delivery hurts ratings.** On-time orders average 4.43 stars; 3–4 days late 3.71; 5+ days late 2.74. Patna, Lucknow and Jaipur are the slowest cities (6–7 days vs a 5-day promise). | `07_delay_vs_rating.png` |

Revenue grew 18% year on year (₹1.80 Cr to ₹2.12 Cr). Monthly revenue is lumpy and shows no clean
festive peak in 2024, because a handful of high-ticket electronics orders swing each month. Revenue
alone is a noisy signal here, which is another reason to look at margin.

## Recommendations
1. **Cap Electronics discounts at 10–15%.** Anything above 15% takes the category to roughly break-even or a loss. Shift promo budget toward Home & Kitchen, Sports and Fashion, which stay profitable even at 20–30% off.
2. **Move acquisition spend from Social/Paid Search to Referral and Email.** They bring customers who order again.
3. **Run a win-back email to the 1,234 silent repeat customers**, and a second-order incentive in the first 30 days to lift month-1 retention above 20%.
4. **Fix last-mile delivery in Patna, Lucknow and Jaipur** (new courier partner, or an honest 7-day promise there). Each extra late day costs rating points.

## How to run
```bash
pip install -r requirements.txt
python data/generate_data.py   # creates the 4 CSV files in data/
python analysis.py             # cleaning + analysis -> outputs/charts, outputs/tables, outputs/findings.json
python run_sql.py              # same questions answered in SQL -> outputs/sql_results.txt
```
`analysis.py` uses `# %%` cell markers: open it in VS Code (Python extension) and click "Run Cell" to
use it like a notebook. The Python and SQL results agree (₹3.92 Cr revenue, 18.2% margin, 54.5% repeat rate).

## Project structure
```
data/            generate_data.py + the 4 CSVs (customers, products, orders, order_items)
analysis.py      cleaning, KPIs, trend, category, discount, channel, RFM, cohort, delivery analysis
sql/             00_views.sql (clean views) + queries.sql (9 business queries)
run_sql.py       loads CSVs into SQLite and runs the queries
outputs/         charts/, tables/, findings.json, sql_results.txt
docs/            CAREER_GUIDE.md (how to present this and get interviews)
```

## Method notes
- Revenue counts **Delivered** orders only (cancelled and returned orders excluded).
- Revenue = list price × quantity × (1 − discount); profit = revenue − unit cost × quantity.
- 59 duplicate order rows removed; 19 city spellings merged into 10 cities plus "Unknown".
- RFM: recency scored in quintiles, frequency capped at 5 orders, monetary in quintiles.
- Limitations: simulated data, no returns cost or shipping cost in profit, no statistical testing of channel differences.
