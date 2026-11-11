SET ANSI_NULLS ON
-- Create a new stored procedure called 'insertBlockBulk' in schema 'dbo'
-- Drop the stored procedure if it already exists
IF EXISTS (
SELECT *
    FROM INFORMATION_SCHEMA.ROUTINES
WHERE SPECIFIC_SCHEMA = N'dbo'
    AND SPECIFIC_NAME = N'insertBlockBulk'
    AND ROUTINE_TYPE = N'PROCEDURE'
)
DROP PROCEDURE dbo.insertBlockBulk
GO
SET QUOTED_IDENTIFIER ON
GO
-- Create the stored procedure in the specified schema
CREATE PROCEDURE [dbo].[insertBlockBulk]
    @Date DATETIME,
    @Symbol NVARCHAR(75),
    @SecurityName NVARCHAR(512),
    @ClientName NVARCHAR(512),
    @BuySell NVARCHAR(10),
    @QuantityTraded BIGINT,
	@netQuantityTraded BIGINT,
    @TradePriceWghtAvgPrice FLOAT,
    @Remarks NVARCHAR(512),
    @Type NVARCHAR(25)
AS
BEGIN
    -- body of the stored procedure
    IF NOT EXISTS (
        SELECT * FROM dbo.blockbulk
        WHERE [Date]=@Date AND Symbol=@Symbol AND ClientName=@ClientName AND BuySell=@BuySell
    )
    BEGIN
        INSERT INTO dbo.blockbulk (
            Date, Symbol, SecurityName, ClientName, BuySell, QuantityTraded, netQuantityTraded, TradePriceWghtAvgPrice, Remarks, Type
        ) VALUES (
            @Date, @Symbol, @SecurityName, @ClientName, @BuySell, @QuantityTraded, @netQuantityTraded, @TradePriceWghtAvgPrice, @Remarks, @Type 
        )
        
    END

END
GO
