import re
from Helpers import DateTimeValidationHelper
from Helpers import DMHelper

# Helper function to convert local date to sqlite format
# Expected input format is DD-MM-YYYY HH:MM
async def LocalToSqlite(message, datetime):

  # Regular expression pattern to use in order to check if date was received in dd-mm-yyyy hh:mm format
  pattern = re.compile(r'((\d{2})-(\d{2})-(\d{4})) (\d{2}):(\d{2})')

  # Compare the date and time that was received to the pattern
  match = pattern.match(datetime)

  # If it matches the pattern provided continue
  if match:

    # Split date into date and time values
    splitdate = datetime.split(' ')
    date = splitdate[0]
    time = splitdate[1]

    # Split date into day, month and year values
    splitdate = date.split('-')
    day = splitdate[0]
    month = splitdate[1]
    year = splitdate[2]

    # Split time into hours and minutes
    splittime = time.split(':')
    hour = splittime[0]
    minute = splittime[1]

    # Generate date in sqlite format
    sqlitedatetime = f"{year}-{month}-{day} {hour}:{minute}"

    # Check if the generated date is valid
    isdatevalid = await DateTimeValidationHelper.ValidateDateTime(message, day, month, year, hour, minute)

    # If date is valid return date in sqlite format
    if isdatevalid:
      return sqlitedatetime

# Helper function to convert sqlite date to local format
# Expected input format is YYYY-MM-DD HH:MM
async def SqliteToLocal(message, datetime):

  # Regular expression pattern to use in order to check if date was received in yyyy-mm-dd hh:mm format
  pattern = re.compile(r'((\d{4})-(\d{2})-(\d{2})) (\d{2}):(\d{2})')

  # Compare the date and time that was received to the pattern
  match = pattern.match(datetime)

  if match:

    # Split date into date and time values
    splitdate = datetime.split(' ')
    date = splitdate[0]
    time = splitdate[1]

    # Split date into day, month and year values
    splitdate = date.split('-')
    day = splitdate[2]
    month = splitdate[1]
    year = splitdate[0]

    # Split time into hours and minutes
    splittime = time.split(':')
    hour = splittime[0]
    minute = splittime[1]

    # Check if the generated date is valid
    isdatevalid = await DateTimeValidationHelper.ValidateDateTime(message, day, month, year, hour, minute)

    # Return local time if date is valid
    if isdatevalid:
      localdatetime = f"{day}-{month}-{year} {hour}:{minute}"
      return localdatetime

# Helper function without future check
async def SqliteToLocalNoCheck(Date):

  # Split date into date and time values
  splitdate = Date.split(' ')
  date = splitdate[0]
  time = splitdate[1]

  # Split date into day, month and year values
  splitdate = date.split('-')
  day = splitdate[2]
  month = splitdate[1]
  year = splitdate[0]

  # Split time into hours and minutes
  splittime = time.split(':')
  hour = splittime[0]
  minute = splittime[1]
  
  localdatetime = f"{day}-{month}-{year} {hour}:{minute}"
  return localdatetime
