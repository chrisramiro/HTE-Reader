from sense_to_word import *
from word import *

land = []
land.append(Word("land", "all"))
land.append(Word("earth", "all"))
land.append(Word("ground", "all"))

WSC_on_all(land, 10)

plan = [Word("plan", "all"), Word("scheme", "all"), Word("design", "all"), Word("project", "all"), Word("proposal", "all"),
        Word("proposition", "all"), Word("suggestion", "all"), Word("resolution", "all"), Word("motion", "all"),
        Word("precaution", "all")]

WSC_on_all(plan, 10)


inequality = word_maker(["inequality", "disparity", "imparity", "odds", "difference", "unevenness", "partiality", "bias", "weight"], "all")

WSC_on_all(inequality, 10)