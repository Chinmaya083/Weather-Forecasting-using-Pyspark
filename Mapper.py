#!/usr/bin/env python3

import sys
print("City, Year, Month, Day, AvgTemperature")
for line in sys.stdin:
  line = line.strip()
  row = line.split(",")
  if row[3] == "Delhi":
      print(row[3] + ',' + row[6] + ',' + row[4] +  ',' + row[5] + ',' + row[-1])
