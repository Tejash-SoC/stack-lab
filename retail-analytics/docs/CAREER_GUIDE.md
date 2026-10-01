# Turning this project into interviews

## 1. Be honest about the data, then make it stronger
Say "simulated dataset" in the README and in interviews. Interviewers respect that far more than
being caught out. The strongest move is to **repeat the analysis on a real dataset** so you can
say you did both:

- Search Kaggle for **"Olist Brazilian E-Commerce"** (orders, items, customers, products, reviews,
  payments). It has the same table shape as this project, so `analysis.py` and `queries.sql` port
  over with column renames. Other good options: **Superstore Sales**, **Online Retail II (UCI)**.
- Keep both versions in the repo: `/simulated` and `/olist`. Two projects with one method shows range.

## 2. Add a dashboard (this is what recruiters click on)
Build a one-page dashboard in **Power BI Desktop** (free) or **Tableau Public** (free):
1. Load `outputs/tables/*.csv` plus `data/orders.csv`, `order_items.csv`, `products.csv`, `customers.csv`.
2. Relationships: orders → customers, order_items → orders, order_items → products.
3. Measures: `Revenue = SUMX(order_items, products[list_price]*order_items[quantity]*(1-order_items[discount_pct]/100))`,
   `Profit`, `Margin %`, `Repeat Rate`.
4. Page layout: 4 KPI cards on top (Revenue, Profit, Margin %, Repeat rate), monthly revenue line,
   category revenue vs margin, discount-margin heatmap (matrix), RFM segment bar, slicers for
   year / city / channel.
5. Publish to Power BI Service or Tableau Public and put the **link at the top of your README**.
6. Screenshot it into `docs/dashboard.png` and embed it in the README.

## 3. Publish
- GitHub repo named `retail-sales-profit-analysis`, with this README, the charts embedded
  (`![](outputs/charts/03_discount_margin_heatmap.png)`), and a clear commit history.
- Pin it on your profile. Add the dashboard link and repo link to your LinkedIn "Featured" section.
- Write a short LinkedIn post: the headline finding (*"Electronics was 73% of revenue at an 8% margin,
  and 30% discounts lost money on every sale"*), one chart, and the repo link.

## 4. Resume bullets (edit the numbers to match what you actually did)
- Analysed 6,000 orders across 3,000 customers (simulated retail dataset) using Python and SQL;
  found Electronics drove 73% of revenue at an 8% margin and recommended capping discounts at 15%.
- Cleaned messy data (removed 59 duplicate orders, standardised 19 city spellings to 10) and wrote
  9 SQL queries using CTEs, joins and window functions (LAG, RANK) to validate Python results.
- Segmented customers with RFM and cohort analysis; showed Champions are 7% of customers but 19% of
  revenue and identified 1,234 repeat customers at churn risk for a win-back campaign.
- Built an interactive Power BI dashboard with KPI cards and slicers (add once you build it).

## 5. Interview questions this project prepares you for
- **Walk me through the project.** Question, data, cleaning, 3 key findings, recommendation, what you'd do next.
- **How did you handle dirty data?** Duplicates, inconsistent categories, missing values, and why cancelled orders are excluded.
- **Why is revenue the wrong metric on its own?** Electronics: biggest revenue, thinnest margin.
- **What is RFM and why those thresholds?** Be ready to say the cutoffs were a judgement call.
- **How would you test that Referral customers really are better?** A/B or at least a significance test; note channels aren't randomised.
- **What are the limitations?** Simulated data, no shipping/return costs, no significance tests.
- **SQL:** write a window-function query live (running total, MoM growth, top-N per group). Practise these on LeetCode SQL 50 or StrataScratch.

## 6. A 7-day plan
| Day | Do |
|---|---|
| 1 | Run everything locally. Read every line of `analysis.py` until you can explain it without notes. |
| 2 | Redo the SQL queries from scratch in your own words. Add two of your own. |
| 3 | Download Olist (or Superstore) and load it. |
| 4 | Port the analysis to the real data. Note which findings change. |
| 5 | Build the Power BI/Tableau dashboard. |
| 6 | Polish the README, push to GitHub, publish the dashboard link. |
| 7 | Post on LinkedIn, rehearse the 2-minute project walkthrough out loud, start applying. |

## 7. Applying
- Target titles: Data Analyst, Junior Data Analyst, Business Analyst, MIS Analyst, Reporting Analyst, Operations Analyst.
- Skills to keep sharp alongside this project: **SQL (most important), Excel (pivots, lookups), one BI tool, basic statistics**.
- Apply daily, tailor the first two lines of your resume summary to each posting, and message the recruiter or hiring manager with the repo link.
