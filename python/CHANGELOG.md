Standardized this across all tables.

Table	            Primary Key
Accounts	        Account_ID
Phone_Numbers	    Phone_ID
Call_Interactions	Call_ID
Promise_To_Pay	    Promise_ID
Payments	        Payment_ID

All IDs will be generated in Python

When we load the data into SQL Server, we'll use IDENTITY_INSERT.

### Future Enhancement

Allow multiple Promise To Pay records per account.

Business Rule:
- An account may have multiple historical promises.
- Only one promise may be active at any point in time.

## 2026-07-20

### Accounts Generator
- Replaced random account generation with a realistic portfolio simulation:
  - Existing inventory (Jul 2024 – Dec 2025)
  - Daily new placements (Jan 2026 business days)
- Changed placement date generation to simulate daily inventory arrivals.
- Updated charge-off dates to be generated relative to placement dates (1–45 days prior).
- Derived Collection Stage from account age instead of random assignment.
- Reordered generation sequence to follow business workflow and eliminate column dependency issues.

### Call Interactions Generator
- Reduced historical call attempts to more realistic ranges by collection stage.
- Added account age adjustment to historical call volume.
- Replaced fixed dial result probabilities with stage-based dial outcome probabilities.
- Replaced fixed RPC disposition probabilities with stage-based disposition probabilities, creating more realistic customer interactions across collection stages.

### Promise To Pay Generator
- Updated simulation end date to align with the January 2026 business timeline.
- Made promise strategies balance-driven:
  - Small balances favor full payments.
  - Medium balances favor partial payments and installments.
  - Large balances favor settlements and installment plans.
- Enhanced promise outcome logic by factoring in both promise strategy and previous customer behavior, resulting in more realistic Kept/Broken promise distributions.


### Payments Generator
- Updated simulation timeline to January 2026.
- Improved kept-promise payment behavior by introducing variable payment fulfillment levels instead of near-complete payments for every kept promise.
- Maintained realistic mix of promise-driven and direct payments while preventing overpayment beyond outstanding balances.