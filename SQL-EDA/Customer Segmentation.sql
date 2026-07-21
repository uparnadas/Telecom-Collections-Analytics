-- Customer Segmentation

-- How many accounts fall into each Credit Score band?

-- 300–499
-- 500–599
-- 600–699
-- 700+

-- What is the average outstanding balance for each credit score band?

WITH Credit_Bucket AS (
SELECT 
	Credit_Score,
	Outstanding_Balance,
	CASE 
		WHEN Credit_Score BETWEEN 300 AND 499 THEN '300-499'
		WHEN Credit_Score BETWEEN 500 AND 599 THEN '500-599'
		WHEN Credit_Score BETWEEN 600 AND 699 THEN '600-699'
		ELSE '700+'
	END AS Credit_Category
FROM dbo.Accounts
)
SELECT
	Credit_Category,
	COUNT(*) AS Total_Accounts,
	CAST(AVG(Outstanding_Balance) AS DECIMAL(10, 2)) AS Avg_Balance
FROM Credit_Bucket
GROUP BY Credit_Category;


-- How many accounts fall into each Days Past Due (DPD) bucket?

-- 30–59
-- 60–89
-- 90–119
-- 120+

WITH PastDue AS (
SELECT
	Days_Past_Due,
	CASE
		WHEN Days_Past_Due BETWEEN 30 AND 59 THEN '30-59'
		WHEN Days_Past_Due BETWEEN 60 AND 89 THEN '60-89'
		WHEN Days_Past_Due BETWEEN 90 AND 119 THEN '90-119'
		ELSE '120+'
	END AS Past_Due_Category
FROM dbo.Accounts
)
SELECT 
	Past_Due_Category,
	COUNT(*) AS Total_Accounts
FROM PastDue
GROUP BY Past_Due_Category
ORDER BY Past_Due_Category;

-- Which State has the highest total outstanding balance?

SELECT 
	TOP 1 State, 
	SUM(Outstanding_Balance) AS Total_Balance
FROM dbo.Accounts
GROUP BY State
ORDER BY Total_Balance DESC;

-- Which State has the highest average balance?

SELECT 
	TOP 1 State, 
	AVG(Outstanding_Balance) AS AVG_Balance
FROM dbo.Accounts
GROUP BY State
ORDER BY AVG_Balance DESC;

-- Which State has the most accounts?

SELECT 
	TOP 1 State, 
	COUNT(*) AS Total_Accounts
FROM dbo.Accounts
GROUP BY State
ORDER BY Total_Accounts DESC;