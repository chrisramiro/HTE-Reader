Quick-Use:

Search for a word on http://historicalthesaurus.arts.gla.ac.uk/
Copy the url of the word list and place it, within quotations, at the "url = " portion of the parser code.

Example:

url = "http://historicalthesaurus.arts.gla.ac.uk/category-selection/?word=cat&label=&category=&startf=&endf=&startl=&endl="

Additionally, change the dest_filename to an appropriate "name.xlsx"

Then, using a terminal:
- Navigate to the appropriate directory in which the parser is stored (i.e. the directory that this txt file should also be in)
- Call "bs4_parser.py" (or "python bs4_parser.py" if you are on Windows)

There should now be an appropriately named .xlsx file within the same directory.