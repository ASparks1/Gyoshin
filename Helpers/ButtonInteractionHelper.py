from Helpers import DMHelper
from Helpers import ReactionHelper
from Commands import Join

async def OnButtonClick(interaction, bot):
  try:
    UserID = interaction.user.id
    Origin = interaction.guild_id
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong resolving server information.")
    return

  if interaction.custom_id == "tank_btn":
    try:
      await interaction.respond(type=6)
      await Join.JoinRaid(interaction.message, bot, "tank", UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return 
  if interaction.custom_id == "dps_btn":
    try:
      await interaction.respond(type=6)
      await Join.JoinRaid(interaction.message, bot, "dps", UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return 
  if interaction.custom_id == "healer_btn":
    try:
      await interaction.respond(type=6)
      await Join.JoinRaid(interaction.message, bot, "healer", UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return 
  if interaction.custom_id == "rally_btn":
    try:
      await interaction.respond(type=6)
      await ReactionHelper.OnAddRallyReaction(interaction.message, bot, UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return 
  if interaction.custom_id == "members_btn":
    try:
      Message = await ReactionHelper.OnMemberReaction(interaction.message, bot, UserID)
      if Message:
        await interaction.respond(type=4, content=f"{Message}")
      elif not Message:
        await interaction.respond(content="No reserves have signed up for this run")
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return
  if interaction.custom_id == "reserves_btn":
    try:
      Message = await ReactionHelper.OnReservesReaction(interaction.message, bot, UserID)
      if Message:
        await interaction.respond(type=4, content=f"{Message}")
      elif not Message:
        await interaction.respond(type=4, content="No reserves have signed up for this run")
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return
  if interaction.custom_id == "reschedule_btn":
    try:
      await interaction.respond(type=6)
      await ReactionHelper.OnAddRescheduleReaction(interaction.message, bot, UserID, Origin)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return 
  if interaction.custom_id == "cancel_btn":
    try:
      await interaction.respond(type=6)
      await ReactionHelper.OnAddCancelReaction(interaction.message, bot, UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return
  if interaction.custom_id == "editdesc_btn":
    try:
      await interaction.respond(type=6)
      await ReactionHelper.OnAddEditDescReaction(interaction.message, bot, UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return