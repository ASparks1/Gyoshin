from Helpers import DMHelper
from Helpers import ReactionHelper
from Helpers import MemberHelper
from Helpers import MessageHelper
from Commands import Join
from Commands import NewOrganizer
from Commands import Dismiss

async def FirstRowButtons(interaction, bot, UserID):
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

async def SecondRowButtons(interaction, bot, UserID):
  if interaction.custom_id == "members_btn":
    try:
      Message = await ReactionHelper.OnMemberReaction(interaction.message, bot)
      if Message:
        await interaction.respond(type=4, content=f"{Message}")
      elif not Message:
        await interaction.respond(content="No message was returned")
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return
  if interaction.custom_id == "reserves_btn":
    try:
      Message = await ReactionHelper.OnReservesReaction(interaction.message, bot)
      if Message:
        await interaction.respond(type=4, content=f"{Message}")
      elif not Message:
        await interaction.respond(type=4, content="No reserves have signed up for this run")
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return
  if interaction.custom_id == "messageraidmembers_btn":
    try:
      await interaction.respond(type=6)
      await MessageHelper.MessageRaidMembers(interaction.message, bot, UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return
  if interaction.custom_id == "dismissmembers_btn":
    try:
      await interaction.respond(type=6)
      await Dismiss.DismissMembers(bot, interaction.message, UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return

async def ThirdRowButtons(interaction, bot, UserID):
  if interaction.custom_id == "editdesc_btn":
    try:
      await interaction.respond(type=6)
      await ReactionHelper.OnAddEditDescReaction(interaction.message, bot, UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return
  if interaction.custom_id == "neworganizer_btn":
    try:
      await interaction.respond(type=6)
      await NewOrganizer.NewOrganizer(bot, interaction.message, UserID)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run.")
      return
  if interaction.custom_id == "reschedule_btn":
    try:
      await interaction.respond(type=6)
      await ReactionHelper.OnAddRescheduleReaction(interaction.message, bot, UserID)
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
