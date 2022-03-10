import sqlite3
import re
import discord
from datetime import datetime
from discord.ui import Button, View
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleIconHelper
from Helpers import DMHelper
from Helpers import DateTimeValidationHelper
from Helpers import DateTimeFormatHelper
from Helpers import ReactionHelper
from Helpers import RaidIDHelper
from Helpers import ButtonInteractionHelper
from Helpers import ButtonRowHelper

async def ListRunsOnDate(ctx, bot, date):
  UserID = ctx.author.id
  Origin = await OriginHelper.GetOrigin(ctx, bot, UserID)
  if not Origin:
    return

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  pattern = re.compile(r'(\d{2})-(\d{2})-(\d{4})')
  match = pattern.match(date)

  if match:
    splitdate = str.split(date, '-')
    day = splitdate[0]
    month = splitdate[1]
    year = splitdate[2]
    sqlitedate = f"{year}-{month}-{day}"

    try:
      current_date = discord.utils.utcnow().strftime("%Y-%m-%d")
      if sqlitedate < current_date:
        await DMHelper.DMUserByID(bot, UserID, "It's not possible to search on dates in the past")
        conn.close()
        return
    except:
      await DMHelper.DMUserByID(bot, UserID, "Unable to convert date from local to sqlite format")
      conn.close()
      return

    try:
      TankIcon = await RoleIconHelper.GetTankIcon()
      DpsIcon = await RoleIconHelper.GetDpsIcon()
      HealerIcon = await RoleIconHelper.GetHealerIcon()
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving role icons")
      conn.close()
      return

    try:
      ChannelID = ctx.channel.id
      c.execute("SELECT ID, Name, OrganizerUserID, Status, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfhealersSignedUp, Date FROM Raids WHERE Date like (?) AND Origin = (?) AND Status != 'Cancelled' AND ChannelID = (?) ORDER BY Date ASC, ID ASC", (sqlitedate+'%', Origin, ChannelID))
    except:
      await DMHelper.DMUserByID(bot, UserID, "Run not found")
      conn.close()
      return

    rows = c.fetchall()
    if rows:
      await ctx.channel.send(f"The following runs are planned on {date}:\n")

      for row in rows:
        try:
          ID = row[0]
          Name = row[1]
          OrganizerUserID = row[2]
          Status = row[3]
          NrOfTanksRequired = row[4]
          NrOfTanksSignedUp = row[5]
          NrOfDpsRequired = row[6]
          NrOfDpsSignedUp = row[7]
          NrOfHealersRequired = row[8]
          NrOfhealersSignedUp = row[9]
          Date = row[10]
          LocalDate = await DateTimeFormatHelper.SqliteToLocalNoCheck(Date)
          try:
            OrganizerName = await UserHelper.GetDisplayName(ctx, OrganizerUserID, bot)
          except:
            await DMHelper.DMUserByID(bot, UserID, "Something went wrong getting the display name of the organizer, perhaps they have left the server")
            conn.close()
            return

        except:
          await DMHelper.DMUserByID(bot, UserID, "Unable to convert variables")
          conn.close()
          return

        if OrganizerName:
          # Create buttons to add
          tank_btn = Button(label="Tank", row=0, style=discord.ButtonStyle.primary, custom_id="tank_btn")
          dps_btn = Button(label="Dps", row=0, style=discord.ButtonStyle.danger, custom_id="dps_btn")
          healer_btn = Button(label="Healer", style=discord.ButtonStyle.success, custom_id="healer_btn")
          rally_btn = Button(label="Rally", custom_id="rally_btn")
          members_btn = Button(label="Members", row=1, custom_id="members_btn")
          reserves_btn = Button(label="Reserves", row=1, custom_id="reserves_btn")
          messageraidmembers_btn = Button(label="Message members", row=1, custom_id="messageraidmembers_btn")
          dismissmembers_btn = Button(label="Dismiss members", row=1, custom_id="dismissmembers_btn")
          editdesc_btn = Button(label="Edit description", row=2, custom_id="editdesc_btn")
          neworganizer_btn = Button(label="New organizer", row=2, custom_id="neworganizer_btn")
          reschedule_btn = Button(label="Reschedule", row=2, custom_id="reschedule_btn")
          cancel_btn = Button(label="Cancel", row=2, style=discord.ButtonStyle.danger, custom_id="cancel_btn")

          # Define button callback actions
          async def button_callback(interaction):
            await interaction.response.send_message(content="Processing", ephemeral=True)
            await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)
          tank_btn.callback = button_callback
          dps_btn.callback = button_callback
          healer_btn.callback = button_callback
          rally_btn.callback = button_callback
          members_btn.callback = button_callback
          reserves_btn.callback = button_callback
          messageraidmembers_btn.callback = button_callback
          dismissmembers_btn.callback = button_callback
          editdesc_btn.callback = button_callback
          neworganizer_btn.callback = button_callback
          reschedule_btn.callback = button_callback
          cancel_btn.callback = button_callback

          # Create view and add buttons to it
          view=View(timeout=None)
          view.add_item(tank_btn)
          view.add_item(dps_btn)
          view.add_item(healer_btn)
          view.add_item(rally_btn)
          view.add_item(members_btn)
          view.add_item(reserves_btn)
          view.add_item(messageraidmembers_btn)
          view.add_item(dismissmembers_btn)
          view.add_item(editdesc_btn)
          view.add_item(neworganizer_btn)
          view.add_item(reschedule_btn)
          view.add_item(cancel_btn)
          await ctx.channel.send(f"**Run:** {ID}\n**Description:** {Name}\n**Organizer:** {OrganizerName}\n**Date (UTC):** {LocalDate}\n**Status:** {Status}\n{TankIcon} {NrOfTanksSignedUp}\/{NrOfTanksRequired} {DpsIcon} {NrOfDpsSignedUp}\/{NrOfDpsRequired} {HealerIcon} {NrOfhealersSignedUp}\/{NrOfHealersRequired}", view=view)

    else:
       await ctx.channel.send(f"No runs found on {date}")
       conn.close()
       return
  else:
    await DMHelper.DMUserByID(bot, UserID, "Invalid date and time detected please use the dd-mm-yyyy format")
    conn.close()
    return

  conn.close()
  return
