import excel
import requests
from word import *
from openpyxl import Workbook

input_num = True

while input_num:
    print("Which service would you like to call?")
    print("0) Create a sense list (input: word, part_of_speech)")
    print("1) Create a sense matrix (input: word, part_of_speech)")
    print("2) Create a baseline sense comparison chart (input: word, part_of_speech)")
    print("3) Iterate through a corpus (input: corpus, part_of_speech, num_words) \n")
    input_num = input("Input a number or 'stop' to stop: ")
    input_word = ""
    input_PoS = ""

    def word_PoS_prompt():
        input_w = input("Please enter a word: ")
        input_p = input("Please enter its part of speech ('aj', 'av', 'cj', 'in', 'n', 'p', 'ph', 'v', 'all'): ")

    if input_num == "0":
        print("Sense List chosen.")
        input_word = input("Please enter a word: ")
        input_PoS = input("Please enter its part of speech ('aj', 'av', 'cj', 'in', 'n', 'p', 'ph', 'v', 'all'): ")
        print("File located at: " + excel.write_sense_list(Word(input_word, input_PoS)))
    elif input_num == "1":
        print("Sense Matrix chosen.")
        input_word, input_PoS = word_PoS_prompt()
        print("File located at: " + excel.write_sense_matrix(Word(input_word, input_PoS)))
    elif input_num == "2":
        print("Baseline Comparison Chart chosen.")
        wb = Workbook()
        ws = wb.active
        input_word, input_PoS = word_PoS_prompt()
        save_loc = excel.write_baseline_comparison_chart(Word(input_word, input_PoS), ws)
        wb.save(save_loc)
        print("File located at: " + save_loc)
    elif input_num == "3":
        print("Corpus Iteration Chosen")
        input_corpus = input("Please enter a corpus ('COCA' or 'BNC'): ").lower()
        input_PoS = input("Please enter the part of speech: ('aj', 'av', 'cj', 'n', 'p', 'v'): ")
        input_num_words = int(input("Please enter the number of words desired: "))
        if input_corpus == "coca":
            excel.write_coca_iteration(input_PoS, input_num_words)
        if input_corpus == "bnc":
            excel.write_bnc_iteration(input_PoS, input_num_words)
    elif str(input_num).lower() == "stop":
        exit()
    else:
        print("Invalid number, please try again.")
