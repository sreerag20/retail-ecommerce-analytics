# Retail & E-Commerce Data Analytics Portfolio

## Project Overview
End-to-end data analytics pipeline for a retail/e-commerce dataset.
Built using Python, MySQL, and Power BI across 7 stages.

## Tools & Technologies
- **Python** — Data generation, cleaning, and transformation (Pandas, Faker, SQLAlchemy)
- **MySQL** — Star schema design, SQL queries, views, and data validation
- **Power BI** — Interactive dashboard with 7 visualisations and DAX measures
- **Jupyter Notebooks** — Step-by-step documented analysis

## Dataset Summary
| Table | Rows | Description |
|-------|------|-------------|
| fact_orders | 5,000+ | Core fact table — orders, revenue, cost, status |
| dim_customers | 1,000 | Customer dimension — segments, regions, RFM base |
| dim_products | 200 | Product catalogue — category, subcategory, price |
| dim_locations | 100 | Geographic dimension — city, state, region |
| dim_sales_reps | 75 | Sales rep lookup — team, manager, hire_date |

## Project Structure
```
retail_portfolio/
├── notebooks/    # Jupyter notebooks (one per stage)
├── scripts/      # Python scripts for data generation and loading
├── sql/          # All SQL files (schema, transformations, validation)
└── reports/      # Dashboard screenshots
```

## Key Features
- Intentional data quality issues injected for realistic cleaning practice
- Star schema with 1 fact table and 4 dimension tables
- RFM customer segmentation and cohort retention analysis
- 7 data validation checks with a rerunnable audit log
- Power BI dashboard with cross-filtering and DAX measures

## How to Run This Project
1. Clone the repository: `git clone https://github.com/YOUR_USERNAME/retail-ecommerce-analytics`
2. Create a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up MySQL and run `sql/01_create_schema.sql`
5. Run scripts in `scripts/` in order to generate and load data
6. Open notebooks in order (Stage_1 through Stage_7)

## Dashboard Preview
*(Add a screenshot of your Power BI dashboard here)*

## Author
**Sreerag A** | Data Analyst
LinkedIn: https://www.linkedin.com/in/sreerag-aj/
