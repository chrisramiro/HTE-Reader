import requests
import word
import sense
from bs4 import *
from math import *

input_num = True

"""while input_num:
    print("Which service would you like to call?")
    print("0) Create a word list (input: word, part_of_speech")
    print("1) Create a sense matrix (input: word, part_of_speech")
    print("2) Create a baseline sense comparison chart (input: word, part_of_speech")
    print("3) Create a sense matrix (input: corpus, part_of_speech, num_words) \n")
    input_num = input("Input a number: ")

    if input_num == 0:
        input_num == False
        print()
    elif input_num == 1:
        input_num == False
        print()
    elif input_num == 2:
        input_num == False
        print()
    elif input_num == 3:
        input_num == False
        print()
    else:
        print("Invalid number, please try again.")"""

def categorizer(category):
    """Takes a category of form "01.02.03.04.05 n" and returns a
    list of lists of form ['01', '02', '03', '04', '05']
    This implementation ignores secondary meanings, which occur after
    a pipe (i.e. 01.02.03 | 04.05 n where 04.05 is ignored)
    """
    listed_cat, i = [], 0
    while not category[i].isalpha():
        if category[i].isdigit():
            listed_cat.append(category[i:i + 2:])
            if category[i + 2] == "|":
                break
            i += 3
    return listed_cat


def make_word_list(word, part_of_speech):
    """Takes a word and searches for it within the HTE database,
    returning a list with the same information, ordered by
    [date, word_form, identifiers, category]"""

    if part_of_speech == "v":
        url = "http://historicalthesaurus.arts.gla.ac.uk/category-selection/?word=" + word + "&pos%5B%5D=allv&pos%5B%5D=v&pos%5B%5D=vi&pos%5B%5D=vm&pos%5B%5D=vp&pos%5B%5D=vr&pos%5B%5D=vt&label=&category=&startf=&endf=&startl=&endl="
    elif part_of_speech == "all":
        url = "http://historicalthesaurus.arts.gla.ac.uk/category-selection/?word=" + word + "&label=&category=&startf=&endf=&startl=&endl="
    else:
        url = "http://historicalthesaurus.arts.gla.ac.uk/category-selection/?word=" + word + "&pos%5B%5D=" + part_of_speech + "&label=&category=&startf=&endf=&startl=&endl="

    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    for a in soup.find_all("a"):
        del a['href']

    catOdds = soup.find_all("p", "catOdd")
    catEvens = soup.find_all("p", "catEven")
    allCat = catOdds + catEvens

    word_list = []

    for index in range(0, len(allCat)):
        date = date_normalizer([allCat[index].contents[-1]][0])
        # Skip past the current selection if the date is not a starting date
        if not date:
            continue
        word_form = [b.text for b in allCat[index].find_all("b")]
        identifiers = [a.text for a in allCat[index].find_all("a")]
        category = [s.text for s in allCat[index].find_all("span")]

        word_list.append([date] + word_form + identifiers + category)

    # this separation is done so that we can sort the list with OE at the beginning instead of the end
    OE_list = [word for word in word_list if word[0] == "OE"]
    non_OE_list = [word for word in word_list if word[0] != "OE"]
    word_list = OE_list + sorted(non_OE_list, key=lambda x: x[0])

    return word_list


def word_list_prompt():
    """The beginning prompt of the bs4 programs in this suite, asking
	for an input word and an input part of speech to then construct
	a word list"""
    input_word = input('Enter your desired word: ')
    print('Enter your desired part of speech ("aj", "av", "cj", "in", "n", "p", "ph", "v")')
    input_PoS = input('Replying with "all" anything else will return all: ')
    return input_word + "[" + input_PoS + "]", make_word_list(input_word, input_PoS)


def date_normalizer(date):
    """Takes a date, which may range in form from (OE-3271) or
	(c1234 - 3210) or (a2574) or (1257) etc., and returns it
	as a form "1234" as a starting date, and also as a string in a list"""
    # retrieve the date as a string
    date = str(date)
    # Remove the initial "("
    date = date[2::]
    if date[0] == "O":
        return "OE"
    # Removes "a" or "c" in front of "a/c1234" (where a, c means "about/circa")
    if date[0].isalpha():
        date = date[1::]
    new_date = ""
    while date[0].isdigit():
        new_date += date[0]
        date = date[1::]
    # Return false if the date is not a starting date (i.e. the parentheses is immediately after it)
    if date[0] == ")":
        return False
    return int(new_date)


def get_selection(col_start, col_end, row):
    """Takes excel col indices and creates a excel formula-usable
	letter-number combination that is one row long of form:
	col_star:, e.x. =PEARSON(E19:AG19,E18:AG18)"""

    abc = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    abc_end = ""
    abc_index = -1
    double_start = False
    double_end = False
    if col_end < col_start:
        print("ERROR: invalid selection, col_end greater than col_row")
        return
    while col_start > 25:
        double_start = True
        abc_index += 1
        col_start -= 26
    if double_start:
        arr_start = abc[abc_index] + abc[col_start]
    else:
        arr_start = abc[col_start]
    abc_index = -1
    while col_end > 25:
        double_end = True
        abc_index += 1
        col_end -= 26
    if double_start:
        arr_end = abc[abc_index] + abc[col_end]
    else:
        arr_end = abc[col_end]
    arr = arr_start + str(row) + ":" + arr_end + str(row)
    return arr


def create_sense_by_n(input_row, input_baseline_sense, new_word_list, worksheet):
    """Creates a 2 by n sequence of excel cells that compare a single base sense
    against multiple other senses (that occur later chronologically) by the
    numbers gained from the categorizer function, at a given row"""

    base_cell = worksheet.cell(row=input_row + 1, column=1)
    base_cell.value = ''.join(str(input_baseline_sense))

    length = len(new_word_list)

    for num in range(2, length + 2):
        row1 = worksheet.cell(row=input_row, column=num)
        row1.value = ''.join(str(new_word_list[num - 2][0]))

    categories = []
    for word in new_word_list:
        categories.append(categorizer(word[-1]))
    base_category = categorizer(input_baseline_sense[-1])

    for col in range(2, length + 2):
        cur_cell = worksheet.cell(row=input_row + 1, column=col)
        similarity_score, index = 0, 0
        list_range = min(len(base_category), len(categories[col - 2]))
        for r in range(0, list_range):
            if base_category[r] == categories[col - 2][r]:
                similarity_score += 1
            else:
                break
        cur_cell.value = exp(-similarity_score)


def make_averaged(input_word, word_list, index, worksheet):
    """Creates several sense_by_n arrays using the beginning baseline word_list
	and calculates their average at the end, also returns the proper locations
	to calculate the pearson correlation coefficient"""

    num_of_senses = index + 1
    if num_of_senses == 1:
        print("Only one baseline found for " + input_word + ".")

    mod_word_list = word_list[index + 1::]
    length = len(mod_word_list)
    for i in range(0, index + 1):
        baseline_sense = word_list[int(i)]
        create_sense_by_n(2 * (i + 1) - 1, baseline_sense, mod_word_list, worksheet)

        # Creates the final row of averages
    avg_row = 2 * (index + 2)

    for num in range(2, length + 2):
        row1 = worksheet.cell(row=avg_row - 1, column=num)
        row1.value = mod_word_list[num - 2][0]

    avg_cell = worksheet.cell(row=avg_row, column=1)
    avg_cell.value = "AVERAGES"
    for j in range(2, length + 2):
        avg_cell = worksheet.cell(row=avg_row, column=j)
        avg_sum = 0
        for i in range(0, index + 1):
            cur_cell = worksheet.cell(row=2 * (i + 1), column=j)
            avg_sum += cur_cell.value
        avg_cell.value = round(avg_sum / num_of_senses, 3)

    x_vals = get_selection(1, length, avg_row)
    y_vals = get_selection(1, length, avg_row - 1)
    return x_vals, y_vals
