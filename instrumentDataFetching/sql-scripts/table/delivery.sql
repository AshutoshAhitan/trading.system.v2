SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[delivery](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Date] [datetime] NOT NULL,
	[Volume] [bigint] NOT NULL,
	[Turnover] [float] NOT NULL,
	[Trades] [bigint] NOT NULL,
	[DeliverableVolume] [bigint] NOT NULL,
	[Symbol] [varchar](75) NOT NULL,
	[VolToTrades] [float] NULL,
	[InvAmtWinAvg3] [bigint] NULL,
	[InvAmtWinAvg5] [bigint] NULL,
	[InvAmtWinAvg7] [bigint] NULL,
	[InvestedAmount] [bigint] NULL,
	[Close] [int] NULL,
	[CostPerTrade] [float] NULL
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
ALTER TABLE [dbo].[delivery] ADD  CONSTRAINT [delivery_index] PRIMARY KEY CLUSTERED 
(
	[Date] ASC,
	[Symbol] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO

