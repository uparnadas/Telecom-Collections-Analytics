-- Broken Promise Analysis
-- The Collections Director wants to identify accounts that frequently make Promises-to-Pay but fail to honor them.

-- Which accounts have the poorest Promise-to-Pay performance, and should therefore be prioritized for follow-up?

SELECT * FROM Promise_To_Pay
ORDER BY Account_ID;

SELECT * FROM Call_Interactions;

WITH PromiseStatus AS (
    SELECT
        Account_ID,
        COUNT(*) AS Total_Promises,
        SUM(
            CASE
                WHEN Promise_Status = 'Kept' THEN 1 ELSE 0 END) AS Kept,
        SUM(
            CASE
                WHEN Promise_Status = 'Broken' THEN 1 ELSE 0 END) AS Broken
    FROM Promise_To_Pay
    GROUP BY Account_ID
),
SuccessRate AS (
    SELECT
        Account_ID,
        Total_Promises,
        Kept,
        Broken,
        CAST((Kept * 100.0) / Total_Promises AS DECIMAL (5,2)) AS Success_Rate
    FROM PromiseStatus
)
SELECT
    Account_ID,
    Total_Promises,
    Kept,
    Broken,
    Success_Rate,
    RANK() OVER (ORDER BY Success_Rate ASC, Broken DESC) AS Success_Rank
FROM SuccessRate;