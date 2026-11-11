-- Create a new stored procedure called 'getBlockBulkDeals' in schema 'dbo'
-- Drop the stored procedure if it already exists
IF EXISTS (
SELECT *
    FROM INFORMATION_SCHEMA.ROUTINES
WHERE SPECIFIC_SCHEMA = N'dbo'
    AND SPECIFIC_NAME = N'getBlockBulkDeals'
    AND ROUTINE_TYPE = N'PROCEDURE'
)
DROP PROCEDURE dbo.getBlockBulkDeals
GO
-- Create the stored procedure in the specified schema
CREATE PROCEDURE dbo.getBlockBulkDeals
    @symbol NVARCHAR(75),
    @startDate DATE,
    @endDate DATE
-- add more stored procedure parameters here
AS
BEGIN
    -- body of the stored procedure
    SELECT * from dbo.blockbulk WHERE Symbol=@symbol AND [Date] BETWEEN @startDate AND @endDate
END
GO

