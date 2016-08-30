from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
import scipy.stats as stats
import numpy as np
import random
import tsp


num_lists = 20

#---------------------------------------------------------------------#
#                                EXPECTED                             #
#---------------------------------------------------------------------#

def create_real(word):
    """Given a Word, forms the real timeline for the word progressed over
    time."""
    return word.nb_dates

def create_probabilities(word, chaining, complex):
    """Given a word, creates the probabilities of a model to predict the next
    sense, given that the previous senses are true. Chaining list is a list """
    probabilities = []
    sense_pool = word.nb_senses[::]
    real_pool = word.bl_senses[::]
    if complex:
        for i in range(len(sense_pool)):
            successes = 0
            for i in range(num_lists):
                r_copy = real_pool[::]
                s_copy = sense_pool[::]
                if chaining(r_copy, s_copy) == sense_pool[0]:
                    successes += 1
            real_pool.append(sense_pool[0])
            sense_pool = sense_pool[1::]
            probabilities += [successes / num_lists]
        return np.array(probabilities)
    else:
        multiple_bl = []
        for bl in word.bl_senses:
            real_pool = [bl]
            probabilities = []
            for i in range(len(sense_pool)):
                successes = 0
                for i in range(num_lists):
                    if chaining(real_pool, sense_pool) == sense_pool[0]:
                        successes += 1
                real_pool.append(sense_pool[0])
                sense_pool = sense_pool[1::]
                probabilities += [successes / num_lists]
            multiple_bl += [probabilities]
        return max(multiple_bl, key = lambda x : sum(x))

def create_score_comparisons(word, chaining, complex):
    comparisons = []
    sense_pool = word.nb_senses[::]
    real_pool = word.bl_senses[::]
    if complex:
        for i in range(len(sense_pool)):
            comparisons += [chaining(real_pool, sense_pool)]
            real_pool.append(sense_pool[0])
            sense_pool = sense_pool[1::]
        return comparisons
    else:
        multiple_bl = []
        for bl in word.bl_senses:
            real_pool = [bl]
            comparisons = []
            for i in range(len(sense_pool)):
                comparisons += [chaining(real_pool, sense_pool)]
                real_pool.append(sense_pool[0])
                sense_pool = sense_pool[1::]
            multiple_bl += [comparisons]
        return max(multiple_bl, key=lambda x: sum(x))


#---------------------------------------------------------------------#
#                                NULL                                 #
#---------------------------------------------------------------------#
def null_probabilities(word):
    num = word.num_nb_senses
    probabilities = []
    for i in range(num):
        probabilities += [1.0/(num - i)]
    return probabilities

def null_chain(word):
    dates = word.nb_dates[::]
    random.shuffle(dates)
    return dates

def create_null(word):
    """Given a Word, forms a null (random) timeline hypothesis for how
    the word progressed over time."""
    chains = [null_chain(word) for i in range(num_lists)]
    real = create_real(word)
    return np.average([stats.kendalltau(real, null)[0] for null in chains])

#---------------------------------------------------------------------#
#                              PROTOTYPE                              #
#---------------------------------------------------------------------#
def over_all_prototype(real_pool, sense_pool):
    score_total = sum([calculate_pure_score(real_pool[0], vs_sense) for vs_sense in sense_pool])
    next_score = calculate_pure_score(real_pool[0], sense_pool[0])
    return (float) (next_score / score_total)

def one_prototype(real_pool, sense_pool):
    scores = np.array([calculate_score(real_pool[0], vs_sense) for vs_sense in sense_pool])
    min_v = scores.min()
    min_indices = [i for i, v in enumerate(scores) if v == min_v]
    chosen_ind = random.choice(min_indices)
    return sense_pool[chosen_ind]

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

    return choose_best_kendall(word, prototype_chain, False)

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

def over_all_exemplar(real_pool, sense_pool):

    def calculate_distance(real_pool, sense):
        score = 0
        for i in range(len(real_pool)):
            score += calculate_pure_score(sense, real_pool[i])
        return score

    score_total = sum([calculate_distance(real_pool, vs_sense) for vs_sense in sense_pool])
    next_score = calculate_distance(real_pool, sense_pool[0])
    return (float) (next_score / score_total)

def one_exemplar(real_pool, sense_pool):

    def calculate_distance(real_pool, sense):
        score = 0
        for i in range(len(real_pool)):
            score += calculate_score(sense, real_pool[i])
        return score

    distance_scores = np.array([calculate_distance(real_pool, sense) for sense in sense_pool])
    min_v = distance_scores.min()
    min_indices = [i for i, v in enumerate(distance_scores) if v == min_v]
    chosen_ind = random.choice(min_indices)
    return sense_pool[chosen_ind]

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

    def calculate_distance(sense, index, prev, baseline):
        score = baseline[index]
        for i in range(len(prev)):
            score += calculate_score(sense, prev[i])
        return score

    while (date_pool):
        distance_scores = np.array([calculate_distance(sense, ind, sense_chain, against_bl) for ind, sense in enumerate(sense_pool)])
        min_v = distance_scores.min()
        min_indices = [i for i, v in enumerate(distance_scores) if v == min_v]
        chosen_ind = random.choice(min_indices)
        date_chain += [date_pool[chosen_ind]]
        sense_chain += [sense_pool[chosen_ind]]
        del date_pool[chosen_ind]
        del sense_pool[chosen_ind]

    real = create_real(word)
    return stats.kendalltau(real, date_chain)[0]

#---------------------------------------------------------------------#
#                            SIMPLE CHAIN                             #
#---------------------------------------------------------------------#

def iterate_simple(prev, sense_pool):
    sum = 0
    for sense in sense_pool:
        sum += calculate_pure_score(prev, sense)
        prev = sense
    return (float) (sum / len(sense_pool))

def over_all_simple(real_pool, sense_pool):
    score_total = sum([calculate_pure_score(real_pool[-1], vs_sense) for vs_sense in sense_pool])
    next_score = calculate_pure_score(real_pool[-1], sense_pool[0])
    return (float) (next_score / score_total)

def one_simple(real_pool, sense_pool):
    scores = np.array([calculate_score(real_pool[-1], vs_sense) for vs_sense in sense_pool])
    min_v = scores.min()
    min_indices = [i for i, v in enumerate(scores) if v == min_v]
    chosen_ind = random.choice(min_indices)
    return sense_pool[chosen_ind]

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

    return choose_best_kendall(word, simple_chain, False)

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

def over_all_complex(real_pool, sense_pool):
    score_total = 0
    for s in sense_pool:
        curr = []
        for r in real_pool:
            curr += [calculate_pure_score(r, s)]
        score_total += max(curr)
    next_score = max([calculate_pure_score(r_score, sense_pool[0]) for r_score in real_pool])
    return (float) (next_score / score_total)

def one_complex(real_pool, sense_pool):
    random.shuffle(real_pool)
    random.shuffle(sense_pool) #you have to shuffle the sense pool because its just gonna iterate through all of real pool and choose first match
    scores = []
    for s in sense_pool:
        scores += [[calculate_score(s, vs_sense) for vs_sense in real_pool]]
    min_score = 5
    min_index = -1
    global_min = np.array([np.exp(-len(w.listed_cat)) for w in real_pool]).min()
    for i in range(len(scores)):
        for j in range(len(scores[i])):
            if scores[i][j] < min_score:
                min_score = scores[i][j]
                min_index = i
        if min_score == global_min:
            break
    return sense_pool[min_index]

def complex_chain(prev_senses, d_pool, s_pool, starter):
    scores = []
    for s in s_pool:
        scores += [[calculate_score(s, vs_sense) for vs_sense in prev_senses]]
    min_score = 5
    min_index = -1
    global_min = np.array([np.exp(-len(w.listed_cat)) for w in prev_senses]).min()
    for i in range(len(scores)):
        for j in range(len(scores[i])):
            if scores[i][j] < min_score:
                min_score = scores[i][j]
                min_index = i
            if min_score == global_min:
                break
    starter += [d_pool[min_index]]
    prev_senses += [s_pool[min_index]]
    del d_pool[min_index]
    del s_pool[min_index]
    if not d_pool:
        return starter
    return complex_chain(prev_senses, d_pool, s_pool, starter)

def create_complex_chain(word):
    """Given a Word, forms a timeline hypothesis for how the word
    progressed over time that assumes sense emerging at t+1 is minimally
    distant to one existing sense at and prior to t."""

    return choose_best_kendall(word, complex_chain, True)

#---------------------------------------------------------------------#
#                                HYBRID                               #
#---------------------------------------------------------------------#

def over_all_hybrid(real_pool, sense_pool):
    next_score = max(calculate_pure_score(real_pool[0], sense_pool[0]), calculate_pure_score(real_pool[-1], sense_pool[0]))
    score_total_p = [calculate_pure_score(real_pool[0], vs_sense) for vs_sense in sense_pool]
    score_total_s = [calculate_pure_score(real_pool[-1], vs_sense) for vs_sense in sense_pool]
    together = zip(score_total_p, score_total_s)
    together = sum([max(x) for x in together])
    return (float) (next_score / together)

def one_hybrid(real_pool, sense_pool):
    simple_scores = np.array([calculate_score(real_pool[-1], vs_sense) for vs_sense in sense_pool])
    proto_scores = np.array([calculate_score(real_pool[0], vs_sense) for vs_sense in sense_pool])
    min_s = simple_scores.min()
    min_p = proto_scores.min()
    if min_p < min_s:
        min_indices = [i for i, v in enumerate(proto_scores) if v == min_p]
    elif min_s < min_p:
        min_indices = [i for i, v in enumerate(simple_scores) if v == min_s]
    else:
        scores = random.choice([simple_scores, proto_scores])
        min_v = scores.min()
        min_indices = [i for i, v in enumerate(scores) if v == min_v]
    return sense_pool[random.choice(min_indices)]

def hybrid_chain(prev_senses, d_pool, s_pool, starter):
    simple_scores = np.array([calculate_score(prev_senses[-1], vs_sense) for vs_sense in s_pool])
    proto_scores = np.array([calculate_score(prev_senses[0], vs_sense) for vs_sense in s_pool])
    min_s = simple_scores.min()
    min_p = proto_scores.min()
    if min_p < min_s:
        min_indices = [i for i, v in enumerate(proto_scores) if v == min_p]
    elif min_s < min_p:
        min_indices = [i for i, v in enumerate(simple_scores) if v == min_s]
    else:
        scores = random.choice([simple_scores, proto_scores])
        min_v = scores.min()
        min_indices = [i for i, v in enumerate(scores) if v == min_v]
    chosen_ind = random.choice(min_indices)
    starter += [d_pool[chosen_ind]]
    prev_senses += [s_pool[chosen_ind]]
    del d_pool[chosen_ind]
    del s_pool[chosen_ind]
    if not d_pool:
        return starter
    return hybrid_chain(prev_senses, d_pool, s_pool, starter)

def create_hybrid(word):
    """Given a Word, forms a timeline hypothesis for how the word
    progressed over time that assumes sense emerging at t+1 is minimally
    distant to sense appeared at t."""

    return choose_best_kendall(word, hybrid_chain, True)

#---------------------------------------------------------------------#
#                                MST                                  #
#---------------------------------------------------------------------#

def create_tsp(word):
    """Given a Word, forms a minimum spanning tree-based timeline
    hypothesis for how the word progressed over time."""
    t = tsp.tsp(create_matrix(word))
    t.solve()
    return(t.result)

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
    return np.exp(-similarity_score)

def calculate_pure_score(bl_sense, nb_sense):
    similarity_score = 0
    list_range = min(len(bl_sense.listed_cat), len(nb_sense.listed_cat))
    for r in range(list_range):
        if bl_sense.listed_cat[r] == nb_sense.listed_cat[r]:
            similarity_score += 1
        else:
            break
    return similarity_score + 1

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
    matrix = np.transpose(matrix)
    matrix[0] = bl_avg_scores

    for row in range(1, new_length):
        for col in range(1, new_length):
            if row == col:
                matrix[row][col] = 0
            else:
                matrix[row][col] = calculate_score(word.senses[row + bl_length-1], word.senses[col + bl_length-1])

    return np.asarray(matrix)

def choose_best_kendall(word, chain_function, complex):

    date_pool = word.nb_dates[::]
    sense_pool = word.nb_senses[::]
    chains = []

    for i in range(len(word.bl_senses)):
        bl_chains = []
        curr_bl_sense = word.bl_senses[i]
        for j in range(num_lists):
            date_pool_copy = date_pool[::]
            sense_pool_copy = sense_pool[::]
            if complex:
                combined = list(zip(date_pool_copy, sense_pool_copy))
                random.shuffle(combined)
                date_pool_copy = [a[0] for a in combined]
                sense_pool_copy = [a[1] for a in combined]
                bl_chains += [chain_function([curr_bl_sense], date_pool_copy, sense_pool_copy, [])]
            else:
                bl_chains += [chain_function(curr_bl_sense, date_pool_copy, sense_pool_copy, [])]
        chains += [bl_chains]

    real = create_real(word)

    kendalls = []
    for i in range(len(chains)):
        kendalls += [np.average([stats.kendalltau(real, chain)[0] for chain in chains[i]])]
    return max(kendalls)

    """
    def choose_best_bl_kendall(real, chrono_lists):
    kendalls = []
    for i in range(len(chrono_lists)):
        kendalls += [np.average([stats.kendalltau(real, chrono)[0] for chrono in chrono_lists[i]])]
    return max(kendalls)

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

    return max_tau, statistic"""





