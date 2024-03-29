import re
import datetime
import math
from datetime import datetime
from datetime import timezone
from Helpers import DateTimeValidationHelper
from Helpers import DMHelper

# Helper function to convert local date to sqlite format
# Expected input format is DD-MM-YYYY HH:MM
async def LocalToSqlite(ctx, datetime):
  pattern = re.compile(r'((\d{2})-(\d{2})-(\d{4})) (\d{2}):(\d{2})')
  match = pattern.match(datetime)

  if match:
    splitdate = datetime.split(' ')
    date = splitdate[0]
    time = splitdate[1]

    splitdate = date.split('-')
    day = splitdate[0]
    month = splitdate[1]
    year = splitdate[2]

    splittime = time.split(':')
    hour = splittime[0]
    minute = splittime[1]

    sqlitedatetime = f"{year}-{month}-{day} {hour}:{minute}"
    isdatevalid = await DateTimeValidationHelper.ValidateDateTime(ctx, day, month, year, hour, minute)

    if isdatevalid:
      return sqlitedatetime

# Helper function to convert sqlite date to local format
# Expected input format is YYYY-MM-DD HH:MM
async def SqliteToLocal(ctx, datetime):
  pattern = re.compile(r'((\d{4})-(\d{2})-(\d{2})) (\d{2}):(\d{2})')
  match = pattern.match(datetime)

  if match:
    splitdate = datetime.split(' ')
    date = splitdate[0]
    time = splitdate[1]

    splitdate = date.split('-')
    day = splitdate[2]
    month = splitdate[1]
    year = splitdate[0]

    splittime = time.split(':')
    hour = splittime[0]
    minute = splittime[1]

    isdatevalid = await DateTimeValidationHelper.ValidateDateTime(ctx, day, month, year, hour, minute)

    if isdatevalid:
     localdatetime = f"{day}-{month}-{year} {hour}:{minute}"
     return localdatetime

# Helper function without future check
async def SqliteToLocalNoCheck(Date):
  splitdate = Date.split(' ')
  date = splitdate[0]
  time = splitdate[1]

  splitdate = date.split('-')
  day = splitdate[2]
  month = splitdate[1]
  year = splitdate[0]

  splittime = time.split(':')
  hour = splittime[0]
  minute = splittime[1]
  
  localdatetime = f"{day}-{month}-{year} {hour}:{minute}"
  return localdatetime

# Helper function to convert local date time format to unix timestamp
async def LocalToUnixTimestamp(Date):
  splitdate = Date.split(' ')
  date = splitdate[0]
  time = splitdate[1]

  splitdate = date.split('-')
  day = splitdate[0]
  month = splitdate[1]
  year = splitdate[2]

  splittime = time.split(':')
  hour = splittime[0]
  minute = splittime[1]

  # Convert time into users local Discord time
  dt = datetime(int(year), int(month), int(day), int(hour), int(minute))
  unixTimestamp = dt.replace(tzinfo=timezone.utc).timestamp()
  # Truncate in order to remove decimal values as Discord will not translate this into users date & time if the timestamp has a .0 after it as returned by previous action
  unixTimestamp = math.trunc(unixTimestamp)
  unixTimestamp = f"<t:{unixTimestamp}:f>"
  return unixTimestamp