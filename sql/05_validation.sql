use retail_portfolio;

# Check 1: ship_date before order_date
select order_id, order_date, ship_date
from fact_orders
where ship_date < order_date;

# Check 2: Completed orders with zero/null revenue
select order_id, status, revenue
from fact_orders
where status = 'Completed'
and (revenue is null or revenue = 0);

# Check 3: Negative revenue
select order_id, revenue
from fact_orders
where revenue < 0;

# Check 4: Duplicate order_id
select order_id, count(*) as cnt
from fact_orders
group by order_id
having cnt > 1;

# Check 5: Orphaned customer_id
select f.order_id, f.customer_id
from fact_orders f
left join dim_customers c on f.customer_id = c.customer_id
where c.customer_id is null
annd f.customer_id != 'UNKNOWN';

# Check 6: Orphaned product_id
select f.order_id, f.product_id
from fact_orders f
left join dim_products p on f.product_id = p.product_id
where p.product_id is null;

# Check 7: end_date before hire_date
select rep_id, hire_date, end_date
from dim_sales_reps
where end_date is not null
and end_date < hire_date;
