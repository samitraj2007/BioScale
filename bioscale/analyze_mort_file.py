import pandas as pd

# Strategy: Find records with clear vital status differences
# Look for patterns where some records have status markers

# Check if there's a README or data dictionary file
import os
mort_dir = 'data/raw/mortality/'
files = os.listdir(mort_dir)
print("Files in mortality directory:")
for f in files:
    print(f"  {f}")
    if f.endswith(('.txt', '.doc', '.pdf', '.md', '.README', '.csv')):
        print(f"    -> Documentation file!")
