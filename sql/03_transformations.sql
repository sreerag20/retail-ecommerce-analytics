use retail_portfolio;

# View 1: Enriched Orders
create or replace view vw_orders_enriched as 
select
    o.*, 
    o.revenue - o.cost as profit,
    datediff(o.ship_date, o.order_date) as days_to_ship,
    year(o.order_date) as order_year,
    month(o.order_date) as order_month,
    quarter(o.order_date) as order_quarter,
    dayname(o.order_date) as order_weekday,
    case
        when o.revenue < 500 then 'Low'
        when o.revenue < 2000 then 'Medium'
        when o.revenue < 10000 then 'High'
        else 'Premium'
    end as revenue_tier,
    c.segment, c.region as customer_region,
    c.status as customer_status, 
    p.category, p.subcategory, p.is_active as product_is_active, 
    l.state, l.territory, 
    r.team as rep_team, r.manager as rep_manager
from fact_orders o
left join dim_customers c on o.customer_id = c.customer_id
left join dim_products p on o.product_id = p.product_id
left join dim_locations l on o.location_id = l.location_id
left join dim_sales_reps r on o.rep_id = r.rep_id;

# View 2: Monthly Revenue
create or replace view vw_monthly_revenue as 
select
    date_format(order_date, '%Y-%m-01') as month_start,
    sum(revenue) as total_revenue,
    sum(revenue - cost) as total_profit,
    count(*) as order_count,
    avg(revenue) as avg_order_value
from vw_orders_enriched
where status = 'Completed'
group by month_start
order by month_start;

# View 3: RFM
create or replace view vw_rfm as
select
    customer_id,
    datediff('2025-01-01', max(order_date)) as recency_days,
    count(distinct order_id) as frequency,
    sum(revenue) as monetary_value
from fact_orders
where status = 'Completed'
group by customer_id;

# View 4: Cohort
create or replace view vw_cohort as
select
    c.customer_id, 
    date_format(c.join_date, '%Y-%m') as cohort_month, 
    date-format(min(o.order_date), '%Y-%m') as first_order_month,
    timestampdiff(month, c.join_date, min(o.order_date)) as months_to _first_order
from dim_customers c
left join fact_orders o on c.customer_id = o.customer_id
group by c.customer_id, c.join_date;
