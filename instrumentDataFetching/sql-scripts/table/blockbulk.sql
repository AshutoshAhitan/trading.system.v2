-- Create a new table called '[blockbulk]' in schema '[dbo]'
-- Drop the table if it already exists
IF OBJECT_ID('[dbo].[blockbulk]', 'U') IS NOT NULL
DROP TABLE [dbo].[blockbulk]
GO
-- Create the table in the specified schema
CREATE TABLE [dbo].[blockbulk]
(
    [Id] INT IDENTITY(1,1) NOT NULL PRIMARY KEY, -- Primary Key column
    [Date] DATETIME NOT NULL,
    [Symbol] NVARCHAR(75) NOT NULL,
    [SecurityName] NVARCHAR(512) NOT NULL,
    [ClientName] NVARCHAR(512) NOT NULL,
    [BuySell] NVARCHAR(10) NOT NULL,
    [QuantityTraded] BIGINT NOT NULL,
	[netQuantityTraded] BIGINT NOT NULL,
    [TradePriceWghtAvgPrice] FLOAT NOT NULL,
    [Remarks] NVARCHAR(512) NOT NULL,
    [Type] NVARCHAR(25) NOT NULL
);
GO
