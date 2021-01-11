#!/usr/bin/env python3

import sys

#f = open("new.csv")
#f.write("City, Year, Month, Day, AvgTemperature\n")
for line in sys.stdin:
  try:
    line = line.strip()
    city, year, month, day, temp = line.split(',')
    print(str(city) + ',' + str(year) + ',' + str(month) + ',' + str(day) + ',' + str(temp))
  except:
    pass
