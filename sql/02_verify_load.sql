use retail_portfolio;

# Row counts for all 5 tables 

select 'fact_orders' as table_name, count(*) as row_count
from fact_orders
union all
select 'dim_customers', count(*) 
from dim_customers
union all
select 'dim_products', count(*) 
from dim_products
union all
select 'dim_locations', count(*) 
from dim_locations
union all
select 'dim_sales_reps', count(*) 
from dim_sales_reps;

# Check for nulls in primary key columns

select 'Null order_id' as check_name, count(*) as count
from fact_orders
where order_id is null
union all
select 'Null customer_id', count(*)
from dim_customers 
where customer_id is null
union all
select 'Null product_id', count(*)
from dim_products
where product_id is null
union all
select 'Null location_id', count(*)
from dim_locations 
where location_id is null
union all
select 'Null rep_id', count(*)
from dim_sales_reps 
where rep_id is null;

# Check date columns are loaded correctly

select order_date, ship_date
from fact_orders
limit 5;
