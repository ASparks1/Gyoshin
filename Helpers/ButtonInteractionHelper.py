from Helpers import DMHelper
from Helpers import ReactionHelper
from Commands import Join

async def OnButtonClick(interaction, bot):
  try:
    UserID = interaction.user.id
    Origin = interaction.guild_id
  except:
    await DMHelper.DMUserByID(bot, UserID, f"Something went wrong resolving server information.")
    return

  if interaction.custom_id == f"tank_btn":
    #try:
    await interaction.respond(type=6)
    await Join.JoinRaid(interaction.message, bot, f"tank", UserID)
    #except:
    #  await DMHelper.DMUserByID(bot, UserID, f"Something went wrong obtaining information for this run.")
    #  return 
  if interaction.custom_id == f"dps_btn":
    try:
      await interaction.respond(type=6)
      await Join.JoinRaid(interaction.message, bot, f"dps", UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong obtaining information for this run.")
      return 
  if interaction.custom_id == f"healer_btn":
    try:
      await interaction.respond(type=6)
      await Join.JoinRaid(interaction.message, bot, f"healer", UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong obtaining information for this run.")
      return 
  if interaction.custom_id == f"rally_btn":
    try:
      await interaction.respond(type=6)
      await ReactionHelper.OnAddRallyReaction(interaction.message, bot, UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong obtaining information for this run.")
      return 
  if interaction.custom_id == f"members_btn":
    try:
      Message = await ReactionHelper.OnMemberReaction(interaction.message, bot, UserID)
      if Message:
        await interaction.respond(type=4, content=f"{Message}")
      elif not Message:
        await interaction.respond(content=f"No reserves have signed up for this run")
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong obtaining information for this run.")
      return
  if interaction.custom_id == f"reserves_btn":
    try:
      Message = await ReactionHelper.OnReservesReaction(interaction.message, bot, UserID)
      if Message:
        await interaction.respond(type=4, content=f"{Message}")
      elif not Message:
        await interaction.respond(type=4, content=f"No reserves have signed up for this run")
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong obtaining information for this run.")
      return
  if interaction.custom_id == f"reschedule_btn":
    try:
      await interaction.respond(type=6)
      await ReactionHelper.OnAddRescheduleReaction(interaction.message, bot, UserID, Origin)
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong obtaining information for this run.")
      return 
  if interaction.custom_id == f"cancel_btn":
    try:
      await interaction.respond(type=6)
      await ReactionHelper.OnAddCancelReaction(interaction.message, bot, UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong obtaining information for this run.")
      return
  if interaction.custom_id == f"editdesc_btn":
    try:
      await interaction.respond(type=6)
      await ReactionHelper.OnAddEditDescReaction(interaction.message, bot, UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong obtaining information for this run.")
      return