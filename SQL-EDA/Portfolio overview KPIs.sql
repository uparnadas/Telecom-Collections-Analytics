-- Portfolio Overview KPIs
-- KPI 1

-- How many active accounts are currently in the portfolio?

SELECT COUNT(*) AS Total_Active_Accounts
FROM dbo.Accounts
WHERE Account_Status = 'Active';

-- All of 1000 Accounts active

-- KPI 2

-- What is the total outstanding balance of all active accounts?


SELECT SUM(Outstanding_Balance) AS Total_Balance
FROM dbo.Accounts
WHERE Account_Status = 'Active';

-- Total Active Balance in Active Accounts is $861261.87

--KPI 3

-- What is the average outstanding balance?

SELECT AVG(Outstanding_Balance) AS Avg_Balance
FROM dbo.Accounts
WHERE Account_Status = 'Active';

-- Average Balance in Active Accounts is $861.261870

-- KPI 4

-- What is the minimum, maximum, and average credit score?

-- Can you return all three values in a single query?

SELECT 
	MIN(Credit_Score) AS Min_Credit_Score,
	MAX(Credit_Score) AS Max_Credit_Score,
	AVG(Credit_Score) AS Avg_Credit_Score
FROM dbo.Accounts;

-- Credit Score range is 435 - 850 and the Average being 646

-- KPI 5

-- How many accounts belong to each Collection Stage?

SELECT Collection_Stage, COUNT(*) AS Total_Accounts
FROM dbo.Accounts
GROUP BY Collection_Stage
ORDER BY Total_Accounts DESC;

-- Highest number of accounts in Primary and Secondary and the lowest in Warehouse

-- KPI 6

-- What is the total outstanding balance by Collection Stage?

SELECT Collection_Stage, SUM(Outstanding_Balance) AS Total_Balance
FROM dbo.Accounts
GROUP BY Collection_Stage
ORDER BY Total_Balance DESC;

-- Highest balance in accounts in Primary and Secondary and the lowest in Warehouse

-- KPI 7

-- What percentage of the portfolio is in each Collection Stage?

SELECT Collection_Stage, 
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dbo.Accounts) AS DECIMAL(10, 2)) AS Percent_Accounts
FROM dbo.Accounts
GROUP BY Collection_Stage
ORDER BY Percent_Accounts DESC;


