from Helpers import MyRunsHelper

async def ListMyRuns(ctx, bot):
  await MyRunsHelper.ListMyRunsHelper(ctx, bot, 'MyRuns')
  await MyRunsHelper.ListMyRunsHelper(ctx, bot, 'MyReserveRuns')
