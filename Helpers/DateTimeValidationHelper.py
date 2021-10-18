import datetime
date = datetime.date.today()
from datetime import datetime
from Helpers import DMHelper

async def ValidateDateTime(message, day, month, year, hour, minute):
  current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
  newdatetime = f"{year}-{month}-{day} {hour}:{minute}"

  try:
    newdatetime = datetime.strptime(newdatetime, "%Y-%m-%d %H:%M")
  except:
    await DMHelper.DMUser(message, "Unable to parse given date")

  try:
    newdatetime = datetime.strftime(newdatetime, "%Y-%m-%d %H:%M")
  except:
    await DMHelper.DMUser(message, "Unable to format given date")

  validdate = (bool(newdatetime >= current_date))
  return validdate
