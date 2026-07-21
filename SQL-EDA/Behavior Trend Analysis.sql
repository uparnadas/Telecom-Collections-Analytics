-- Behavior Trend Analysis
-- The Collections Director wants to identify accounts whose payment behavior is deteriorating over time. 
-- An account may have started making regular payments but is now paying less frequently or paying smaller amounts.

-- How would you identify those accounts?

WITH PaymentHistory AS (
    SELECT
        Account_ID,
        Payment_Date,
        Payment_Amount,

        LAG(Payment_Amount) OVER (
            PARTITION BY Account_ID
            ORDER BY Payment_Date
        ) AS Previous_Payment,

        LAG(Payment_Date) OVER (
            PARTITION BY Account_ID
            ORDER BY Payment_Date
        ) AS Previous_Payment_Date
    FROM Payments
),

PaymentTrend AS (
    SELECT
        Account_ID,
        Payment_Date,
        Payment_Amount,
        Previous_Payment,

        DATEDIFF(
            DAY,
            Previous_Payment_Date,
            Payment_Date
        ) AS Days_Between_Payments,

        CASE
            WHEN Previous_Payment IS NOT NULL
             AND Payment_Amount < Previous_Payment
            THEN 1
            ELSE 0
        END AS Payment_Decreased
    FROM PaymentHistory
),

GapTrend AS (
    SELECT
        *,
        LAG(Days_Between_Payments) OVER (
            PARTITION BY Account_ID
            ORDER BY Payment_Date
        ) AS Previous_Gap
    FROM PaymentTrend
)

SELECT
    Account_ID,

    COUNT(*) AS Total_Payments,

    SUM(Payment_Decreased) AS Times_Payment_Decreased,

    SUM(
        CASE
            WHEN Previous_Gap IS NOT NULL
             AND Days_Between_Payments > Previous_Gap
            THEN 1
            ELSE 0
        END
    ) AS Times_Gap_Increased,

    CASE
        WHEN SUM(Payment_Decreased) >= 2
         AND SUM(
                CASE
                    WHEN Previous_Gap IS NOT NULL
                     AND Days_Between_Payments > Previous_Gap
                    THEN 1
                    ELSE 0
                END
            ) >= 2
        THEN 'Deteriorating'

        WHEN SUM(Payment_Decreased) >= 2
        THEN 'Payment Amount Declining'

        WHEN SUM(
                CASE
                    WHEN Previous_Gap IS NOT NULL
                     AND Days_Between_Payments > Previous_Gap
                    THEN 1
                    ELSE 0
                END
            ) >= 2
        THEN 'Payment Frequency Declining'

        ELSE 'Stable'
    END AS Account_Status

FROM GapTrend
GROUP BY Account_ID
ORDER BY Account_Status DESC, Account_ID;
