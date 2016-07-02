from simple_word import *
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
import scipy.stats as stats
import numpy as np
import random

num_lists = 100

#---------------------------------------------------------------------#
#                                EXPECTED                             #
#---------------------------------------------------------------------#

def create_real(word):
    """Given a Word, forms the real timeline for the word progressed over
    time."""
    return word.nb_dates
#---------------------------------------------------------------------#
#                                NULL                                 #
#---------------------------------------------------------------------#

def null_chain(word):
    dates = word.nb_dates[::]
    random.shuffle(dates)
    return dates

def create_null(word):
    """Given a Word, forms a null (random) timeline hypothesis for how
    the word progressed over time."""
    chains = [null_chain(word) for i in range(num_lists)]
    real = create_real(word)
    return best_of_lot(real, chains)

#---------------------------------------------------------------------#
#                              PROTOTYPE                              #
#---------------------------------------------------------------------#

def prototype_chain(sense, d_pool, s_pool, starter):
    scores = np.array([calculate_score(sense, vs_sense) for vs_sense in s_pool])
    min_v = scores.min()
    min_indices = [i for i, v in enumerate(scores) if v == min_v]
    chosen_ind = random.choice(min_indices)
    starter += [d_pool[chosen_ind]]
    del d_pool[chosen_ind]
    del s_pool[chosen_ind]
    if not d_pool:
        return starter
    return prototype_chain(sense, d_pool, s_pool, starter)

def create_prototype(word):
    """Given a Word, forms a timeline hypothesis for how the word
    progressed over time that assumes sense emerging at t+1 is minimally
    distant to the initial seeding sense(s)."""

    return choose_best_kendall(word, prototype_chain)

    #FOR AVERAGE
    """
    matrix = create_matrix(word)
    date_pool = word.nb_dates
    score_pool = matrix[0][1::]
    pool = zip(date_pool, score_pool)
    pool = [list(x) for x in zip(date_pool, score_pool)]
    random.shuffle(pool)
    pool.sort(key = lambda x: x[1])
    return [int(x) for x in (np.transpose(pool)[0])]
    """



#---------------------------------------------------------------------#
#                              EXEMPLAR                               #
#---------------------------------------------------------------------#

def create_exemplar(word):
    """Given a Word, forms a timeline hypothesis for how the word
    progressed over time that assumes sense emerging at t+1 is minimally
    distant to all existing senses at and prior to t."""

    matrix = create_matrix(word)

    date_chain = []
    sense_chain = []
    date_pool = word.nb_dates[::]
    sense_pool = word.nb_senses[::]
    min = 5

    #gets the first closest sense compared to baseline
    against_bl = np.array(matrix[0][1::])
    min_v = against_bl.min()
    min_indices = [i for i, v in enumerate(against_bl) if v == min_v]
    chosen_ind = random.choice(min_indices)
    date_chain += [date_pool[chosen_ind]]
    sense_chain += [sense_pool[chosen_ind]]
    del date_pool[chosen_ind]
    del sense_pool[chosen_ind]

    def calculate_distance(sense, index, prev):
        score = against_bl[index]
        for i in range(len(prev)):
            score += calculate_score(sense, prev[i])
        return score

    against_bl = matrix[0][1::]

    while (date_pool):
        distance_scores = np.array([calculate_distance(sense, ind, sense_chain) for ind, sense in enumerate(sense_pool)])
        min_v = distance_scores.min()
        min_indices = [i for i, v in enumerate(distance_scores) if v == min_v]
        chosen_ind = random.choice(min_indices)
        date_chain += [date_pool[chosen_ind]]
        sense_chain += [sense_pool[chosen_ind]]
        del against_bl[chosen_ind]
        del date_pool[chosen_ind]
        del sense_pool[chosen_ind]

    return date_chain

#---------------------------------------------------------------------#
#                            SIMPLE CHAIN                             #
#---------------------------------------------------------------------#

def simple_chain(sense, d_pool, s_pool, starter):
    scores = np.array([calculate_score(sense, vs_sense) for vs_sense in s_pool])
    min_v = scores.min()
    min_indices = [i for i, v in enumerate(scores) if v == min_v]
    chosen_ind = random.choice(min_indices)
    starter += [d_pool[chosen_ind]]
    curr_sense = s_pool[chosen_ind]
    del d_pool[chosen_ind]
    del s_pool[chosen_ind]
    if not d_pool:
        return starter
    return simple_chain(curr_sense, d_pool, s_pool, starter)

def create_simple_chain(word):
    """Given a Word, forms a timeline hypothesis for how the word
    progressed over time that assumes sense emerging at t+1 is minimally
    distant to sense appeared at t."""

    return choose_best_kendall(word, simple_chain)

    #FOR AVERAGE
    """
    chain = []
    date_pool = word.nb_dates
    sense_pool = word.nb_senses
    min = 5

    matrix = create_matrix(word)

    #gets all the indices of the minimum scores when compared to baseline
    against_bl = np.array(matrix[0][1::])
    min_v = against_bl.min()
    min_indices = [i for i, v in enumerate(against_bl) if v == min_v]
    chosen_ind = random.choice(min_indices)
    chain += [date_pool[chosen_ind]]
    curr_sense = sense_pool[chosen_ind]
    del date_pool[chosen_ind]
    del sense_pool[chosen_ind]

    while (date_pool):
        vs_scores = np.array([calculate_score(curr_sense, sense) for sense in word.nb_senses])
        min_v = vs_scores.min()
        min_indices = [i for i, v in enumerate(vs_scores) if v == min_v]
        chosen_ind = random.choice(min_indices)
        chain += [date_pool[chosen_ind]]
        curr_sense = sense_pool[chosen_ind]
        del date_pool[chosen_ind]
        del sense_pool[chosen_ind]

    return chain"""

#---------------------------------------------------------------------#
#                            COMPLEX CHAIN                            #
#---------------------------------------------------------------------#
    """Given a Word, forms a timeline hypothesis for how the word
    progressed over time that assumes sense emerging at t+1 is minimally
    distant to one existing sense at and prior to t."""

#randomize the pool beforehand

#---------------------------------------------------------------------#
#                                MST                                  #
#---------------------------------------------------------------------#


#run all but cut off

def create_mst(word):
    """Given a Word, forms a minimum spanning tree-based timeline
    hypothesis for how the word progressed over time."""
    mst = minimum_spanning_tree(create_matrix(word))
    mst.toarray().astype(int)
    return mst

#---------------------------------------------------------------------#
#                    HELPER FUNCTIONS                                 #
#---------------------------------------------------------------------#

def calculate_score(bl_sense, nb_sense):
    similarity_score = 0
    list_range = min(len(bl_sense.listed_cat), len(nb_sense.listed_cat))
    for r in range(list_range):
        if bl_sense.listed_cat[r] == nb_sense.listed_cat[r]:
            similarity_score += 1
        else:
            break
    return exp(-similarity_score)

def create_matrix(word):
    if word.length == 0 or word.length == 1:
        print("Sense Matrix not possible for given input: " + word.label)
        exit()
    length = len(word.senses)
    nb_length = word.num_nb_senses
    bl_length = word.num_bl_senses
    matrix = [[0 for x in range(nb_length)] for y in range(bl_length)]
    bl_avg_scores = []


    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            matrix[row][col] = calculate_score(word.senses[row], word.senses[col + bl_length])

    bl_avg_scores = matrix[0]

    for i in range(bl_length-1):
        bl_avg_scores = [x + y for x, y in zip(bl_avg_scores, matrix[i+1])]

    bl_avg_scores = [0] + [score/bl_length for score in bl_avg_scores]

    new_length = length - bl_length + 1
    matrix = [[0 for x in range(new_length)] for y in range(new_length)]
    matrix[0] = bl_avg_scores
    matrix = numpy.transpose(matrix)
    matrix[0] = bl_avg_scores

    for row in range(1, new_length):
        for col in range(1, new_length):
            if row == col:
                matrix[row][col] = 0
            else:
                matrix[row][col] = calculate_score(word.senses[row + bl_length-1], word.senses[col + bl_length-1])

    return np.asarray(matrix)

def choose_best_bl_kendall(real, chrono_lists):
    kendalls = []
    for i in range(len(chrono_lists)):
        kendalls += [np.average([stats.kendalltau(real, chrono)[0] for chrono in chrono_lists[i]])]
    return kendalls.index(max(kendalls)), max(kendalls)

def choose_best_kendall(word, chain_function):

    date_pool = word.nb_dates[::]
    sense_pool = word.nb_senses[::]
    chains = []

    for i in range(len(word.bl_senses)):
        bl_chains = []
        curr_bl_sense = word.bl_senses[i]
        for j in range(num_lists):
            date_pool_copy = date_pool[::]
            sense_pool_copy = sense_pool[::]
            bl_chains += [chain_function(curr_bl_sense, date_pool_copy, sense_pool_copy, [])]
        chains += [bl_chains]

    real = create_real(word)

    k_index, k_value = (choose_best_bl_kendall(real, chains))
    best_lot = chains[k_index]

    return best_of_lot(real, best_lot)

def best_of_lot(real, lot):
    best_index = -1
    max_tau = -1.01
    statistic = 0
    for i in range(len(lot)):
        if stats.kendalltau(real, lot[i])[0] > max_tau:
            best_index = i
            max_tau = stats.kendalltau(real, lot[i])[0]
            statistic = stats.kendalltau(real, lot[i])[1]

    return str(lot[best_index]) + " Tau: " + str(max_tau) + ", P-Value: " + str(statistic)





