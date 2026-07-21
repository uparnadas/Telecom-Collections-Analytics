-- Section 1 — Ranking Functions --
-- Query 1 — Rank States by Outstanding Balance --
-- Which states have the largest outstanding portfolio? --

SELECT
	State,
	SUM(Outstanding_Balance) AS Total_Balance,
	RANK() OVER (ORDER BY SUM(Outstanding_Balance) DESC) AS State_Rank
FROM Accounts
GROUP BY State
ORDER BY State_Rank;

-- Query 2 — Top 10 Highest Balance Accounts --
-- Which accounts currently owe the most money? --

WITH NumberedRows AS (
	SELECT
		Account_ID,
		Account_Number,
		Customer_First_name,
		Customer_Last_Name,
		State,
		Outstanding_Balance,
		ROW_NUMBER() OVER (ORDER BY Outstanding_Balance DESC) AS Acc_Row
	FROM Accounts
)
SELECT * 
FROM NumberedRows
WHERE Acc_Row <= 10
ORDER BY Acc_Row;

-- Query 3 — Rank Collection Stages --
-- Rank collection stages based on total outstanding balance. --

SELECT
	Collection_Stage,
	SUM(Outstanding_Balance) AS Total_Balance,
	DENSE_RANK() OVER (ORDER BY SUM(Outstanding_Balance) DESC) AS Collection_Rank
FROM Accounts
GROUP BY Collection_Stage
ORDER BY Collection_Rank;

-- Query 4 — Divide Accounts into Balance Quartiles --
-- Which accounts fall into the top 25% of balances? --

WITH RankedAccounts AS (
	SELECT
		Account_ID,
		Account_Number,
		State,
		Outstanding_Balance,
		NTILE(4) OVER (ORDER BY Outstanding_Balance DESC) AS Quartile
	FROM Accounts
)
SELECT *
FROM RankedAccounts
ORDER BY Quartile, Outstanding_Balance DESC;

-- How many accounts are in each quartile?

WITH RankedAccounts AS (
	SELECT
		Account_ID,
		Account_Number,
		State,
		Outstanding_Balance,
		NTILE(4) OVER (ORDER BY Outstanding_Balance DESC) AS Quartile
	FROM Accounts
)
SELECT Quartile, COUNT(*) AS No_Of_Accounts
FROM RankedAccounts
GROUP BY Quartile
ORDER BY Quartile DESC;

-- Query 5 — Top 5 Payments per State --
-- What are the five largest payments within each state? --

WITH RankedStates AS (
	SELECT
		a.State,
		p.Payment_ID,
		p.Payment_Amount,
		ROW_NUMBER() OVER (PARTITION BY State ORDER BY p.Payment_Amount DESC) AS State_Rank
	FROM Accounts a
	JOIN Payments p 
	ON a.Account_ID = p.Account_ID
)
SELECT
	State,
	Payment_ID,
	Payment_Amount,
	State_Rank
FROM RankedStates
WHERE State_Rank <=5
ORDER BY State;

----------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------

-- Section 2 — Window Aggregates (5 Queries) --
-- Query 1 - Running Recovery --

SELECT
	Payment_Date,
	Payment_Amount,
	SUM(Payment_Amount) OVER (ORDER BY Payment_Date, Payment_ID) AS Running_Recovery
FROM Payments;

-- Query 2 - Running Payment Count --

SELECT
	Payment_Date,
	Payment_ID,
	COUNT(*) OVER (ORDER BY Payment_Date, Payment_ID) AS Running_Pmt_Count
FROM Payments;	

-- Query 3 - Average Payment by State
-- For every payment, show the average payment amount for that customer's state.

SELECT
	State,
	Payment_ID,
	Payment_Amount,
	AVG(Payment_Amount) OVER(PARTITION BY State) AS Avg_State_Payment
FROM Accounts a
	JOIN Payments p
	ON a.Account_ID = p.Account_ID

-- Query 4 - Compare Each Payment to the State Average
-- Is each payment above or below the average payment for that customer's state?

WITH PaymentStats AS (
	SELECT
		State,
		Payment_ID,
		Payment_Amount,
		CAST(AVG(Payment_Amount) OVER(PARTITION BY State) AS DECIMAL (10,2)) AS Avg_State_Payment
	FROM Accounts a
		JOIN Payments p
		ON a.Account_ID = p.Account_ID
)
SELECT
State,
Payment_ID,
Payment_Amount,
Avg_State_Payment,
CAST((Payment_Amount - Avg_State_Payment) AS DECIMAL (10,2)) AS Diff_From_Average
FROM PaymentStats;

-- Query 3 - Moving Average Payment --
-- 7 Day Moving Average --

SELECT
	Payment_Date,
	Payment_Amount,
	AVG(Payment_Amount) OVER (ORDER BY Payment_Date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS Moving_Average
FROM Payments;

-- Query 4 - Running Calls --

SELECT
	Call_Date,
	Call_ID,
	COUNT(*) OVER (ORDER BY Call_Date) AS Running_Calls
FROM Call_Interactions;

-- Query 5 - Cumulative Portfolio Balance

SELECT
	Placement_Date,
	Collection_Stage,
	Original_Balance,
	SUM(Original_Balance) OVER (PARTITION BY Collection_Stage ORDER BY Placement_Date) AS Cummulative_Balance
FROM Accounts
ORDER BY Collection_Stage, Placement_Date;

----------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------
-- Query 10 - Monthly Recovery Trend
-- How much money was collected each month, and what is the cumulative recovery over the months?


WITH MonthlyPayments AS (
	SELECT
		DATEPART(month, Payment_Date) AS Month,
		SUM(Payment_Amount) AS Monthly_Recovery
	FROM Payments
	GROUP BY DATEPART(month, Payment_Date)
)
SELECT
	Month,
	Monthly_Recovery,
	SUM(Monthly_Recovery) OVER (ORDER BY Month) AS Running_Recovery
FROM
	MonthlyPayments;
----------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------
-- Section 3 — LAG / LEAD (5 Queries)
-- Query 1 - Days Between Consecutive Payments
-- For each account, how many days elapsed between consecutive payments?

WITH Consecutive_Payments AS (
	SELECT
		Account_ID,
		Payment_Date,
		LAG(Payment_Date) OVER (PARTITION BY Account_ID ORDER BY Payment_Date) AS Prev_Date
	FROM Payments
)
SELECT
	Account_ID,
	Payment_Date,
	Prev_Date,
	DATEDIFF(day, Prev_Date, Payment_Date) AS Days_Since_Previous
FROM Consecutive_Payments
ORDER BY Account_ID, Payment_Date;



-- Query 2 - Next payment
-- For each payment, show the next payment made by the same account.
WITH Consecutive_Payments AS (
	SELECT
		Account_ID,
		Payment_Date,
		LEAD(Payment_Date) OVER (PARTITION BY Account_ID ORDER BY Payment_Date) AS Next_Date
	FROM Payments
)
SELECT
	Account_ID,
	Payment_Date,
	Next_Date,
	DATEDIFF(day, Payment_Date, Next_Date) AS Days_To_Next_Payment
FROM Consecutive_Payments
ORDER BY Account_ID, Payment_Date;


-- Query 3 - First Payment per Account
-- For every payment, show the first payment date ever made by that account.

SELECT
	Account_ID,
	Payment_Date,
	FIRST_VALUE(Payment_Date) OVER(PARTITION BY Account_ID ORDER BY Payment_Date) AS First_Payment
FROM Payments
ORDER BY Account_ID, Payment_Date;

-- Query 4 - Latest Payment per Account
-- For every payment, show the latest payment date for that account.

SELECT
	Account_ID,
	Payment_Date,
	LAST_VALUE(Payment_Date) OVER(PARTITION BY Account_ID ORDER BY Payment_Date 
		ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS Last_Payment
FROM Payments
ORDER BY Account_ID, Payment_Date;

-- Query 5 - Largest Payment for Every Account
-- For every payment made by an account, show the largest payment that account has ever made.

SELECT
	Account_ID,
	Payment_ID,
	Payment_Amount,
	MAX(Payment_Amount) OVER (PARTITION BY Account_ID) AS Largest_Payment
FROM Payments
ORDER BY Account_ID, Payment_Amount;
----------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------

-- Query 6 - Payment Percentage of Account Total
-- What percentage of an account's total payments does each payment represent?

WITH PercentPayments AS (
	SELECT
		Account_ID,
		Payment_ID,
		Payment_Amount,
		SUM(Payment_Amount) OVER (PARTITION BY Account_ID) AS Total_Payments_For_Account
	FROM Payments
)
SELECT
	Account_ID,
		Payment_ID,
		Payment_Amount,
		Total_Payments_For_Account,
		CAST((Payment_Amount * 100.0) / Total_Payments_For_Account AS DECIMAL (10,2)) AS Payment_Percentage
FROM PercentPayments;