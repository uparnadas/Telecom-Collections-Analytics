## Telecom Collections Analytics

An end-to-end analytics project that helps collections managers prioritize accounts, monitor recovery performance, and improve operational efficiency using Python, SQL Server, and Power BI.

## Project Overview

Collections teams often have thousands of delinquent accounts but limited agent capacity.

Calling every customer isn't practical.

This project demonstrates how analytics can help collections managers identify which accounts should be prioritized, monitor collection performance, and track recovery metrics through an interactive Power BI dashboard.

The project was built using a synthetic telecom collections dataset generated in Python to simulate a realistic collections environment.

## Project Highlights

15K+ synthetic customer accounts
3,00,224 call interaction records
5 relational database tables
5 interactive Power BI report pages
60+ SQL business queries
Custom call prioritization framework

## Business Problem

Collections managers need answers to questions like:

- Which accounts should agents call first?
- Which accounts have the highest recovery potential?
- Which collection stages perform the best?
- How often are customers keeping their Promise to Pay?
- What factors contribute to high-risk accounts?
- How effective are collection efforts over time?

Without a centralized analytics solution, answering these questions requires manually combining data from multiple sources.

## Solution
## This project provides an interactive analytics dashboard that enables managers to:

1) Prioritize accounts using a custom Call Priority Score
2) Monitor recovery performance
3) Analyze Promise-to-Pay trends
4) Track collection stage performance
6) Identify high-risk accounts
7) Support data-driven dialing strategies

## Tech Stack
## Tool                        Purpose
Python                         Synthetic data generation & validation
SQL                            Server	Data storage & business analysis
SQL	                           KPIs, reporting queries & window functions
Power BI	                     Dashboard development
DAX	                           Business measures & calculations

## Dataset
## The project consists of five related tables:

Table	                          Description
Accounts	                      Customer account information
Phone Numbers	                  Contact information
Call Interactions	              Dial attempts and call outcomes
Promise To Pay	                Customer payment commitments
Payments	                      Actual payment transactions

## Data Model

<img width="1536" height="1024" alt="ER Diagram" src="https://github.com/user-attachments/assets/555b6e29-07ce-447a-bd89-fa4e84139bf2" />

## Dashboard Pages

## Home Page
<img width="1179" height="663" alt="HomePage" src="https://github.com/user-attachments/assets/b253391b-8690-4b57-91c3-2d31efa33d1f" />

## Dialing Pool Prioritization
Helps managers identify which accounts should be contacted first based on:

- Risk Category
- Call Priority Score
- Days Past Due
- Outstanding Balance
- Credit Score

<img width="666" height="374" alt="Dialing" src="https://github.com/user-attachments/assets/23354d88-04d3-4920-8c05-3605166b76f1" />

## Executive Overview

High-level KPIs including:

- Total Outstanding Balance
- Recovery %
- Promise Success Rate
- Total Payments
- Collection Stage Performance

<img width="666" height="372" alt="Executive" src="https://github.com/user-attachments/assets/8c99fac2-e5d2-4bb8-9738-d91747232221" />

## Collections Operations

Operational metrics including:

- Call Outcomes
- Right Party Contact Rate
- Promise to Pay trends
- Agent activity

<img width="663" height="371" alt="Operations" src="https://github.com/user-attachments/assets/211ee0e3-bb35-4a63-bd01-593360ccda92" />

## Promise & Recovery

Detailed payment and promise analysis including:

- Promise Fulfillment
- Recovery Trends
- Payment Analysis

<img width="659" height="371" alt="Promise" src="https://github.com/user-attachments/assets/6a8ad2a2-7953-4f99-8057-d01e1a3c176d" />

## Key Features
- Synthetic data generation using Python
- Relational SQL database
- SQL window functions
- Business KPI development
- Custom Call Priority Score
- Risk categorization framework
- Interactive Power BI dashboard
- Performance optimization

## Business KPIs
- Recovery Percentage
- Promise Success Rate
- Right Party Contact Rate
- Collection Stage Performance
- Outstanding Balance
- Total Payments
- High-Risk Accounts
- Dialing Priority Score

## Key Insights

- Pre-Writeoff accounts contribute significantly to recoveries.
- Broken Promise-to-Pay history is a strong indicator of future collection risk.
- High outstanding balances combined with poor payment history require higher dialing priority.
- Collection performance varies across collection stages.

## How to Run
1) Generate the synthetic data using the Python scripts (or use the provided CSV files).
2) Create the SQL Server database and execute the SQL scripts to create the schema and import the data.
3) Open the Power BI .pbix file.
4) Refresh the data model to load the latest data.
5) Explore the interactive dashboards.

## Skills Demonstrated
- Data Modeling
- SQL
- Window Functions
- Data Validation
- Power BI
- DAX
- Business Intelligence
- Dashboard Design
- Performance Optimization
- End-to-End Analytics

## About Me

I'm transitioning into Data Analytics after 8+ years in operations. This project combines my domain knowledge in collections with technical skills in Python, SQL, and Power BI to solve a real-world business problem.

If you'd like to connect or discuss this project, feel free to reach out on LinkedIn.
https://www.linkedin.com/in/uparnadas/

⭐ If you found this project interesting, consider giving it a star!
