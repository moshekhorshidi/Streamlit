import streamlit as st
import datetime
import pandas as pd
import time

# ui function section 
# section 1 on ui

st.set_page_config(page_title = 'Moshe khorshidi Report Manager',page_icon='📊')

# UI info welcome text
st.title("Azure Store Report Manager UI")
st.write("Welcome to report manager and azure database exploration ***Web application***, developed by **Moshe Khorshidi**.")
st.write("***Phone: +972-526775714 , eMail: MosheKhorshidi@gmail.com***, ***LinkedIn:*** [My LinkedIn Profile 👋](https://www.linkedin.com/in/moshe-khorshidi-sql-python-tableau-data-analysis-bi-engineering-curiosity-for-innovation/) ")

# information message to user on test connection on azure database
st.info("Users can be **offline and get un-updated data from azure server**, for better usage test your connection first.")

# test connection on azure database
st.caption("**👇 Please Test Coonection to Azure SQL database**")
if st.button("Test Connection To Database Server", key = 1):
    
    try:

        progress_text = "Test Connection in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
            
        for percent_complete in range(100):
            time.sleep(0.03)
            my_bar.progress(percent_complete + 1, text=progress_text)
        my_bar.empty()
        st.success(f"Azure SQL Database session is **active**  :sunglasses: , time established:  **{datetime.datetime.now()}**", icon="✅")


    except: 
            exception_message = '**Click F5 to reload page and Try to test connection again! Connection not active, user see not updated data (WebApp offline)**'
            st.info(exception_message)




# UI info on section 1 of the webapp
st.subheader("My Project Database Tables",divider='violet')
#st.header("Azure Database Tables Exploration", divider='violet')
#st.subheader("Select a table you want to explore Raw data on:")

st.markdown("Click **'See table names button'** to see tables names on my database") 

if st.button("See Database tables names", key = 2):

    result = pd.read_csv('table_names.csv')

    if result.all:
        
        st.write("***Table names on Azure datbase:***")
        st.write(result)
        TableNamesQueryText = """

        /*Azure SQL query snippet*/

        SELECT distinct 
                t.name as "Table Name",
                s.name as "Schema Name",
                s.schema_id as "Schema ID"
        FROM sys.tables t inner join sys.schemas s
            ON t.schema_id = s.schema_id
        where t.name not in('Customer', 'ErrorLog')
        and s.name = 'SalesLT'
        union 
        select name,'SalesLT', schema_id 
        from sys.views

            """
        st.code(TableNamesQueryText, language='sql')
        st.button("Close tables names and code snipp", key = 3)
        
    else:
        
        data_container = st.empty()  # Create an empty container
        data_container.info("No Data on this table: empty result")     
   
# section 2 on ui - sql reports 

st.subheader("My Company C level Database Reports", divider='violet')
#st.header("Company Azure Database Reports", divider='violet')

reports_options = st.selectbox('***Select your relevant report***',
                         ('No report selected','Customer Ranking Report','Sales Person details','Product Revenue Report'
                          ,'Customers Taxes Report'))
reports_massege = st.write("***Report that will execute and Presented is:***", reports_options) 
user_choosen_report = reports_options

if st.button("Execute Report"):
    if user_choosen_report == 'Customer Ranking Report':
        result = pd.read_csv('customer_ranking_report.csv')
        st.dataframe(result)
        Customer_Ranking_Report_code = """ 

        /*Azure SQL query snippet*/

        select 

            RANK() over (order by sum(sod.OrderQty) desc) as "Customer Ranking",
            cast(c.customerid as varchar(25)) as "Customer ID",
            c.CompanyName as "Company Name",
            CONCAT(FirstName,' ' ,LastName) as "Full Name",
            case when Title = 'Mr.' then 'M'
                    when Title = 'Ms.' then 'F'
            else null end as "Gender",
            count(soh.salesOrderID) as "Total Orders",
            sum(sod.OrderQty) as "Total Quentity Orderd",
            round(sum(sod.linetotal),3) as "Total revenue from customer $" 

        from SalesLT.Customer c 
        LEFT JOIN SalesLT.CustomerAddress ca 
            ON c.customerid = ca.customerid
        LEFT JOIN SalesLT.SalesOrderHeader soh
            ON soh.customerid = c.customerid
        LEFT JOIN SalesLT.salesOrderDetail sod
            ON sod.salesOrderID = soh.salesOrderID
        group by c.customerid, Title , CONCAT(FirstName,' ' ,LastName), c.CompanyName
        having count(soh.salesOrderID) > 0 

                     """
        st.code(Customer_Ranking_Report_code, language='sql') 
        st.button("close report")
    
    elif user_choosen_report == 'Sales Person details':
         result = pd.read_csv('Salesperson_info.csv')
         st.table(result)
         Sales_Person_details = """
                
            ***Azure SQL query snippet:***
                  
                select 	distinct 
                    rank() over (order by sum(totaldue) desc) as "Salesperson Ranking",
                    trim(' 1 2 3 4 5 6 7 8 9 0 ' from trim('\ ' from trim('adventure-works' FROM cust.salesperson))) as "Sales Person",
                    count(distinct cust.customerid) as "Total Customers Sale",
                    sum(totaldue) as "Total Revenue from Salesperson",
                    lag(sum(totaldue)) over (order by sum(totaldue) desc) - sum(totaldue) as "Salesperson Difference", 
                    round((lag(sum(totaldue)) over (order by sum(totaldue) desc) - sum(totaldue))*100.0/
                    lag(sum(totaldue)) over (order by sum(totaldue) desc),3) as " (%) Gap Percentage"
                from SalesLT.Customer cust
                inner join SalesLT.SalesOrderHeader sod 
                    on cust.customerid = sod.customerid
                group by trim(' 1 2 3 4 5 6 7 8 9 0 ' from trim('\ ' from trim('adventure-works' FROM cust.salesperson)))
                  
                    """
         
         st.code(Sales_Person_details, language='sql') 
         st.button("close report")

    elif user_choosen_report == 'Product Revenue Report':
        result = pd.read_csv('Product_Revenue_Report.csv')
        st.write(result)
        Product_Revenue_Report = """ 

                ***Azure SQL query snippet:***

    
                    with report as (
                    
                    SELECT distinct
                    pc.name as "Category name",
                    p.name as "Detailed Product name",
                    listprice as "Product Price",
                    sum(orderqty) over ( partition by pc.name, p.name, listprice order by pc.name ) as "total qty orderd",
                    sum(TotalDue) over ( partition by pc.name, p.name, listprice order by pc.name ) as "($) Total Revenue From product"
                    FROM [SalesLT].[Product] as p
                    inner join [SalesLT].[ProductCategory] as pc
                           on p.ProductCategoryid = pc.ProductCategoryid
                    inner join [SalesLT].ProductModel as pm
                           on pm.ProductModelid = p.ProductModelid
                    inner join [SalesLT].ProductModelProductDescription as pmp
                           on pmp.ProductModelid = p.ProductModelid
                    inner join [SalesLT].SalesOrderDetail as sod
                           on sod.productid = p.productid
                    inner join [SalesLT].SalesOrderHeader soh  
                           on soh.salesorderid = sod.salesorderid ) 


                    select RANK() over ( order by "Total Revenue From product" desc ) AS "Detailed Product Revenue Rank", 
                              report.* 
                    from report 

                     """
        st.code(Product_Revenue_Report, language='sql') 
        st.button("close report")

    elif user_choosen_report == 'Customers Taxes Report':
        result = pd.read_csv('Customers_Taxes_Report.csv')
        st.dataframe(result)
        
        Customers_taxes_report = """ 

                ***Azure SQL query snippet:***

                        with Tax_Info as (

                        SELECT distinct
                        cast(sod.SalesOrderID as varchar(25) ) as "Sales Order ID",
                        c.CompanyName as "Company Name",
                        concat(c.firstname, ' ', c.lastname) as "Full Name",
                        TaxAmt as "Taxes Amount",
                        Freight as "Freight Amount",
                        sum(sod.OrderQty) over (partition by sod.SalesOrderID  order by sod.SalesOrderID ) as "Total Order Quentity"
                        FROM [SalesLT].[Product] as p
                        inner join [SalesLT].SalesOrderDetail as sod
                               on sod.productid = p.productid
                        inner join [SalesLT].SalesOrderHeader soh  
                               on soh.salesorderid = sod.salesorderid
                        inner join [SalesLT].customer c 
                                  on c.customerid = soh.customerid
                        ) 

                        select rank() over(order by "Taxes Amount" desc) as "Tax Ranking For Customer", Tax_Info.*
                        from Tax_Info 

                     """
        st.code(Customers_taxes_report,language='sql')
        st.button("Close report") 

    else:
         st.info("""
                 
                **Report not selected**
                 
                User guide check:

                1. Not empty selection or default value - "No report selected"
                2. Check if report was selected properly from list of reports
                3. try to test connection again
                 
                 """)
         
         st.button("Close user check")
         
         
      
st.subheader("My Company C level Data Visualization",divider='violet')

vizz_options = st.selectbox("***Select your Vizz and click analyze visual***",
                         ('No Vizz selected','Top Ranking Customers by Quentity Orderd','Top Ranking Customers by Revenue'))
vizz_massege = st.write("Vizz Presented: ", vizz_options) 
user_choosen_vizz = vizz_options

if st.button("Analyze Visual"):
    if user_choosen_vizz == 'Top Ranking Customers by Quentity Orderd':
        result = pd.read_csv('top_ranking_report_customers_qty.csv')
        
        chart_data = result

        st.bar_chart(chart_data,x="Vizz Company Rank", y=["Total Quentity Orderd","Total Orders"])


        vizz_text = "***Note: Analyze top ranked customers by the total orders and quantity of products purchasing***"
        
        st.info(vizz_text)
        
        st.button("Close Selected Vizz")

    elif user_choosen_vizz == 'Top Ranking Customers by Revenue':
        result = pd.read_csv('top_ranking_report_customers_revenue.csv')
        
        chart_data = result
        
        st.bar_chart(chart_data,x="Vizz Company Rank", y="($) Total revenue from customer")


        vizz_text = "***Note: Analyze top ranked customers by the revenue inserted to the company***"
        
        st.info(vizz_text)
        
        st.button("Close Selected Vizz")
    
    else:
         
         st.info("""
                 
                **Vizz not selected**
                 
                User guide check:

                1. Not empty selection or default value - "No Vizz selected"
                2. Check if report was selected properly from list of reports
                3. try to test connection again
                 
                 """)
         
         st.button("Close user check")
