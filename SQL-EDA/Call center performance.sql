-- Call Center Performance

-- KPI 1 — Total Calls

-- How many calls were made during the entire collection period?

SELECT COUNT(*) FROM Call_Interactions

-- KPI 2 — Calls by Day
-- On which dates did collectors make the most calls?

SELECT Call_Date, COUNT(*) AS Total_Calls
FROM Call_Interactions
GROUP BY Call_Date
ORDER BY Total_Calls DESC;

-- KPI 3 — Calls by Hour
-- At what hour of the day are collectors placing the most calls?

SELECT DATEPART(hour, Call_Time) AS Call_Hour, COUNT(*) AS Total_Calls
FROM Call_Interactions
GROUP BY DATEPART(hour, Call_Time)
ORDER BY Total_Calls DESC;

-- KPI 4 — RPC Rate
-- Percentage of calls that resulted in Right Party Contact (RPC).
-- Check
SELECT
	SUM(CASE WHEN Dial_Result='Right Party Contact' THEN 1 ELSE 0 END) * 100 / COUNT(*) AS RPC_Percent
FROM Call_Interactions;

-- KPI 5 — Contact Rate
-- Percentage of calls where any contact was made.

SELECT
	(SELECT COUNT(*)
		FROM Call_Interactions
		WHERE Dial_Result IN ('Right Party Contact', 'Voicemail')) * 100 / COUNT(*) AS Percent_Contact
FROM Call_Interactions;

-- KPI 6 — Average Talk Time
-- How long do collectors spend on a call, on average?

-- Considering Calls with 0 seconds as that is one call as well
SELECT AVG(Talk_Time_Seconds) AS Avg_Talk_Time
FROM Call_Interactions;

-- Considering Calls with 0 seconds as no call
SELECT
	SUM(Talk_Time_Seconds) / 
		(SELECT COUNT(Talk_Time_Seconds) AS Call_Count
		FROM Call_Interactions
		WHERE Talk_Time_Seconds > 1)
FROM Call_Interactions;

-- KPI 7 — Average RPC Talk Time
-- Calculate average talk time only for RPCs.

SELECT AVG(Talk_Time_Seconds)
FROM Call_Interactions
WHERE Dial_Result = 'Right Party Contact';

-- KPI 8 — Dial Result Distribution
-- How many calls ended with each Dial Result?

SELECT Dial_Result, COUNT(*) AS Total_Calls
FROM Call_Interactions
GROUP BY Dial_Result
ORDER BY Total_Calls DESC;

-- KPI 9 — Which Phone Source Performs Best?
-- Which Phone Source has the highest RPC rate?
-- Total Calls, Total RPC Calls, RPC %

WITH call_type AS (
	SELECT 
		p.Phone_Source AS Phone_Source,
		COUNT(c.Call_ID) AS Total_Calls,
		SUM(
	CASE 
		WHEN c.Dial_Result = 'Right Party Contact' THEN 1
		ELSE 0
	END
) AS RPC_Calls
	FROM Call_Interactions c
	LEFT JOIN Phone_Numbers p
	ON c.Phone_ID = p.Phone_ID
	GROUP BY p.Phone_Source
)
SELECT
	Phone_Source,
	Total_Calls,
	RPC_Calls,
	CAST((RPC_Calls * 100.0) / Total_Calls AS DECIMAL (5,2)) AS Percent_Calls
FROM call_type
ORDER BY Percent_Calls DESC;

-- KPI 10
-- Which Phone Type Performs Best?

WITH call_type AS (
	SELECT 
		p.Phone_Type AS Phone_Type,
		COUNT(c.Call_ID) AS Total_Calls,
		SUM(
	CASE 
		WHEN c.Dial_Result = 'Right Party Contact' THEN 1
		ELSE 0
	END
) AS RPC_Calls
	FROM Call_Interactions c
	LEFT JOIN Phone_Numbers p
	ON c.Phone_ID = p.Phone_ID
	GROUP BY p.Phone_Type
)
SELECT
	Phone_Type,
	Total_Calls,
	RPC_Calls,
	CAST((RPC_Calls * 100.0) / Total_Calls AS DECIMAL (5,2)) AS Percent_Calls
FROM call_type
ORDER BY Percent_Calls DESC;