SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- Create the stored procedure in the specified schema
CREATE PROCEDURE [dbo].[insertDelivery]
    @Date DATE,
    @Close INT,
    @Volume BIGINT,
    @Turnover FLOAT,
    @Trades BIGINT,
    @DeliverableVolume BIGINT,
    @Symbol VARCHAR(75)
AS
BEGIN
    -- body of the stored procedure
    IF EXISTS (
        SELECT * FROM dbo.delivery
        WHERE [Date]=@Date AND Symbol=@Symbol
    )
    BEGIN
        UPDATE dbo.delivery
        SET [Close]=@Close, Volume=@Volume, Turnover=@Turnover, Trades=@Trades, DeliverableVolume=@DeliverableVolume
        WHERE [Date]=@Date AND Symbol=@Symbol
    END

    ELSE
    BEGIN
        INSERT INTO dbo.delivery (
            Date, [Close], Volume, Turnover, Trades, DeliverableVolume, Symbol
        ) VALUES (
            @Date, @Close, @Volume, @Turnover, @Trades, @DeliverableVolume, @Symbol
        )
    END

END
GO

