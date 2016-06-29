from source import *
from openpyxl import Workbook

# <----- BEGIN USER INTERACTION ----->

input_word, word_list = word_list_prompt()

if len(word_list) == 1:
    print("There is only one sense and therefore no comparison can be made.")
    raise SystemExit

wb = Workbook()
ws1 = wb.active

print('Would you like to use one baseline sense or all the beginning senses?')
input_choice = input('Reply 0 for the average or 1 for one sense: ')

# <----- USER CHOOSES ALL THE BEGINNING SENSES ----->
if int(input_choice) == 0:
    dest_filename = "average_compared_" + input_word + ".xlsx"

    index = 0
    while True:
        try:
            if word_list[index][0] != word_list[index + 1][0]:
                break
        except:
            print("Don't use" + word_list[index])
        index += 1

    make_averaged(input_word, word_list, index, ws1)

# <----- USER CHOOSES A BASELINE SINGLE SENSE ----->

elif input(input_choice) == 1:
    print("Possible baseline senses:")
    index = 0
    #the printed senses will all be OE or the earliest senses (that are equivalent)
    while True:
        print(str(index) + ": " + str(word_list[index][:-1:]))
        if word_list[index][0] != word_list[index + 1][0]:
            break
        index += 1

    input_index = input('Enter the number of the desired baseline sense: ')
    baseline_sense = word_list[int(input_index)]
    mod_word_list = word_list[index + 1::]
    dest_filename = "single_compared_" + input_word + "_sense_#_" + input_index + ".xlsx"

    create_sense_by_n(1, baseline_sense, mod_word_list, ws1)

else:
    print("Please try again with a valid number.")

wb.save(filename = dest_filename)
