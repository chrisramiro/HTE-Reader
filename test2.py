import scipy.stats as stats
from word import *
from word_data_structures import *

wordy = Word("fire", "all")

#print(create_mst(wordy))

print("REAL: ")
print(create_real(wordy), flush=True)

print()

print("NULL: ")
print(create_null(wordy), flush=True)

print()

print("PROTOTYPE: ")
print(create_prototype(wordy), flush=True)

print()

#print("EXEMPLAR:  " + str(create_exemplar(wordy)))

print("SIMPLE: ")
print(create_simple_chain(wordy), flush=True)