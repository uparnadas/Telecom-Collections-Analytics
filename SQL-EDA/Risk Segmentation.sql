-- Risk Segmentation
-- Management wants to identify accounts that appear healthy today but are likely to become delinquent 
-- within the next month based on historical behavior.

WITH PromiseStatus AS (
    -- Broken Promise > 3
    SELECT
        Account_ID,
        SUM(
            CASE
                WHEN Promise_Status = 'Broken' THEN 1 ELSE 0 END) AS Broken_Promise
    FROM Promise_To_Pay
    GROUP BY Account_ID
),
AccountStatus AS (
    -- Days past due > 180
    SELECT 
    Account_ID,
    CASE
        WHEN Days_Past_Due > 180 THEN 2 ELSE 0
    END AS DPD_Score,
    CASE
        WHEN Outstanding_Balance > 10000 THEN 1 ELSE 0 
    END AS Balance_Score,
    CASE
        WHEN Credit_Score < 500 THEN 1 ELSE 0 
    END AS Credit_Score
    FROM Accounts
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
Scores AS (
    SELECT
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
    LEFT JOIN RefusalStatus r
    ON a.Account_ID = r.Account_ID
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
    Account_ID,
    CASE
        WHEN Risk_Score >= 4 THEN 'High Risk'
        WHEN Risk_Score >= 3 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS Risk_Category
FROM RiskScores

