import sqlite3
from datetime import datetime
from datetime import timedelta

# Helper function to automatically delete old raid data in order to keep database size limited
async def DeleteOldRaidData():

  # Open connection to the database
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Get current date and time
  try:
    current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    current_date = datetime.utcnow().strptime(current_date, "%Y-%m-%d %H:%M")
    yesterday = current_date - timedelta(days=1)
    yesterday = datetime.strftime(yesterday, "%Y-%m-%d %H:%M")
  except:
    print("Something went wrong converting dates")
    return
    
  # Store query results
  try:
    c.execute(f"SELECT ID FROM Raids WHERE Date <= (?)", (yesterday,))
  except:
    print("Something went wrong checking for old raids")
    return

  rows = c.fetchall()

  # Check if there are results
  if rows:
    for row in rows:
      try:
        ID = row[0]
        c.execute(f"DELETE FROM RaidReserves WHERE RaidID = (?)", (ID,))
        print(f"Cleaning up raidreserves data for run {ID}")
        conn.commit()
      except:
        print("Something went wrong deleting raidreserves")
        conn.close()
        return
      try:
        ID = row[0]
        c.execute(f"DELETE FROM RaidMembers WHERE RaidID = (?)", (ID,))
        print(f"Cleaning up raidmember data for run {ID}")
        conn.commit()
      except:
        print("Something went wrong deleting raidmembers")
        conn.close()
        return
      try:
        c.execute(f"DELETE FROM Raids WHERE ID = (?)", (ID,))
        print(f"Cleaning up raid data for run {ID}")
        conn.commit()
      except:
        print("Something went wrong deleting raids")
        conn.close()
        return
  else:
      print("No data found to clean up")
      conn.close()
      return
  conn.close()
  return