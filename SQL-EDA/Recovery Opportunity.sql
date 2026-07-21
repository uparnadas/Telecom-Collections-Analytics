-- Recovery Opportunity
-- Tomorrow our team can only call 20% of our accounts due to limited staffing. We want to maximize collections. 
-- Which accounts should we prioritize?
 

WITH AccountStats AS (
-- DPD < 180
-- Credit Score > 500
    SELECT 
        Account_ID,
        CASE
            WHEN Days_Past_Due < 180 THEN 2 ELSE 0
        END AS DPD_Score,
        CASE
            WHEN Credit_Score > 500 THEN 1 ELSE 0 
        END AS Credit_Score
    FROM Accounts
),
Promise AS (
-- Recent Broken Promise
    SELECT
        Account_ID,
        Promise_Date,
        Promise_Status,
        ROW_NUMBER() OVER (PARTITION BY Account_ID ORDER BY Promise_Date DESC) AS Promise_Rank
    FROM Promise_To_Pay
),
PaymentStats AS (
-- Payments > 2
    SELECT
        Account_ID,
        CASE
            WHEN COUNT(Payment_ID) > 2 THEN 2 ELSE 0
        END AS Payment_Score
    FROM Payments
    GROUP BY Account_ID
),
Scores AS (
    SELECT
        a.Account_ID,
        a.DPD_Score,
        a.Credit_Score,
        pa.Payment_Score
    FROM AccountStats a
    LEFT JOIN Promise p
    ON a.Account_ID = p.Account_ID
    LEFT JOIN PaymentStats pa
    ON a.Account_ID = pa.Account_ID
    WHERE p.Promise_Status = 'Broken' AND p.Promise_Rank = 1
),
Priority_Score AS (
    SELECT
    Account_ID, 
    (
        + ISNULL(DPD_Score,0)
        + ISNULL(Credit_Score,0)
        + ISNULL(Payment_Score,0)
    ) AS PriorityScore
    FROM Scores
)
SELECT
    Account_ID,
    CASE
        WHEN PriorityScore > 4 THEN 'High Probability'
        WHEN PriorityScore > 2 THEN 'Medium Probability'
    ELSE 'Low Probability'
END AS Priority_Category
FROM Priority_Score
ORDER BY Priority_Category



--Promise
--WHERE Promise_Status = 'Broken' AND Promise_Rank = 1