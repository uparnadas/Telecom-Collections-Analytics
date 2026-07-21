-- Promise to Pay Analysis

-- KPI 1 — Overall PTP Rate
-- What percentage of RPCs resulted in a Promise to Pay?

SELECT
CAST((SUM(CASE WHEN Promise_To_Pay = '1' THEN 1 ELSE 0 END)) * 100.00 / 
	SUM(CASE WHEN Dial_Result = 'Right Party Contact' THEN 1 ELSE 0 END) AS DECIMAL (5,2))
FROM Call_Interactions;

-- KPI 2 — PTP Rate by Collection Stage
-- Which collection stage produces the most promises?

WITH RPC AS (
	SELECT
		a.Collection_Stage,
		SUM(CASE WHEN c.Dial_Result = 'Right Party Contact' THEN 1 ELSE 0 END) AS Total_RPC
	FROM Accounts a
	LEFT JOIN Call_Interactions c
	ON a.Account_ID = c.Account_ID
	GROUP BY a.Collection_Stage
),
PTP AS (
	SELECT 
		a.Collection_Stage,
		COUNT(p.Promise_ID) AS Total_Promise
	FROM Accounts a
	LEFT JOIN Promise_To_Pay p
	ON a.Account_ID = p.Account_ID
	GROUP BY a.Collection_Stage
)

SELECT
	r.Collection_Stage,
	r.Total_RPC,
	pt.Total_Promise,
	CAST(
		(pt.Total_Promise * 100.0) / NULLIF(r.Total_RPC, 0)
	AS DECIMAL(5,2)) AS PTP_Rate
FROM RPC r
JOIN PTP pt
ON r.Collection_Stage = pt.Collection_Stage
ORDER BY PTP_Rate DESC;


-- KPI 3 — Promise Status Distribution
-- How many promises are: Active, Kept, Broken

SELECT 
	Promise_Status,
	COUNT(*) AS Total_Promise
FROM Promise_To_Pay
GROUP BY Promise_Status;

-- KPI 4 — Promise Fulfillment Rate
-- What percentage of all promises were fulfilled?

SELECT
	CAST((SUM(CASE WHEN Promise_Status = 'Kept' THEN 1 ELSE 0 END)) * 100.00 / COUNT(*) AS DECIMAL (5,2))
FROM Promise_To_Pay;

-- KPI 5 — Average Promised Amount
-- Considering all Promises as fulfilled promises are Payments in other words,
-- and we are trying to analyse accounts converted to promises

SELECT AVG(Promised_Amount) AS Avg_promise
FROM Promise_To_Pay;

-- KPI 7 — Fulfillment Rate by Collection Stage
-- For each collection stage calculate: Total promises, Fulfilled promises, Fulfillment %

WITH Promise AS (
	SELECT 
		a.Collection_Stage,
		COUNT(p.Promise_ID) AS Total_Promise,
		SUM(CASE WHEN p.Promise_Status = 'Kept' THEN 1 ELSE 0 END) AS Fulfilled_Promise
	FROM Accounts a
	LEFT JOIN Promise_To_Pay p
	ON a.Account_ID = p.Account_ID
	GROUP BY a.Collection_Stage
)
SELECT
	Collection_Stage,
	Total_Promise,
	Fulfilled_Promise,
	CAST(
		(Fulfilled_Promise * 100.0) / NULLIF(Total_Promise, 0)
	AS DECIMAL(5,2)) AS Fulfilled_Percent
FROM Promise 
ORDER BY Fulfilled_Percent DESC;

-- KPI 8 — Average Promise Amount by Collection Stage
-- Which stage secures the largest commitments?

SELECT
		a.Collection_Stage,
		AVG(p.Promise_ID) AS Avg_Fulfilled
	FROM Accounts a
	LEFT JOIN Promise_To_Pay p
	ON a.Account_ID = p.Account_ID
	GROUP BY a.Collection_Stage;

-- KPI 9 — Credit Score vs Promise Fulfillment
-- For each bucket determine: Total promises, Fulfilled promises, Fulfillment %

WITH Credit_Bucket AS (
SELECT 
	p.Promise_ID,
	p.Promise_Status,
	CASE 
		WHEN a.Credit_Score BETWEEN 300 AND 499 THEN '300-499'
		WHEN a.Credit_Score BETWEEN 500 AND 599 THEN '500-599'
		WHEN a.Credit_Score BETWEEN 600 AND 699 THEN '600-699'
		ELSE '700+'
	END AS Credit_Category
FROM Accounts a
LEFT JOIN Promise_To_Pay p
ON a.Account_ID = p.Account_ID
)

SELECT
	Credit_Category,
	COUNT(Promise_ID) AS Total_Promise,
	SUM(CASE WHEN Promise_Status = 'Kept' THEN 1 ELSE 0 END) AS Fulfilled_Promise,
	CAST(
		SUM(CASE WHEN Promise_Status = 'Kept' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(Promise_ID), 0)
	AS DECIMAL(5,2)) AS Fulfilled_Percent
FROM Credit_Bucket
GROUP BY Credit_Category;

-- KPI 10 — States with Highest Broken Promise Rate
-- For each state calculate: Total promises, Broken promises, Broken %

WITH Promise AS (
	SELECT 
		a.State,
		COUNT(p.Promise_ID) AS Total_Promise,
		SUM(CASE WHEN p.Promise_Status = 'Broken' THEN 1 ELSE 0 END) AS Broken_Promise
	FROM Accounts a
	LEFT JOIN Promise_To_Pay p
	ON a.Account_ID = p.Account_ID
	GROUP BY a.State
)
SELECT
	State,
	Total_Promise,
	Broken_Promise,
	CAST(
		(Broken_Promise * 100.0) / NULLIF(Total_Promise, 0)
	AS DECIMAL(5,2)) AS Broken_Percent
FROM Promise 
ORDER BY Broken_Percent DESC;

-- INSIGHTS --

-- Customers in Tertiary Stage are more likely to keep promises.
-- Lower credit score customers have a higher broken promise rate.
-- State Illinois has unusually poor fulfillment.