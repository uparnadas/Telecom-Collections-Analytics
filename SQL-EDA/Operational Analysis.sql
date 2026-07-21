-- Operational Analysis

-- KPI 1 — Calls by Hour
-- Which hour of the day sees the highest call volume?

SELECT 
	DATEPART(hour, Call_Time) AS Call_Hour,
	COUNT(*) AS Total_Calls
FROM Call_Interactions
GROUP BY DATEPART(hour, Call_Time)
ORDER BY Total_Calls DESC;

-- KPI 1a - Calls by Day of Week
-- Which weekdays have the highest call volumes?

SELECT
	DATENAME(weekday, Call_Date) AS Week_Day,
	COUNT(Call_ID) AS Total_Calls
FROM Call_Interactions
GROUP BY DATENAME(weekday, Call_Date)
ORDER BY Total_Calls DESC;

-- KPI 2 — RPC Rate by Hour
-- Which calling hour produces the highest Right Party Contact rate?
-- Total Calls, RPC Calls, RPC Rate Grouped by hour

WITH RPC AS (
	SELECT 
		DATEPART(hour, Call_Time) AS Call_Hour,
		COUNT(*) AS Total_Calls,
		SUM(
			CASE
				WHEN Dial_Result = 'Right Party Contact' THEN 1 ELSE 0 END) AS RPC_Calls
	FROM Call_Interactions
	GROUP BY DATEPART(hour, Call_Time)
)
SELECT
	Call_Hour,
	CAST(RPC_Calls * 100.0 / Total_Calls AS DECIMAL (10,2)) AS RPC_Rate
FROM RPC
ORDER BY RPC_Rate DESC;

-- KPI 2a - RPC Rate by Day of Week
-- Which day produces the highest Right Party Contact rate?

WITH RPC AS (
	SELECT 
		DATENAME(weekday, Call_Date) AS Week_Day,
		COUNT(*) AS Total_Calls,
		SUM(
			CASE
				WHEN Dial_Result = 'Right Party Contact' THEN 1 ELSE 0 END) AS RPC_Calls
	FROM Call_Interactions
	GROUP BY DATENAME(weekday, Call_Date)
)
SELECT
	Week_Day,
	CAST(RPC_Calls * 100.0 / Total_Calls AS DECIMAL (10,2)) AS RPC_Rate
FROM RPC;

-- KPI 3 — Average Talk Time by Hour
-- Are longer conversations happening during certain hours?

SELECT 
	DATEPART(hour, Call_Time) AS Call_Hour,
	AVG(Talk_Time_Seconds) AS Avg_Talk_Time
FROM Call_Interactions
GROUP BY DATEPART(hour, Call_Time)
ORDER BY Avg_Talk_Time DESC;

-- KPI 3a - Average Talk Time by Day of Week
-- Are conversations longer on certain days?

SELECT 
	DATENAME(weekday, Call_Date) AS Week_Day,
	AVG(Talk_Time_Seconds) AS Avg_Talk_Time
FROM Call_Interactions
GROUP BY DATENAME(weekday, Call_Date)
ORDER BY Avg_Talk_Time DESC;

-- KPI 4 — Promise Rate by Hour
-- For each hour: Total Calls, PTP Calls, PTP %

SELECT
	DATEPART(hour, Call_Time) AS Call_Hour,
	COUNT(Call_ID) AS Total_Calls,
	SUM(
		CASE
			WHEN Promise_To_Pay = 1 THEN 1 ELSE 0 END) AS PTP_Calls,
	CAST((SUM(CASE WHEN Promise_To_Pay = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(Call_ID) AS DECIMAL (10,2)) AS PTP_Rate
FROM Call_Interactions
GROUP BY DATEPART(hour, Call_Time)
ORDER BY PTP_Rate DESC;		

-- KPI 4a - PTP Rate by Day of Week
-- Which day generates the most promises?

SELECT
	DATENAME(weekday, Call_Date) AS Week_Day,
	COUNT(Call_ID) AS Total_Calls,
	SUM(
		CASE
			WHEN Promise_To_Pay = 1 THEN 1 ELSE 0 END) AS PTP_Calls,
	CAST((SUM(CASE WHEN Promise_To_Pay = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(Call_ID) AS DECIMAL (10,2)) AS PTP_Rate
FROM Call_Interactions
GROUP BY DATENAME(weekday, Call_Date)
ORDER BY PTP_Rate DESC;		


-- KPI 5 — Callback Rate

SELECT
	DATEPART(hour, Call_Time) AS Call_Hour,
	SUM(CASE WHEN Callback_Requested = 1 THEN 1 ELSE 0 END) AS Total_CallBack,
	CAST((SUM(CASE WHEN Callback_Requested = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(Call_ID) AS DECIMAL (5,2)) AS CallBack_Rate
FROM Call_Interactions
GROUP BY DATEPART(hour, Call_Time)
ORDER BY CallBack_Rate DESC;

-- KPI 6 — Settlement Request Rate
-- Which hours generate the most settlement discussions?

SELECT
	DATEPART(hour, Call_Time) AS Call_Hour,
	SUM(CASE WHEN Settlement_Requested = 1 THEN 1 ELSE 0 END) AS Total_Settlement,
	CAST((SUM(CASE WHEN Settlement_Requested = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(Call_ID) AS DECIMAL (5,2)) AS Settlement_Rate
FROM Call_Interactions
GROUP BY DATEPART(hour, Call_Time)
ORDER BY Settlement_Rate DESC;

-- KPI 7 — Payments Received by Day of Week
-- Which day ultimately leads to the most payments?

SELECT
	DATENAME(weekday, Payment_Date) AS Week_Day,
	COUNT(Payment_ID) AS Total_Payments
FROM Payments
GROUP BY DATENAME(weekday, Payment_Date)
ORDER BY Total_Payments DESC;

-- KPI 9 Operational Funnel
-- Total Calls -> Right Party Contacts -> Promises -> Payments

SELECT
	COUNT(Call_ID) AS Total_Calls,
	SUM(CASE WHEN Dial_Result = 'Right Party Contact' THEN 1 ELSE 0 END) AS RPC_Calls,
	CAST((SUM(CASE WHEN Dial_Result = 'Right Party Contact' THEN 1 ELSE 0 END) * 100.0) / COUNT(Call_ID) AS DECIMAL (10,2)) AS RPC_Rate,
	SUM(CASE WHEN Promise_To_Pay = 1 THEN 1 ELSE 0 END) AS Total_Promises,
	CAST((SUM(CASE WHEN Promise_To_Pay = 1 THEN 1 ELSE 0 END) * 100.0) / 
		SUM(CASE WHEN Dial_Result = 'Right Party Contact' THEN 1 ELSE 0 END) AS DECIMAL (10,2)) AS PTP_Rate,
	(SELECT COUNT(Payment_ID) AS Total_Payments FROM Payments) AS Total_Payments,
	CAST((SELECT COUNT(Payment_ID) AS Total_Payments FROM Payments) * 100.0 / 
		SUM(CASE WHEN Promise_To_Pay = 1 THEN 1 ELSE 0 END) AS DECIMAL (10,2)) AS Payment_Rate
FROM Call_Interactions;
	

-- KPI 10 - Overall Collection Dashboard
-- A single-row summary including:Total Calls, RPC Rate, Contact Rate, PTP Rate, PTP Conversion Rate, Recovery Rate, Average Payment, Average Days to First Payment


SELECT
	COUNT(Call_ID) AS Total_Calls,
	
	CAST((SUM(CASE WHEN Dial_Result = 'Right Party Contact' THEN 1 ELSE 0 END) * 100.0) / COUNT(Call_ID) AS DECIMAL (10,2)) AS RPC_Rate,
	
	(SELECT COUNT(Call_ID)
		FROM Call_Interactions
		WHERE Dial_Result IN ('Right Party Contact', 'Voicemail')) * 100 / COUNT(Call_ID) AS Contact_Rate,
	
	CAST((SUM(CASE WHEN Promise_To_Pay = 1 THEN 1 ELSE 0 END) * 100.0) / 
		SUM(CASE WHEN Dial_Result = 'Right Party Contact' THEN 1 ELSE 0 END) AS DECIMAL (10,2)) AS PTP_Rate,
	
	CAST((SELECT COUNT(Payment_ID) FROM Payments) * 100.0 / 
		SUM(CASE WHEN Promise_To_Pay = 1 THEN 1 ELSE 0 END) AS DECIMAL (10,2)) AS PTP_Conversion_Rate,
	
	CAST((SELECT SUM(Payment_Amount) FROM Payments) * 100.0 /
		(SELECT SUM(Original_Balance) FROM Accounts) AS DECIMAL (10,2)) AS Recovery_Rate,
	
	(SELECT CAST(AVG(Payment_Amount) AS DECIMAL(10,2)) FROM Payments) AS Avg_Payment,

	(SELECT AVG(Days_To_First_Payment)
		FROM
		(SELECT 
			a.Placement_Date,
			MIN(p.Payment_Date) AS First_Payment,
			DATEDIFF(day, a.Placement_Date, MIN(p.Payment_Date)) AS Days_To_First_Payment
		FROM Accounts a
		JOIN Payments p 
		ON a.Account_ID = p.Account_ID
		GROUP BY a.Account_ID, a.Placement_Date) t) AS Avg_Days_To_First_Payment

FROM Call_Interactions;