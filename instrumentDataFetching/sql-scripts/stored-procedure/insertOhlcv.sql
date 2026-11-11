SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- Create the stored procedure in the specified schema
CREATE PROCEDURE [dbo].[insertOhlcv]
    @Date DATE,
    @Open FLOAT,
    @High FLOAT,
    @Low FLOAT,
    @Close FLOAT,
    @AdjClose FLOAT,
    @Volume BIGINT,
    @Symbol VARCHAR(75),
    @Timeframe VARCHAR(15)
AS
BEGIN
    -- body of the stored procedure
    IF EXISTS (
        select * from dbo.ohlcv where date=@Date and Symbol=@Symbol and Timeframe=@Timeframe
    )
    BEGIN
        UPDATE dbo.ohlcv
        SET [Open]=@Open, High=@High, Low=@Low, [Close]=@Close, AdjClose=@AdjClose, Volume=@Volume
        WHERE [Date]=@Date AND Symbol=@Symbol AND Timeframe=@Timeframe
    END

    ELSE
    BEGIN
        INSERT INTO dbo.ohlcv (
            Date, [Open], High, Low, [Close], AdjClose, Volume, Symbol, Timeframe
        ) VALUES (
            @Date, @Open, @High, @Low, @Close, @AdjClose, @Volume, @Symbol, @Timeframe
        ) 
    END
END
GO

