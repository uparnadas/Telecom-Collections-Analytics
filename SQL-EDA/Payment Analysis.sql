-- Payment Analysis

-- KPI 1 — Total Amount Collected
-- How much money has the agency recovered?

SELECT SUM(Payment_Amount) AS Total_Amount FROM Payments;

-- KPI 2 — Number of Payments
-- How many successful payments have been received?

SELECT COUNT(Payment_Amount) AS Total_Payments FROM Payments;

-- KPI 3 — Average Payment Amount

SELECT CAST(AVG(Payment_Amount) AS DECIMAL(10,2)) AS Avg_Payment FROM Payments;

-- KPI 4 — Recovery Rate
-- Recovered Amount ÷ Outstanding Portfolio Balance × 100

WITH totalpayments AS (
	SELECT 
	Account_ID,
	SUM(Payment_Amount) AS Recovered_Amount 
	FROM Payments
	GROUP BY Account_ID
)

SELECT
	CAST((SUM(Recovered_Amount) * 100.0) / SUM(a.Original_Balance)  AS DECIMAL (10,2)) AS Recovery_Rate
FROM
	totalpayments p
	JOIN Accounts a
ON p.Account_ID = a.Account_ID;

-- KPI 5 — Recovery by Collection Stage
-- Collection Stage, Total Collected, Number of Payments, Average Payment

SELECT
	a.Collection_Stage,
	SUM(p.Payment_Amount) AS Total_Collected,
	COUNT(p.Payment_Amount) AS Total_Payments,
	CAST(AVG(p.Payment_Amount) AS DECIMAL (10,2)) AS Avg_Payment
FROM Accounts a
JOIN Payments p
ON a.Account_ID = p.Account_ID
GROUP BY a.Collection_Stage;

-- KPI 6 — Recovery by Payment Method
-- Which method contributes the highest recovery?

SELECT
	Payment_Method,
	SUM(Payment_Amount) AS Total_Payments
FROM Payments
GROUP BY Payment_Method
ORDER BY Total_Payments DESC;

-- KPI 7 — Recovery by State

SELECT
	a.State,
	SUM(p.Payment_Amount) AS Total_Payments
FROM Accounts a
JOIN Payments p
ON a.Account_ID = p.Account_ID
GROUP BY a.State
ORDER BY Total_Payments DESC;

-- KPI 8 — Recovery by Credit Score Bucket
-- Credit Bucket, Total Collected, Number of Payments, Average Payment

WITH Credit_Bucket AS (
SELECT 
	p.Payment_Amount,
	CASE 
		WHEN a.Credit_Score BETWEEN 300 AND 499 THEN '300-499'
		WHEN a.Credit_Score BETWEEN 500 AND 599 THEN '500-599'
		WHEN a.Credit_Score BETWEEN 600 AND 699 THEN '600-699'
		ELSE '700+'
	END AS Credit_Category
FROM Accounts a
LEFT JOIN Payments p
ON a.Account_ID = p.Account_ID
)
SELECT
	Credit_Category,
	SUM(Payment_Amount) AS Total_Collected,
	COUNT(Payment_Amount) AS Total_Payments,
	CAST(AVG(Payment_Amount) AS DECIMAL (10,2)) AS Avg_Payment
FROM Credit_Bucket
GROUP BY Credit_Category;

-- KPI 9 — Days to First Payment
-- min, max, and avg

WITH paymentdate AS (
	SELECT
		Account_ID,
		MIN(Payment_Date) AS First_Payment
	FROM Payments
	GROUP BY Account_ID
)
SELECT
	MIN(DATEDIFF(day, a.Placement_Date, p.First_Payment)) AS Min_Date_Diff,
	MAX(DATEDIFF(day, a.Placement_Date, p.First_Payment)) AS Max_Date_Diff,
	Avg(DATEDIFF(day, a.Placement_Date, p.First_Payment)) AS Avg_Date_Diff
FROM Accounts a
JOIN paymentdate p 
ON a.Account_ID = p.Account_ID;

-- KPI 10 — PTP Conversion Rate
-- What percentage of promises actually resulted in a payment?

SELECT
    CAST(
        COUNT(DISTINCT Promise_ID) * 100.0 /
        (SELECT COUNT(*) FROM Promise_To_Pay)
    AS DECIMAL(10,2)) AS PTP_Rate
FROM Payments
WHERE Promise_ID IS NOT NULL;

-- RECOMMENDATIONS --

-- Tertiary deserves more collector effort considering the lowest total collections and total payments
-- PTP Rate is 15.11%, which says that collectors are taking promises which are actually converting into payments
