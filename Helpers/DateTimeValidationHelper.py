from datetime import datetime
from Helpers import DMHelper
date = datetime.date.today()

async def ValidateDateTime(message, day, month, year, hour, minute):

  # Get current date and time
  current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

  # Convert inputs into sqlite format date
  newdatetime = f"{year}-{month}-{day} {hour}:{minute}"

  # Parse string into a datetime object
  try:
    newdatetime = datetime.strptime(newdatetime, "%Y-%m-%d %H:%M")
  # Throw error when parsing fails
  except:
    await DMHelper.DMUser(message, "Unable to parse given date")

  # Format newly parsed datetime object in the same manner
  try:
    newdatetime = datetime.strftime(newdatetime, "%Y-%m-%d %H:%M")
  # Throw error when formatting fails
  except:
    await DMHelper.DMUser(message, "Unable to format given date")

  # Check if the received date is equal or higher then the current date
  validdate = (bool(newdatetime >= current_date))
  return validdate
