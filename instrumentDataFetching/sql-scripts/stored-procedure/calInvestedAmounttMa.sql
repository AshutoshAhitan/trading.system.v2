-- Create a new stored procedure called 'calInvestedAmountMa' in schema 'dbo'
-- Drop the stored procedure if it already exists
IF EXISTS (
SELECT *
    FROM INFORMATION_SCHEMA.ROUTINES
WHERE SPECIFIC_SCHEMA = N'dbo'
    AND SPECIFIC_NAME = N'calInvestedAmountMa'
    AND ROUTINE_TYPE = N'PROCEDURE'
)
DROP PROCEDURE dbo.calInvestedAmountMa
GO
-- Create the stored procedure in the specified schema
CREATE PROCEDURE dbo.calInvestedAmountMa
    @symbol VARCHAR(75)
AS
BEGIN
    select 1;
END
GO

