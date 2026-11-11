-- Create a new stored procedure called 'calPriceAndVolMa' in schema 'dbo'
-- Drop the stored procedure if it already exists
IF EXISTS (
SELECT *
    FROM INFORMATION_SCHEMA.ROUTINES
WHERE SPECIFIC_SCHEMA = N'dbo'
    AND SPECIFIC_NAME = N'calPriceAndVolMa'
    AND ROUTINE_TYPE = N'PROCEDURE'
)
DROP PROCEDURE dbo.calPriceAndVolMa
GO
-- Create the stored procedure in the specified schema
CREATE PROCEDURE dbo.calPriceAndVolMa
    @symbol VARCHAR(75)
AS
BEGIN
    -- body of the stored procedure
    select 1;
END

