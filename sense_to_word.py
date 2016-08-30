import random
import numpy as np
from word import *

def word_maker(words, PoS):
    if type(PoS) == list:
        words = zip(words, PoS)
        return [Word(words[i][0], words[i][1]) for i in range(len(words))]
    else:
        return [Word(word, PoS) for word in words]

def WSC_on_all(words, num):
    print("Test for " + str(words))
    models = [0, 0, 0, 0, 0]
    for i in range(num):
        models[0] += word_space_creation(words, null_attr)
        models[1] += word_space_creation(words, simple_attr)
        models[2] += word_space_creation(words, prototype_attr)
        models[3] += word_space_creation(words, exemplar_attr)
        models[4] += word_space_creation(words, complex_attr)
    models = np.array(models)
    models /= 10
    print("In order: Null, Simple, Prototype, Exemplar, Complex")
    print(models)

def word_space_creation(words, model):
    accuracy = 0
    space = sum([word.num_nb_senses for word in words])
    base_words = [[word.bl_senses[0]] for word in words]
    senses = [word.nb_senses[i] for word in words for i in range(word.num_nb_senses)]
    random.shuffle(senses)
    while(senses):
        chosen = model(base_words, senses[0])
        if senses[0] in words[chosen].nb_senses:
            accuracy += 1
        for i in range(len(base_words)):
            if(senses[0] in words[i].nb_senses):
                base_words[i].append(senses[0])
                break
        senses = senses[1::]
    return (float) (accuracy / space)

def contains(words, index, sense):
    if (sense in words[index].nb_senses):
        return 1
    return 0


def null_attr(curr_set, curr_sense):
    return random.randrange(0, len(curr_set))


def simple_attr(curr_set, curr_sense):
    scores = []
    for i in range(len(curr_set)):
        scores.append(calculate_pure_score(curr_set[i][-1], curr_sense))
    m = max(scores)
    indices = [i for i, v in enumerate(scores) if v == m]
    return random.choice(indices)


def prototype_attr(curr_set, curr_sense):
    scores = []
    for i in range(len(curr_set)):
        scores.append(calculate_pure_score(curr_set[i][0], curr_sense))
    m = max(scores)
    indices = [i for i, v in enumerate(scores) if v == m]
    return random.choice(indices)


def exemplar_attr(curr_set, curr_sense):
    scores = []
    for i in range(len(curr_set)):
        scores.append(0)
        for j in curr_set[i]:
            scores[i] += calculate_pure_score(j, curr_sense)
    m = max(scores)
    indices = [i for i, v in enumerate(scores) if v == m]
    return random.choice(indices)


def complex_attr(curr_set, curr_sense):
    scores = []
    for i in range(len(curr_set)):
        scores.append(max([calculate_pure_score(curr_set[i][j], curr_sense) for j in range(len(curr_set[i]))]))
    m = max(scores)
    indices = [i for i, v in enumerate(scores) if v == m]
    return random.choice(indices)


def calculate_pure_score(bl_sense, nb_sense):
    similarity_score = 0
    list_range = min(len(bl_sense.listed_cat), len(nb_sense.listed_cat))
    for r in range(list_range):
        if bl_sense.listed_cat[r] == nb_sense.listed_cat[r]:
            similarity_score += 1
        else:
            break
    return similarity_score + 1