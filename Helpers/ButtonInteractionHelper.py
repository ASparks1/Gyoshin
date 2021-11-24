from Helpers import DMHelper
from Helpers import ButtonRowHelper

async def OnButtonClick(interaction, bot):
  try:
    UserID = interaction.user.id
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong resolving server information.")
    return

  if interaction.custom_id in ("tank_btn","dps_btn","healer_btn","rally_btn"):
    await ButtonRowHelper.FirstRowButtons(interaction, bot, UserID)
  if interaction.custom_id in ("members_btn","reserves_btn","messageraidmembers_btn"):
    await ButtonRowHelper.SecondRowButtons(interaction, bot, UserID)
  if interaction.custom_id in ("editdesc_btn","neworganizer_btn","reschedule_btn","cancel_btn"):
    await ButtonRowHelper.ThirdRowButtons(interaction, bot, UserID)
