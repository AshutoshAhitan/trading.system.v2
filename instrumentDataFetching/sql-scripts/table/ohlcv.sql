SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ohlcv](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Date] [datetime] NOT NULL,
	[Open] [float] NOT NULL,
	[High] [float] NOT NULL,
	[Low] [float] NOT NULL,
	[Close] [float] NOT NULL,
	[AdjClose] [float] NOT NULL,
	[Volume] [bigint] NOT NULL,
	[Symbol] [varchar](75) NOT NULL,
	[Timeframe] [varchar](15) NOT NULL,
) ON [PRIMARY]
GO


ALTER TABLE dbo.ohlcv
ADD CONSTRAINT ohlcv_index PRIMARY KEY (Date, Symbol, Timeframe);
