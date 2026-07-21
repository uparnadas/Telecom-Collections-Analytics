-- 1) How many rows are in each table?

SELECT COUNT(*) AS Total_Rows
FROM Accounts

SELECT COUNT(*) AS Total_Rows
FROM Phone_Numbers;

SELECT COUNT(*) AS Total_Rows
FROM Call_Interactions;

SELECT COUNT(*) AS Total_Rows
FROM Promise_To_Pay;

SELECT COUNT(*) AS Total_Rows
FROM Payments;

-- 2) Display the first 10 rows from each table.

SELECT TOP 10 * FROM Accounts;

SELECT TOP 10 * FROM Phone_Numbers;

SELECT TOP 10 * FROM dbo.Call_Interactions;

SELECT TOP 10 * FROM dbo.Promise_To_Pay;

SELECT TOP 10 * FROM dbo.Payments;

-- 3) Find the number of columns in each table.

SELECT COUNT(*) AS Total_Columns
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
  AND TABLE_NAME = 'Accounts';

SELECT COUNT(*) AS Total_Columns
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'dbo' 
  AND TABLE_NAME = 'Phone_Numbers';

SELECT COUNT(*) AS Total_Columns
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'dbo' 
  AND TABLE_NAME = 'Call_Interactions';

SELECT COUNT(*) AS Total_Columns
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'dbo' 
  AND TABLE_NAME = 'Promise_To_Pay';

SELECT COUNT(*) AS Total_Columns
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'dbo' 
  AND TABLE_NAME = 'Payments';

-- 4) Check whether any table contains duplicate primary keys.

SELECT Account_ID, COUNT(*) as DuplicateCount
FROM dbo.Accounts
GROUP BY Account_ID
HAVING COUNT(*) > 1;

SELECT Phone_ID, COUNT(*) as DuplicateCount
FROM dbo.Phone_Numbers
GROUP BY Phone_ID
HAVING COUNT(*) > 1;

SELECT Call_ID, COUNT(*) as DuplicateCount
FROM dbo.Call_Interactions
GROUP BY Call_ID
HAVING COUNT(*) > 1;

SELECT Promise_ID, COUNT(*) as DuplicateCount
FROM dbo.Promise_To_Pay
GROUP BY Promise_ID
HAVING COUNT(*) > 1;

SELECT Payment_ID, COUNT(*) as DuplicateCount
FROM dbo.Payments
GROUP BY Payment_ID
HAVING COUNT(*) > 1;

-- 5) Verify that all foreign keys have matching parent records.

SELECT p.Account_ID
FROM dbo.Phone_Numbers p
LEFT JOIN
dbo.Accounts a
ON p.Account_ID = a.Account_ID
WHERE a.Account_ID IS NULL;

SELECT c.Phone_ID
FROM dbo.Call_Interactions c
LEFT JOIN
dbo.Phone_Numbers p
ON c.Phone_ID = p.Phone_ID
WHERE p.Account_ID IS NULL;

SELECT pr.Call_ID
FROM dbo.Promise_To_Pay pr
LEFT JOIN
dbo.Call_Interactions c
ON pr.Call_ID = c.Call_ID
WHERE c.Call_ID IS NULL;

SELECT pa.Promise_ID
FROM dbo.Payments pa
LEFT JOIN
dbo.Promise_To_Pay pr
ON pa.Promise_ID = pr.Promise_ID
WHERE pr.Promise_ID IS NULL;

