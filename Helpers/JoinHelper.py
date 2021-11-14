import sqlite3
from Helpers import DMHelper
from Helpers import MessageHelper
from Helpers import NotificationHelper

# Helper function to notify organizer when all slots have been filled
async def NotifyOrganizer(message, bot, UserID, RaidID, Organizer, Description, LocalDate):
  try:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()
    c.execute("SELECT NrOfPlayersRequired, NrOfPlayersSignedUp FROM Raids  WHERE ID = (?)", (RaidID,))
    row = c.fetchone()

    if row:
      NrOfPlayersRequired = row[0]
      NrOfPlayersSignedUp = row[1]

    if NrOfPlayersRequired == NrOfPlayersSignedUp:
      try:
        c.execute("UPDATE Raids SET Status = 'Formed' WHERE ID = (?)", (RaidID,))
        try:
          conn.commit()
          conn.close()
          UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID)
          await message.edit(content=UpdatedMessage)
          NotifyOrganizerMessage = await NotificationHelper.NotifyUser(message, Organizer)
          await message.channel.send(f"{NotifyOrganizerMessage}\nYour crew for {Description} on {LocalDate} has been assembled!")
          return
        except:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong joining you to this run.")
          conn.close()
          return
      except:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating party status to formed.")
        conn.close()
        return
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of signed up players and dps")
    conn.close()
    return
