from source import *
from openpyxl import Workbook

input_word, word_list = word_list_prompt()

wb = Workbook()
dest_filename = "" + input_word + ".xlsx"
ws1 = wb.active
ws1['A1'], ws1['B1'], ws1['C1'], ws1['J1'] = "Starting Date", "Word Form", "Identifiers", "Category"
length = len(word_list)
abc = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

for num in range(2, length + 2):
    for index in range(0, len(word_list[num - 2])-1):
        ws1[abc[index] + str(num)] = word_list[num - 2][index]
    ws1['J' + str(num)] = word_list[num - 2][-1]
wb.save(filename = dest_filename)
