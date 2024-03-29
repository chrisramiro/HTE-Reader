
class Sense:

    def __init__(self, word, raw_list, index):
        self.word = word
        self.date = self.date_normalizer([raw_list[index].contents[-1]][0])             #int or bool
        self.word_form = ' '.join([b.text for b in raw_list[index].find_all("b")])      #str
        self.identifiers = ' -> '.join([a.text for a in raw_list[index].find_all("a")]) #str
        self.listed_id = [a.text for a in raw_list[index].find_all("a")]                #list
        self.categories = ' '.join([s.text for s in raw_list[index].find_all("span")])  #str
        self.listed_cat = self.categorizer(self.categories)
        self.PoS = self.categories[-2:].strip();
        if self.listed_cat[0] == "01":         #1 for External, 2 for Mental, 3 for Social
            self.externality = 1
        else:
            self.externality = 0

    def date_normalizer(self, date):
        """Takes a date, which may range in form from (OE-3271) or
    	(c1234 - 3210) or (a2574) or (1257) etc., and returns it
    	as a form "1234" as a starting date, and also as a string in a list"""
        # retrieve the date as a string
        date = str(date)
        date = date[2::]  # Remove the initial "("
        if date[0] == "O":
            return "OE"
        dash_index = date.find("–") #only starting dates should be used
        if dash_index == -1:
            return False
        if date[0].isalpha():
            date = date[1::]
        return int(date[:4:]) #dates less than 4 digits are displayed as "OE"

    def categorizer(self, category):
        """Takes a category of form "01.02.03.04.05 n" and returns a
        list of lists of form ['01', '02', '03', '04', '05']
        This implementation ignores secondary meanings, which occur after
        a pipe (i.e. 01.02.03 | 04.05 n where 04.05 n is ignored)"""
        listed_cat, i = [], 0
        while not category[i].isalpha():
            if category[i].isdigit():
                listed_cat.append(category[i:i + 2:])
                if category[i + 2] == "|":
                    break
                i += 3
        return listed_cat

    def __str__(self):
        return str(self.date) + " | " + self.word_form + " | " + self.identifiers + " | " + self.categories + " | " + str(self.listed_cat)
