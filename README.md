# Coderhouse's Data Engineering Example Final Project
### Developed by Sol De Benedet
## Requirements
Have Docker
## Description
This code gives you all the tools to run the specific DAG called ETL_products.

# What this DAG does is:

* Creates a table in Readshift with data about products of an ecommerce
* Pulls data from the [Store API](https://storerestapi.com/)
* Merges the data with additional data of products stock and sales. 
* Saves that merged data into a Redshift Database (simulating a Data Warehouse).
* Checks if there is any oversold product. If there is, it sends an email to whatever address is configured in .env alerting about the anomaly.
* Send a notification email to inform the execution of the process

![alt text](https://github.com/curlydaria/coderhouse-data-engineer/blob/master/dag_screenshot.png)
