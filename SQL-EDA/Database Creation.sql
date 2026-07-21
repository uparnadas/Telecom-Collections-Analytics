-- Create the Database
CREATE DATABASE NovaCollectionsDB;

USE NovaCollectionsDB;

-- First, drop the tables inside the schema
DROP TABLE IF EXISTS schema_name.Accounts;
DROP TABLE IF EXISTS schema_name.Phone_Numbers;
DROP TABLE IF EXISTS schema_name.Call_Interactions;
DROP TABLE IF EXISTS schema_name.Promise_To_Pay;
DROP TABLE IF EXISTS schema_name.Payments;


-- Create the Accounts Table
TRUNCATE TABLE dbo.Accounts;
CREATE TABLE Accounts
(
    Account_ID INT PRIMARY KEY,
    Account_Number VARCHAR(20) UNIQUE NOT NULL,
    Customer_First_Name VARCHAR(50),
    Customer_Last_Name VARCHAR(50),
    State VARCHAR(50),
    City VARCHAR(50),
    Zip_Code VARCHAR(10),
    Collection_Stage VARCHAR(30),
    Days_Past_Due INT,
    Original_Balance DECIMAL(12,2),
    Outstanding_Balance DECIMAL(12,2),
    Credit_Score INT,
    Charge_Off_Date DATE,
    Placement_Date DATE,
    Last_Payment_Date DATE,
    Account_Tenure_Months INT,
    Account_Status VARCHAR(20),
    Bankruptcy_Flag BIT,
    Fraud_Flag BIT
);

-- Create the Phone Number Table
DROP TABLE dbo.Phone_Numbers;
CREATE TABLE dbo.Phone_Numbers
(
    Phone_ID INT PRIMARY KEY,
    Account_ID INT NOT NULL,
    Phone_Number VARCHAR(20) NOT NULL,
    Phone_Source VARCHAR(30),
    Phone_Type VARCHAR(20),
    Is_Primary BIT,
    Is_Verified BIT,
    Is_DNC BIT,
    Date_Added DATE,
    Phone_Status VARCHAR(30),
    Preferred_Dial_Order INT,

    CONSTRAINT FK_PhoneNumbers_Accounts
        FOREIGN KEY(Account_ID)
        REFERENCES dbo.Accounts(Account_ID)
);

-- Create the Call Interactions Table

CREATE TABLE Call_Interactions
(
    Call_ID INT PRIMARY KEY,
    Account_ID INT NOT NULL,
    Phone_ID INT NOT NULL,
    Call_Date DATE NOT NULL,
    Call_Time TIME NOT NULL,
    Dial_Result VARCHAR(30) NOT NULL,
    Talk_Time_Seconds INT NOT NULL,
    Agent_Disposition VARCHAR(50) NULL,
    Promise_To_Pay BIT NOT NULL,
    Callback_Requested BIT NOT NULL,
    Settlement_Requested BIT NOT NULL,

    CONSTRAINT FK_CallInteractions_Accounts
        FOREIGN KEY (Account_ID)
        REFERENCES Accounts(Account_ID),

    CONSTRAINT FK_CallInteractions_Phones
        FOREIGN KEY (Phone_ID)
        REFERENCES Phone_Numbers(Phone_ID)
);

-- Create the Promise To Pay Table

CREATE TABLE Promise_To_Pay
(
    Promise_ID INT PRIMARY KEY,
    Call_ID INT NOT NULL,
    Account_ID INT NOT NULL,
    Promise_Date DATE NOT NULL,
    Promise_Due_Date DATE NOT NULL,
    Promised_Amount DECIMAL(12,2) NOT NULL,
    Promise_Status VARCHAR(20) NOT NULL,

    CONSTRAINT FK_PTP_Accounts
        FOREIGN KEY (Account_ID)
        REFERENCES Accounts(Account_ID),

    CONSTRAINT FK_PTP_CallInteractions
        FOREIGN KEY (Call_ID)
        REFERENCES Call_Interactions(Call_ID)
);

-- Create the Payments Table

CREATE TABLE Payments
(
    Payment_ID INT PRIMARY KEY,
    Account_ID INT NOT NULL,
    Promise_ID INT NULL,
    Payment_Date DATE NOT NULL,
    Payment_Amount DECIMAL(12,2) NOT NULL,
    Payment_Method VARCHAR(30) NOT NULL,

    CONSTRAINT FK_Payments_Accounts
        FOREIGN KEY (Account_ID)
        REFERENCES Accounts(Account_ID),

    CONSTRAINT FK_Payments_PTP
        FOREIGN KEY (Promise_ID)
        REFERENCES Promise_To_Pay(Promise_ID)
);

Select * from Accounts;
Select * from Phone_Numbers;
Select * from Call_Interactions;
Select * from Promise_To_Pay;
Select * from Payments;