from Helpers import MyRunsHelper

async def ListMyRuns(message, bot):
  await MyRunsHelper.ListMyRunsHelper(message, bot, 'MyRuns')
  await MyRunsHelper.ListMyRunsHelper(message, bot, 'MyReserveRuns')
