-- Executive Dashboard
-- The Head of Collections wants a single SQL query that powers an executive dashboard showing one row per account with all important KPIs

WITH AccountStatus AS (
    -- Days past due > 180
    SELECT 
    a.Account_ID,
    a.Outstanding_Balance,
    a.Days_Past_Due,
    SUM(p.Payment_Amount) AS Total_Payment,
    MAX(p.Payment_Date) AS Last_Payment,
    CAST(SUM(p.Payment_Amount) * 100.0 / SUM(a.Original_Balance) AS DECIMAL (10,2)) AS Recovery_Percent,
    CASE
        WHEN a.Days_Past_Due > 180 THEN 2 ELSE 0
    END AS DPD_Score,
    CASE
        WHEN a.Outstanding_Balance > 10000 THEN 1 ELSE 0 
    END AS Balance_Score,
    CASE
        WHEN a.Credit_Score < 500 THEN 1 ELSE 0 
    END AS Credit_Score
    FROM Accounts a
    JOIN Payments p
    ON a.Account_ID = p.Account_ID
    GROUP BY
    a.Account_ID,
    a.Outstanding_Balance,
    a.Days_Past_Due,
    a.Original_Balance,
    a.Credit_Score
),
PromiseStatus AS (
    -- Broken Promise > 3
    SELECT
        Account_ID,
        SUM(
            CASE
                WHEN Promise_Status = 'Broken' THEN 1 ELSE 0 END) AS Broken_Promise
    FROM Promise_To_Pay
    GROUP BY Account_ID
),
LatestPromise AS (
-- Latest Promise Status
    SELECT
        Account_ID,
        Promise_Status,
        Promise_Date
    FROM (
        SELECT
            Account_ID,
            Promise_Status,
            Promise_Date,
            ROW_NUMBER() OVER (PARTITION BY Account_ID ORDER BY Promise_Date DESC) AS rn
        FROM Promise_To_Pay
    ) p
    WHERE rn = 1
),
RefusalStatus AS (
    -- Refused to pay > 3
    SELECT
    Account_ID,
    SUM(
        CASE
            WHEN Agent_Disposition = 'Refused To Pay' THEN 1 ELSE 0 END) AS Refusal_Stats
    FROM Call_Interactions
    GROUP BY Account_ID
),
LatestCall AS (
-- Latest Call Dial Result
    SELECT *
    FROM (
        SELECT
            Account_ID,
            Dial_Result,
            Call_Date,
            ROW_NUMBER() OVER (
                PARTITION BY Account_ID
                ORDER BY Call_Date DESC
            ) AS rn
        FROM Call_Interactions
    ) c
    WHERE rn = 1
),
Scores AS (
    SELECT
    a.Outstanding_Balance,
    a.Days_Past_Due,
    a.Total_Payment,
    a.Recovery_Percent,
    a.Last_Payment,
    lc.Dial_Result,
    lp.Promise_Status,
    a.DPD_Score,
    a.Balance_Score,
    a.Credit_Score,
    a.Account_ID,
    CASE
        WHEN p.Broken_Promise > 3 THEN 2 ELSE 0
    END AS Broken_Promise_Score,    
    CASE
        WHEN r.Refusal_Stats > 3 THEN 1 ELSE 0
    END AS Refusal_Score
    FROM AccountStatus a
    LEFT JOIN PromiseStatus p
    ON a.Account_ID = p.Account_ID
    LEFT JOIN LatestPromise lp
    ON a.Account_ID = lp.Account_ID
    LEFT JOIN RefusalStatus r
    ON a.Account_ID = r.Account_ID
    LEFT JOIN LatestCall lc
    ON a.Account_ID = lc.Account_ID
),
RiskScores AS (
    SELECT
    Account_ID, 
    (
        ISNULL(Broken_Promise_Score,0)
        + ISNULL(DPD_Score,0)
        + ISNULL(Balance_Score,0)
        + ISNULL(Credit_Score,0)
        + ISNULL(Refusal_Score,0)
    ) AS Risk_Score
    FROM Scores
)
SELECT
    s.Account_ID,
    s.Outstanding_Balance,
    s.Total_Payment,
    s.Recovery_Percent,
    s.Dial_Result,
    s.Promise_Status,
    s.Days_Past_Due,
    CASE
        WHEN Risk_Score >= 4 THEN 'High Risk'
        WHEN Risk_Score >= 3 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS Risk_Category
FROM Scores s
LEFT JOIN RiskScores r
ON s.Account_ID = r.Account_ID
ORDER BY Account_ID
