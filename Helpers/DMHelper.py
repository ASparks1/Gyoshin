# Send a DM to the user who wrote the message
async def DMUser(message, messagestring):
    try:
      await message.author.send(messagestring)
    except:
      return

# Send a DM to a specific user id
async def DMUserByID(bot, UserID, messagestring):
 try:
   user = await bot.fetch_user(UserID)
   await user.send(messagestring)
 except:
   return
 return
