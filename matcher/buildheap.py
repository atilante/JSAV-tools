#!/usr/bin/python3
# -*- coding: utf-8 -*-

import copy

class BuildHeapMatcher:

    def __init__(self):
        # Sequential definitions of main loop variants for 10-element
        # Build-heap. Each sequence of five numbers refers to the build-heap
        # array indices for which the Heapify procedure is called.
        self.loop_variants = (
            # code, name, sequence
            (100, 'Correct',            (4, 3, 2, 1, 0)), # also "Level LR"
            (200, 'Zigzag RL',          (4, 3, 1, 2, 0)),
            (300, 'Zigzag LR',          (3, 4, 2, 1, 0)),
            (400, 'Level LR',           (3, 4, 1, 2, 0)),
            (500, 'Top-down',           (0, 1, 2, 3, 4)),
            (600, 'Zigzag top-down LR', (0, 1, 2, 4, 3)),
            (700, 'Zigzag top-down RL', (0, 2, 1, 4, 3)),
            (800, 'Inorder',            (3, 1, 4, 0, 2))
        )

        # List of heapify algorithms. These are used together with loop
        # variants.
        # Code = code of loop variant + code of heapify variant
        self.heapify_algorithms = (
            # code, name, algorithm
            (0, 'Correct', self.min_heapify),
            (1, 'No-Recursion', self.no_recursion),
            (2, 'Delayed recursion', self.delayed_recursion),
            (3, 'Heapify-with-Father LR', self.heapify_with_father_lr),
            (4, 'Heapify-with-Father LR recursive',
                self.heapify_with_father_lr_recursive),
            (5, 'Heapify-with-Father RL', self.heapify_with_father_rl),
            (6, 'Heapify-with-Father RL recursive',
                 self.heapify_with_father_rl_recursive),
            (7, 'Heapify-up', self.heapify_up),
            (8, 'Max-heapify', self.max_heapify),
            (9, 'Wrong-duplicate', self.wrong_duplicate),
            (10, 'Path-Bubblesort', self.path_bubblesort),
            (11, 'Smallest-Instantly-Up', self.smallest_instantly_up)
        )

        self.compute_class_preferences()


        # For delayed recursion which uses and compute_level_indices().
        self.heap_levels = []
        self.assumed_heap_size = 0

        # Statistics for matching
        self.statistics = {
            'cross-match': [0] * (13 * 13), # Replicated study algo variants
            'misconception-as-correct': 0,
            'multiple-misconceptions': 0,
            'total-matched': 0
        }
        self.statistics['cross-match']

    def compute_class_preferences(self):
        """Computes class preferences for loop variant hypothesis."""

        # Manual analysis of 1430 Build-heap submissions.
        # Class code = code of main loop variant + code of heapify
        #
        #              Code of main loop variant
        #        100  200  300  400  500  600  700  800
        #      +---------------------------------------
        # H  0 | 927   68   14   26    4    0    0   14
        # e  1 |  51   12    4    2    2    0    0    3
        # a  2 |  24    3    1    3    0    0    0    1
        # p  3 |   0    1    0    0    0    0    0    0
        # i  4 |   1    3    0    0    0    0    0    0
        # f  5 |   5    1    0    0    0    0    0    0
        # y  6 |  22    1    0    1    0    0    0    0
        #    7 |   5    0    0    0    0    1    1    0
        #    8 |   4    0    0    1    0    0    0    0
        #    9 |  11    1    0    0    1    0    0    1
        #   10 |   1    0    0    0    0    0    0    0
        #   11 |   0    0    0    0    1    0    0    0
        #
        # Unrecognised: 208


        # Order of preference for class codes when there are multiple
        # equal choices. Lower preference value means higher preference.
        # This preference order has been computed for classes that had at least
        # three submissions in the manual classification.
        preference_order = [100, 200, 101, 400, 102, 106, 300, 800,
            201, 109, 105, 107, 108, 301, 500, 202, 206, 402, 801]
        self.class_preference = { preference_order[i] : i
            for i in range(len(preference_order)) }

        # Other class codes: compute from loop variant and heapify variant
        # probabilities.


        loop_variant_probabilities = [
            # code, estimated probability
            (100, 1051/1430), # Correct
            (200,   90/1430), # Zigzag RL
            (300,   19/1430), # Zigzag LR
            (400,   33/1430), # Level LR
            (500,    7/1430), # Top-down
            (600,    1/1430), # Zigzag top-down LR
            (700,    1/1430), # Zigzag top-down RL
            (800,   19/1430)  # Inorder
            ]

        heapify_variant_probabilities = [
            # code, estimated probability
            ( 0, 1053/1430), # Correct
            ( 1,   74/1430), # No-recursion
            ( 2,   32/1430), # Delayed recursion
            ( 3,    1/1430), # Heapify-with-Father LR
            ( 4,    4/1430), # Heapify-with-Father LR recursive
            ( 5,    6/1430), # Heapify-with-father RL
            ( 6,   24/1430), # Heapify-with-father RL recursive
            ( 7,    7/1430), # Heapify-up
            ( 8,    5/1430), # Max-heapify
            ( 9,   14/1430), # Wrong-duplicate
            (10,    1/1430), # Path-bubblesort
            (11,    1/1430), # Smallest-instantly-up
            ]

        probabilities_and_codes = []

        for lv in loop_variant_probabilities:
            for hv in heapify_variant_probabilities:
                code = lv[0] + hv[0]
                probability = lv[1] * hv[1]
                probabilities_and_codes.append((probability, code))

        probabilities_and_codes.sort(reverse = True)
        preference_value = len(preference_order)
        for x in probabilities_and_codes:
            probability = x[0]
            code = x[1]
            if code not in self.class_preference:
                self.class_preference[code] = preference_value
                preference_value += 1

        # Test
#         print("   | 100 200 300 400 500 600 700 800")
#         print("---+--------------------------------")
#         for heapify_code in range(0, 12):
#             s = "{:2} |".format(heapify_code)
#             for loop_code in range(100, 900, 100):
#                 code = loop_code + heapify_code
#                 s += " {:3}".format(self.class_preference[code])
#             print(s)


    def compute_level_indices(self, heap_size):
        """Computes left and right indices of nodes for each level of the
        binary heap.

        Parameters:
        heap_size: positive integer, size of the heap

        Returns:
        list containing tuples (l, r) where l and r are left and right indices
        of one level in the binary tree representation of the heap. Levels
        are traversed top-down.
        """
        level_indices = []
        i = 0
        level_width = 1
        while (i < heap_size):
            level_indices.append((i, min(i + level_width - 1, heap_size - 1)))
            i += level_width
            level_width *= 2
        self.heap_levels = level_indices
        self.assumed_heap_size = heap_size

    def describe_variants(self):
        print("The following Build-heap variants have been defined.")
        print("Code, loop, heapify")
        print("0 unrecognised or not sure")
        for loop in self.loop_variants:
            for algo in self.heapify_algorithms:
                print("{} {} / {}".format(loop[0] + algo[0], loop[1], algo[1]))


    def parse_recording(self, recording):
        """Parses a JSAV recording of build-heap exercise into a compact
        representation.

        Parameters:
        recording (list): list of *steps*, each step is a dict with keys:
            'ind': list of dicts. Each dict is key-value pair: {'v': x}, where
                   x is a value in an array storing the binary heap.
            'style': string, ignored
            'classes': string, ignored

        Returns:
        (input, states, swaps)
            input: list of integers representing the heap in its initial state
            states: list of tuples, each representing the heap array as sequence
                    of states
            swaps: list of pairs of integers, each referring to array indices
                   involved in a swap
        """
        steps = len(recording)

        # Size of the binary heap
        array_size = len(recording[0]['ind'])

        # Input of the exercise
        input = []
        for x in recording[0]['ind']:
            input.append(x['v'])


        # Actual swaps performed.
        # Note that JSAV might record some steps redundant, as all the user's
        # actions do not change the heap array.
        swaps = []
        states = [tuple(input)]
        heap_array_prev = input
        for i in range(1, steps):
            heap_array = []
            for x in recording[i]['ind']:
                heap_array.append(x['v'])

            swapped = []    # contains array indices of swaps
            for j in range(array_size):
                if heap_array[j] != heap_array_prev[j]:
                    swapped.append(j)
            if len(swapped) == 2:
                swaps.append(tuple(swapped))
                states.append(tuple(heap_array))
            heap_array_prev = heap_array

        return (input, states, swaps)


    def match(self, recording, options = {'similarity': 'states',
        'Jaccard': False, 'threshold': 0, 'verbosity': 0}, debug_text = []):
        """Matches a JSAV recording of build-heap exercise to known
        misconceived algorithms.

        Parameters:
        recording (list): list of *steps*, each step is a dict with keys:
            'ind': list of dicts. Each dict is key-value pair: {'v': x}, where
                   x is a value in an array storing the binary heap.
            'style': string, ignored
            'classes': string, ignored

        options: optional dictionary
            'similarity': similarity algorithm for student's submission and
            |             result of misconceived algorithm
            +-- 'states': state-based similarity algorithm
            +-- 'lcs'   : longest common subsequence of swaps
            +-- 'dtw'   : dynamic time warping of swaps

            'Jaccard': use Jaccard similarity coefficient with the similarity
                       algorithm; either True or False.

            'threshold':
                'Jaccard' == False: if the best matching candidate sequence
                has match below the threshold, the recording will be classified
                as "unknown"
                'Jaccard' == True: the same, but relative value 0 <= x < 1
                for Jaccard similarity coefficient.

            'verbosity':
                0: do nothing
                1: add the following string to debug_text:
                   "chosen class, highest similarity, equally best classes"

        debug_text = a list. If options['verbosity'] != 0, appends a string
           to this list describing details of the classification.

        """

        input, states, swaps = self.parse_recording(recording)

        best_similarity = 0 # The initial state will always match
        best_classes = [0]  # The "unknown" class

        for loop in self.loop_variants:
            for algo in self.heapify_algorithms:
                class_code = loop[0] + algo[0]

                algo_states, algo_swaps = self.build_heap_variant(loop[2],
                    algo[2], input)
                #print("{}: {} / {}".format(class_code, loop[1], algo[1]))
                #self.print_heap_sequence(algo_states, algo_swaps)

                m = 0
                len_algo = 0.1
                len_states = 0.1
                if (algo[1] == 'Delayed recursion'):
                    m = 1 + self.lcs_similarity_delayed_recursion(algo_swaps,
                                                                  swaps)
                else:
                    if options['similarity'] == 'states':
                        m = self.state_similarity(algo_states, states)
                        len_algo = len(algo_states)
                        len_states = len(states)
                    elif options['similarity'] == 'lcs':
                        m = self.lcs_similarity(algo_swaps, swaps)
                        len_algo = len(algo_swaps)
                        len_states = len(swaps)
                    else:
                        raise Exception(
                            "Similarity algorithm '{}' not implemented"
                            .format(options['similarity']))

                if options['Jaccard'] == True:
                    # Jaccard similarity coefficient:
                    # J(X,Y) = |X union Y| / |X intersection Y|
                    # = similarity(X,Y) / (len(X) + len(Y) - similarity(X,Y)
                    m /= (len_algo + len_states - m)

                if (m > best_similarity):
                    best_classes = [class_code]
                    best_similarity = m
                elif (m == best_similarity):
                    best_classes.append(class_code)

        chosen_class = 0
        # Choose naively the first class from equal candidates
        if best_similarity > options['threshold']:
            chosen_class = best_classes[0]

        if options['verbosity'] == 1:
            s = str(best_similarity)
            if chosen_class == 0:
                s += ' (under threshold)'
            else:
                for c in best_classes:
                    s += ' ' + str(c)
            debug_text.append(s)

        return chosen_class

    def choose_class(self, best_classes):
        """Chooses the most preferable class among given equal candidates.

        Parameters:
        best_classes: list of class codes

        Returns:
        one of class codes in best_classes
        """

        best_preference = 1000000
        best_class = 0
        #delayed_recursion_codes = [] # test
        for c in best_classes:
            #if c % 100 == 2:
            #    delayed_recursion_codes.append(c)
            p = None
            if c in self.class_preference:
                p = self.class_preference[c]
            else:
                p = c
            if p < best_preference:
                best_preference = p
                best_class = c
        #if (len(delayed_recursion_codes) > 0):
        #    print("Delayed-recursion: {} over {}".format(best_class,
        #        delayed_recursion_codes))
        return best_class


    def loop_hypothesis_match(self, recording, options = {'similarity': 'states',
        'Jaccard': False, 'threshold': 0, 'verbosity': 0}, debug_text = []):
        """The same as replicated_study_match, but with main loop variant
        hypothesis.

        Parameters:
        recording (list): list of *steps*, each step is a dict with keys:
            'ind': list of dicts. Each dict is key-value pair: {'v': x}, where
                   x is a value in an array storing the binary heap.
            'style': string, ignored
            'classes': string, ignored
        """

        input, states, swaps = self.parse_recording(recording)

        best_similarity = 0 # The initial state will always match
        best_classes = [0]  # The "unknown" class
        algo_score = {}
        algo_perfect_match = []

        for loop in self.loop_variants:
            for algo in self.heapify_algorithms:
                class_code = loop[0] + algo[0]

                algo_states, algo_swaps = self.build_heap_variant(loop[2],
                    algo[2], input)

                score = 0
                len_algo = 0.1
                len_states = 0.1
                if (algo[1] == 'Delayed recursion'):
                    score = 1 + self.lcs_similarity_delayed_recursion(algo_swaps,
                                                                  swaps)
                else:
                    if options['similarity'] == 'states':
                        score = self.state_similarity(algo_states, states)
                        len_algo = len(algo_states)
                        len_states = len(states)
                    elif options['similarity'] == 'lcs':
                        score = self.lcs_similarity(algo_swaps, swaps)
                        len_algo = len(algo_swaps)
                        len_states = len(swaps)
                    else:
                        raise Exception(
                            "Similarity algorithm '{}' not implemented"
                            .format(options['similarity']))

                algo_score[class_code] = score
                if (algo_states == states):
                    algo_perfect_match.append(class_code)
                if (score > best_similarity):
                    best_classes = [class_code]
                    best_similarity = score
                elif (score == best_similarity):
                    best_classes.append(class_code)

        # Classify sequence

        # A: 100% correct.
        # B: 100% match with some misconceived candidate.
        # If there are several candidates fulfilling the property, the one
        # with the lowest index is chosen. The 'Correct' variant has the lowest
        # index and the 'Other' variant the highest.


        if (len(algo_perfect_match) > 0):
            if (len(algo_perfect_match) > 1):
                if 100 in algo_perfect_match:
                    self.statistics['misconception-as-correct'] += 1
                else:
                    self.statistics['multiple-misconceptions'] += 1

            return self.choose_class(algo_perfect_match)


        # C: No perfect match and the sequence of some misconceived algorithm
        # matches at least two steps further than the correct algorithm.
        max_score = max(algo_score)
        if (max_score - algo_score[100] >= 2):
            best_candidates = [i for i in range(len(algo_perfect_match))
                if algo_score[i] == max_score]
            if (len(best_candidates) > 1):
                self.statistics['multiple-misconceptions'] += 1
            c = self.choose_class(best_candidates)
            if c > 0:
                return c

        # D: None of the rules apply.
        if (len(states) == 1):
            # No-Swaps
            return 10

        algo_states, algo_swaps = self.build_heap_variant((4, 3, 2, 1, 0),
            self.min_heapify, input)
        if self.correct_with_extra_steps(states, algo_states):
            # Extra-Steps-After-Correct
            return 11

        if self.swaps_resemble_build_heap(swaps, len(states[0])):
            # Swaps-Resemble-Build-heap
            return 12

        if self.min_heap_property(states[-1], 0):
            # Nonsystematic-Build-heap:
            # Minimum heap property holds for end state
            return 13

        if self.swaps_are_legal(states, swaps, len(states[0])):
            # Legal-swaps
            return 14

        if self.swaps_are_legal_by_index(swaps, len(states[0])):
            # Legal-swap-indices
            return 15

        return 0


    def replicated_study_match(self, recording):
        """Matches a JSAV recording of build-heap exercise to known
        misconceived algorithms according to study: Ville Karavirta,
        Ari Korhonen, and Otto Seppälä. 2013. Misconceptions in Visual
        Algorithm Simulation Revisited: On UI’s Effect on Student Performance,
        Attitudes, and Misconceptions. DOI 10.1109/LaTiCE.2013.35

        Parameters:
        recording (list): list of *steps*, each step is a dict with keys:
            'ind': list of dicts. Each dict is key-value pair: {'v': x}, where
                   x is a value in an array storing the binary heap.
            'style': string, ignored
            'classes': string, ignored
        """

        # Name, main loop, heapify algorithm.
        # The order of algorithms in this list also describes a descending
        # order of preference when multiple algorithms fit equally well into
        # the student's sequence.
        algo_variants = [
            ('Correct',             (4,3,2,1,0), self.min_heapify),
            ('Wrong-Duplicate',     (4,3,2,1,0), self.wrong_duplicate),
            ('Heapify-with-Father', (4,3,2,1,0), self.heapify_with_father_lr),
            ('Heapify-with-Father', (4,3,2,1,0),
             self.heapify_with_father_lr_recursive),
            ('Heapify-with-Father', (4,3,2,1,0), self.heapify_with_father_rl),
            ('Heapify-with-Father', (4,3,2,1,0),
             self.heapify_with_father_rl_recursive),
            ('Left-to-Right',       (3,4,1,2,0), self.min_heapify),
            ('No-Recursion',        (4,3,2,1,0), self.no_recursion),
            ('Single-Skip',         None, None),
            ('Top-Down',            (0,1,2,3,4), self.min_heapify),
            ('Delayed-Recursion',   None,        None),
            ('Smallest-Instantly-Up', (0,1,2,3,4), self.smallest_instantly_up),
            ('Other',               (0,2,1,4,3), self.smallest_instantly_up),
            ('Maximum-Heap',        (4,3,2,1,0), self.max_heapify),
            ]

        V = len(algo_variants)
        algo_score = [0] * V # index of last matching state
        algo_perfect_match = [False] * V
        algo_swap_count = [0] * V

        # Special cases:
        # Single-Skip: Min-Heapify with one missing state
        # Delayed-Recursion: two variants, specific matching algorithm

        input, states, swaps = self.parse_recording(recording)

        for i in range(len(algo_variants)):
            (name, main_loop, heapify) = algo_variants[i]
            if (name == 'Single-Skip'):
                # Single-Skips produces many candidate sequences. Store the
                # similarity score of the best match.
                algo_sequences = self.single_skips(input)
                max_score = 0
                for s in algo_sequences:
                    score = self.state_similarity(algo_states, states)
                    if score > max_score and not algo_perfect_match[i]:
                        max_score = score
                        algo_score[i] = score
                        algo_perfect_match[i] = (algo_states == states)
                        algo_swap_count[i] = len(s) - 1

            elif (name == 'Delayed-Recursion'):
                dr1_swaps = self.build_min_heap_dr_level(input)
                dr2_swaps = self.build_min_heap_dr_end(input)
                dr1_states = self.states_from_swaps(input, dr1_swaps)
                dr2_states = self.states_from_swaps(input, dr2_swaps)
                score1 = self.state_similarity(dr1_states, states)
                score2 = self.state_similarity(dr2_states, states)
                if score1 > score2:
                    algo_score[i] = score1
                    algo_swap_count[i] = len(dr1_swaps)
                    algo_perfect_match[i] = (dr1_states == states)
                else:
                    algo_score[i] = score2
                    algo_swap_count[i] = len(dr2_swaps)
                    algo_perfect_match[i] = (dr2_states == states)

            else:
                algo_states, algo_swaps = self.build_heap_variant(main_loop,
                    heapify, input)
                algo_score[i] = self.state_similarity(algo_states, states)
                algo_swap_count[i] = len(algo_swaps)
                algo_perfect_match[i] = (algo_states == states)

        self.statistics['total-matched'] += 1


        cross = self.statistics['cross-match']


        # Classify sequence

        # A: 100% correct.
        # B: 100% match with some misconceived candidate.
        # If there are several candidates fulfilling the property, the one
        # with the lowest index is chosen. The 'Correct' variant has the lowest
        # index and the 'Other' variant the highest.
        best_candidates = [i for i in range(len(algo_perfect_match))
                           if algo_perfect_match[i]]
        if (len(best_candidates) > 0):
            if (len(best_candidates) > 1):
                #print("Ambiguous perfect match: {}".format(best_candidates))
                if (best_candidates[0] == 0):
                    self.statistics['misconception-as-correct'] += 1
                else:
                    self.statistics['multiple-misconceptions'] += 1
                self.__record_ambiguous_matches(best_candidates)
            # best_candidates[0] has the lowest index
            return (algo_variants[best_candidates[0]][0], 'Finished')


        # C: No perfect match and the sequence of some misconceived algorithm
        # matches at laest two steps further than the correct algorithm.
        max_score = max(algo_score)
        if (max_score - algo_score[0] >= 2):
            best_candidates = [i for i in range(len(algo_perfect_match))
                if algo_score[i] == max_score]
            if (len(best_candidates) > 1):
                #print("Ambiguous partial match: {}".format(best_candidates))
                self.statistics['multiple-misconceptions'] += 1
                self.__record_ambiguous_matches(best_candidates)
            return (algo_variants[best_candidates[0]][0], 'Unfinished')

        # D: None of the rules apply.
        return ('Unknown', 'Unfinished')

    def __record_ambiguous_matches(self, equal_candidates):

        for i in range(len(equal_candidates)):
            x = equal_candidates[i]
            for j in range(i + 1, len(equal_candidates)):
                y = equal_candidates[j]
                self.statistics['cross-match'][y * 13 + x] += 1

    def print_statistics(self):
        print()
        print("Submission matching statistics")
        print("------------------------------")

        total = self.statistics['total-matched']
        pass_correct = self.statistics['misconception-as-correct']
        multi_misc = self.statistics['multiple-misconceptions']
        cross = self.statistics['cross-match']

        print("Submissions classified:          {}".format(total))
        print("Misconception passes as correct; {}".format(pass_correct))
        print("Incorrect, equal misconceptions: {}".format(multi_misc))
        print("Matrix of cross-matches:")
        for i in range(13):
            print(cross[i * 13 : (i+1) * 13])


    def build_heap_variant(self, main_loop, heapify, input):
        """Runs a build-heap variant.

        Parameters:
        main_loop: list of heap array indices for which a heapify function is
                   called.
        heapify:   a heapify function.
        input:     input array

        Returns:
        (states, swaps): states is a list containing the state of the heap
                         array after each swap.
                         swaps is similar to states but only has the index pair
                         of each swap.
        """
        current_state = copy.copy(input)
        states = [tuple(input)]
        swaps = []
        for i in main_loop:
            heapify(current_state, i, states, swaps)

        return (states, swaps)


    #
    # Matching algorithms
    #

    def state_similarity(self, C, S):
        """Finds furthest matching state of candidate sequence in student's
        sequence.

        According to: Otto Seppälä, Lauri Malmi & Ari Korhonen (2006)
        Observations on student misconceptions—A case study of the Build –
        Heap Algorithm, Computer Science Education, 16:3, 241-255,
        DOI: 10.1080/08993400600913523

        Parameters:
        C (list): candidate sequence produced by an algorithm
        S (list): student's sequence

        Returns: index of last matching state in student's sequence + 1.
        """

        i = 0   # test index in candidate sequence
        j = 0   # test index in student's sequence
        skipped_states = 0
        while i < len(C) and j < len(S):
            #print("i: {} j: {} ".format(i, j))
            # Skip states in student's sequence until a matching state is found
            # or the end of student's sequence is reached.
            k = j
            while k < len(S) and C[i] != S[k]:
                k += 1
            # Count a state in candidate sequence as matched if applicable.
            if k < len(S):
                j = k + 1
            i += 1
        return j

    def state_similarity_dr(self, input, C_swaps, S_swaps, heap_size):
        """Version of state_similarity() to detect delayed recursion where
        recursive swaps are performed after each level of the heap.

        Parameters:
        input:   initial state of the heap array
        C_swaps: candidate swaps of the No-recursion algorithm. This is a list
                 of tuples (a,b,r): a and b are indices of the heap array, and
                 r == True if the swap is recursive, False otherwise.

        S_swaps: student's swaps. List of tuples (a,b) where a and b are indices
                 of the heap array.

        Returns: index in student's sequence.
        """
        i = 0   # test index in candidate sequence
        j = 0   # test index in student's sequence
        C_state = input
        S_state = input
        while i < len(C_swaps) and j < len(S_swaps):
            if C_swaps[i][2] == True:
                # Recursive swap. Count number of adjacent recursive swaps.
                k = i + 1
                while k < len(C_swaps) and C_swaps[k][2] == True:
                    k += 1
                adjacent = k - i
                # Try to match C_swaps[i ... i + adjacent - 1] to
                # S_swaps[j ... j + adjacent - 1].
                matched = [False] * adjacent # which recursive swaps in S_swaps
                                             # are matched
                furthest_matching_i = i - 1
                furthest_matching_j = j - 1
                for k in range(i, i + adjacent):
                    for l in range(j, min(j + adjacent, len(S_swaps))):
                        if (C_swaps[k][0:2] == S_swaps[l][0:2] and
                            matched[l - i] == False):
                            matched[l - i] = True
                            if (k > furthest_matching_i):
                                furthest_matching_i = k
                            if (l > furthest_matching_j):
                                furthest_matching_j = l
                # Go forward in C_swaps and S_swaps according to the last
                # corresponding recursive swaps
                for k in range(i, furthest_matching_i + 1):
                    self.swap(C_state, C_swaps[i])
                for k in range(j, furthest_matching_j + 1):
                    self.swap(S_state, S_swaps[j])
                i = furthest_matching_i + 1
                j = furthest_matching_j + 1

            else:
                # Skip states in student's sequence until a matching state is
                # found or end of student's sequence is reached.
                k = j
                S_state_test = S_state
                while k < len(S_swaps) and C_state != S_state_test:
                    self.swap(S_state_test, S_swaps[k])
                    k += 1
                # Count a state in candidate sequence as matched if applicable.
                if k < len(S_swaps):
                    S_state = S_state_test
                    j = k + 1
                self.swap(C_state, C_swaps[i])
                i += 1
        return j

    def lcs_similarity(self, X, Y):
        """Length of longest common subsequence for sequences X and Y.
        Dynamic programming solution."""
        sim, matches = self.lcs(X, Y)
        return sim

    def lcs(self, X, Y):
        """Longest common subsequence for sequences X and Y.
        Dynamic programming solution.

        Returns:
        (sim, matches): sim is length of longest common subsequence.
                        matches is a list of tuples (a, b): each tuple indicates
                        a matching character; X[a] == Y[b]
        """

        # Adapted from:
        # Cormen, Leiserson, Rivest, Stein: Introduction to Algorithms (3rd ed.).
        # MIT Press 2009. ISBN 9780262270830. Page  394.

        m = len(X)
        n = len(Y)
        c = []
        b = []
        for i in range(m + 1):
            c.append([0] * (n + 1))
            b.append([0] * (n + 1))

        # c[i][j] will hold the length of longest common subsequence for substrings
        # X_i and Y_j: X_i is the first i characters of X, and Y_j is the first j
        # characters of Y.

        # Entries of b[i][j] correspond to entries c[i][j]:
        # b[i][j] = 1, if there are matching characters
        #         = 2, if one index of i was skipped
        #         = 3, if one index of j was skipped

        # Note that the top row and leftmost column are zeroes, as they depict the
        # case where at least one substring is empty. These cases make it easier
        # to compute the first actual results where either i or j is 1.

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if X[i - 1] == Y[j - 1]:
                    # If the characters match, grow the length by one from the
                    # upper-left cell
                    c[i][j] = c[i - 1][j - 1] + 1
                    b[i][j] = 1
                else:
                    # Choose the value of either upper or left cell, which one is
                    # greater.
                    if c[i - 1][j] >= c[i][j - 1]:
                        c[i][j] = c[i - 1][j]
                        b[i][j] = 2
                    else:
                        c[i][j] = c[i][j - 1]
                        b[i][j] = 3

        # Construct sequence of matching indices in X and Y
        matches = []
        i = m
        j = n
        while (i > 0 and j > 0):
            if (b[i][j] == 1):
                matches.append((i - 1, j - 1))
                i -= 1
                j -= 1
            elif (b[i][j] == 2):
                i -= 1
            else:
                j -= 1
        matches.reverse()
        return (c[m][n], matches)

    def states_from_swaps(self, input, swaps):
        """Constructs a sequence of states from sequence of swaps and an input.
        """

        A = copy.copy(input)
        states = [tuple(A)]
        for s in swaps:
            self.swap(A, s)
            states.append(tuple(A))
        return states

    def swaps_from_states(self, S):
        """Constructs a swap sequence from a sequence containing states of heap
        array states."""
        swaps = []
        for i in range(1, len(S)):
            indices = []
            for j in range(len(S[i])):
                if (S[i] != S[i-1]):
                    indices.append(j)
            swaps.append(tuple(indices))

    def swap(self, A, s):
        """Swaps elements at indices s[0] and s[1] in array A."""
        A[s[0]], A[s[1]] = A[s[1]], A[s[0]]


    def lcs_similarity_delayed_recursion(self, C_swaps, S_swaps):
        """Length of longest common subsequence for student's sequence and
        candidate sequence allowing delayed recursion.

        Parameters:
        C_swaps: candidate swaps of the No-recursion algorithm. This is a list
                 of tuples (a,b,r): a and b are indices of the heap array, and
                 r == True if the swap is recursive, False otherwise.

        S_swaps: student's swaps. List of tuples (a,b) where a and b are indices
                 of the heap array.

        """
        # First, compute longest common subsequence for nonrecursive candidate
        # swaps and student's swaps. Create a copy of C_swaps which does not
        # contain recursiveness information and where recursive swaps have been
        # replaced with (-1, -1).
        C_swaps_comparable = [(-1, -1) if s[2] else s[0:2] for s in C_swaps]

        # match_count: number of matching nonrecursive swaps
        # matches: list of tuples (c,s): c is index of swap in C_swaps and s
        #     is corresponding index in S_swaps.
        match_count, matches = self.lcs(C_swaps_comparable, S_swaps)

        # Second, try to match recursive candidate swaps to remaining student's
        # swaps. Construct two auxiliary lists:
        # C_in_S_swaps: index of each C_swap in S_swaps, or -1 if not found.
        # S_swap_matched: indicates which student's swaps have already been
        #                 matched.
        C_in_S_swaps = [-1] * len(C_swaps)
        S_swap_matched = [False] * len(S_swaps)
        for x in matches:
            C_in_S_swaps[x[0]] = x[1]
            S_swap_matched[x[1]] = True

        # Iterate through matches and try to match nonrecursive swaps.

        # Minimum position for a recursive swap in S_swaps. This is updated
        # every time a nonrecursive swap is encountered, as we know a recursive
        # swap at C_swap[i] could be placed at any position after the last
        # preceding *nonrecursive* swap. Initialise min_pos to an unreachable
        # value to skip possible recursive swaps in S_swaps before the first
        # nonrecursive swap.
        min_pos = len(S_swaps) + 1
        for i in range(len(C_swaps)):
            if C_swaps[i][2] == False:
                if C_in_S_swaps[i] > -1:
                    # Matched C_swap, nonrecursive. Update min_pos to the
                    # location of the same swap in S_swaps.
                    min_pos = C_in_S_swaps[i] + 1
            else:
                # Recursive swap in C_swaps. Try to find a corresponding swap
                # in S_swaps beginning from min_pos.
                target_swap = C_swaps[i][0:2]
                for j in range(min_pos, len(S_swaps)):
                    if S_swaps[j] == target_swap:
                        C_in_S_swaps[i] = j
                        match_count += 1
                        break

        # Final check: if matched swaps appear in the same order in C_swaps
        # and S_swaps, this is clearly not a case of delayed recursion.
        is_delayed_recursion = False
        prev_index = -1
        for i in range(len(C_in_S_swaps)):
            v = C_in_S_swaps[i]
            if v > -1:
                if v < prev_index:
                    is_delayed_recursion = True
                    break
                else:
                    prev_index = v

        return match_count if is_delayed_recursion else 0

    def sequence_similarity(self, recorded_swaps, algo_swaps):
        """Matches a sequence of swaps in the exercise recording against
        a sequence of swaps performed by some algorithm variant."""

        recorded_n = len(recorded_swaps) # recorded sequence
        algo_n = len(algo_swaps)         # candidate sequence
        matches = []
        # Iterate over candidate sequence, selecting a single state at a time
        for i in range(algo_n):

            j = 0 # index of swap in the recording
            if len(matches) > 0:
                j = matches[-1][1] # continue from the last match if possible

            # Iterate over the student's states trying to find that very
            # same state
            while j < recorded_swaps: # try to find a matching state
                if algo_swaps[i] == recorded_swaps[j]:
                    matches.append((i, j))
                    break
                j += 1
        return i


    #
    # Heapify algorithm variants
    #

    def min_heapify(self, A, i, states, swaps):
        """Correct min-heapify.

        Parameters:
        A (list of integers): the heap array, will be modified.
        i (integer):          an index in the heap array to begin.
        states (list of tuples): each time a swap is performed, a tuple copy
                                 of A is stored here.
        swaps (list of tuples): each time a swap is performed, a tuple
                                indicating the swap indices is stored here:
                                (i,j), where 0 <= i < j < len(A).
        """
        l = 2 * i + 1
        r = l + 1
        smallest = i
        if l < len(A) and A[l] < A[i]:
            smallest = l
        if r < len(A) and A[r] < A[smallest]:
            smallest = r
        if smallest != i:
            A[i], A[smallest] = A[smallest], A[i]
            swaps.append((i, smallest))
            states.append(tuple(A))
            self.min_heapify(A, smallest, states, swaps)

    def no_recursion(self, A, i, states, swaps):
        """Min-heapify without recursion.

        Parameters:
        A (list of integers): the heap array, will be modified.
        i (integer):          an index in the heap array to begin.
        states (list of tuples): each time a swap is performed, a tuple copy
                                 of A is stored here.
        swaps (list of tuples): each time a swap is performed, a tuple
                                indicating the swap indices is stored here:
                                (i,j), where 0 <= i < j < len(A).
        """
        l = 2 * i + 1
        r = l + 1
        smallest = i
        if l < len(A) and A[l] < A[i]:
            smallest = l
        if r < len(A) and A[r] < A[smallest]:
            smallest = r
        if smallest != i:
            A[i], A[smallest] = A[smallest], A[i]
            swaps.append((i, smallest))
            states.append(tuple(A))

    def delayed_recursion(self, A, i, states, swaps, first_instance = True):
        """Min-heapify for delayed recursion: *recursive* swaps where
        Min-heapify have called itself are marked, but they are in their
        original position.

        Parameters:
        A (list of integers): the heap array, will be modified.
        i (integer):          an index in the heap array to begin.
        states (list of tuples): each time a swap is performed, a tuple copy
                                 of A is stored here.
        swaps (list of tuples): each time a swap is performed, a tuple
                                indicating the swap indices is stored here:
                                (i,j, r), where 0 <= i < j < len(A) and
                                r = True if swap is recursive, False otherwise.
        """
        l = 2 * i + 1
        r = l + 1
        smallest = i
        if l < len(A) and A[l] < A[i]:
            smallest = l
        if r < len(A) and A[r] < A[smallest]:
            smallest = r
        if smallest != i:
            A[i], A[smallest] = A[smallest], A[i]
            swaps.append((i, smallest, not first_instance))
            states.append(tuple(A))
            self.delayed_recursion(A, smallest, states, swaps, False)

    def build_min_heap_dr_level(self, input, show_recursivity = False):
        """Build-min-heap for delayed recursion: *recursive* swaps where
        Min-heapify have called itself are marked. The recursive swaps are
        performed after a whole level in the binary tree representation has
        been traversed.

        Parameters:
        input (list of integers): the heap array
        show_recursivity: if True, returns for each swap extra information
                          whether the swap was recursive.

        Returns:
        swaps (list of tuples): each time a swap is performed, a tuple
                                indicating the swap indices is stored here.

            If show_recursivity == True: swaps are tuples (i,j, r), where
            0 <= i < j < len(A) and r = True if swap is recursive, False
            otherwise. If show_recursivity == False, swaps are tuples (i,j).
        """

        A = copy.copy(input)
        if self.assumed_heap_size != len(A):
            self.compute_level_indices(len(A))

        final_swaps = []
        recursive_swap_queue = []
        j = len(self.heap_levels) - 2 # The lowermost level only has leaves.

        # Main loop of Build-heap (correct descending index version)
        for i in range(len(A) // 2 - 1, -1, -1):
            # Run min-heapify for index i
            tmp_states = []
            tmp_swaps = []
            self.delayed_recursion(A, i, tmp_states, tmp_swaps)

            # Filter recursive swaps of Min-heapify into queue.
            for s in tmp_swaps:
                if s[2] == True: # Recursive swap
                    recursive_swap_queue.append(s)
                else:
                    final_swaps.append(s)

            # If the leftmost node in the current level of the tree has been
            # reached, flush queue of recursive swaps into final result.
            if (i == self.heap_levels[j][0]):

                final_swaps += recursive_swap_queue
                recursive_swap_queue = []
                j -= 1

        if show_recursivity:
            return final_swaps
        else:
            return [s[0:2] for s in final_swaps]


    def build_min_heap_dr_end(self, input, show_recursivity = False):
        """Build-min-heap for delayed recursion: *recursive* swaps where
        Min-heapify have called itself are marked. The recursive swaps are
        performed in the end.

        Parameters:
        A (list of integers): the heap array
        show_recursivity: if True, returns for each swap extra information
                  whether the swap was recursive.

        Returns:
        swaps (list of tuples): each time a swap is performed, a tuple
                                indicating the swap indices is stored here.

            If show_recursivity == True: swaps are tuples (i,j, r), where
            0 <= i < j < len(A) and r = True if swap is recursive, False
            otherwise. If show_recursivity == False, swaps are tuples (i,j).
        """

        A = copy.copy(input)
        nonrecursive_swaps = []
        recursive_swap_queue = []

        # Main loop of Build-heap (correct descending index version)
        for i in range(len(A) // 2 - 1, -1, -1):
            # Run min-heapify for index i
            tmp_states = []
            tmp_swaps = []
            self.delayed_recursion(A, i, tmp_states, tmp_swaps)

            # Filter recursive swaps of Min-heapify into queue.
            for s in tmp_swaps:
                if s[2] == True: # Recursive swap
                    recursive_swap_queue.append(s)
                else:
                    nonrecursive_swaps.append(s)

        final_swaps = nonrecursive_swaps + recursive_swap_queue
        if show_recursivity:
            return final_swaps
        else:
            return [s[0:2] for s in final_swaps]


    def single_skips(self, input):
        """Single-skips algorithm variants.

        Parameters:
        input: initial state of the heap array

        Returns:
        a list where each element is a candidate sequence (sequence of states)
        """

        A = copy.copy(input) # heap array
        states = []
        swaps = []

        # Run correct variant where recursive and nonrecursive swaps are
        # identified.
        for i in range(4, -1, -1):
            self.delayed_recursion(A, i, states, swaps)

        # Generate systematically variants where one swap is omitted.

        all_sequences = []
        for i in range(len(swaps)):  # i is the omitted swap
            A = copy.copy(input)
            j = 0
            sequence = [tuple(input)]
            while (j < len(swaps)): # iterate through all swaps
                if (i != j):
                    self.swap(A, swaps[j])
                    sequence.append(tuple(A))
                    j += 1
                else:
                    j += 1 # skip current swap
                    # terminate recursion
                    while (j < len(swaps) and swaps[j][2] == True):
                        j += 1
            all_sequences.append(sequence)

        return all_sequences



    def heapify_with_father_lr(self, A, i, states, swaps):
        """Min-heapify: heapify-with-father, left child first"""
        l = 2 * i + 1
        r = l + 1

        if l < len(A) and A[l] < A[i]:
            A[i], A[l] = A[l], A[i]
            swaps.append((i, l))
            states.append(tuple(A))

        if r < len(A) and A[r] < A[i]:
            A[i], A[r] = A[r], A[i]
            swaps.append((i, r))
            states.append(tuple(A))

    def heapify_with_father_lr_recursive(self, A, i, states, swaps):
        """Min-heapify: heapify-with-father, right child first, recursive"""
        l = 2 * i + 1
        r = l + 1

        if l < len(A) and A[l] < A[i]:
            A[i], A[l] = A[l], A[i]
            swaps.append((i, l))
            states.append(tuple(A))
            self.heapify_with_father_lr_recursive(A, l, states, swaps)

        if r < len(A) and A[r] < A[i]:
            A[i], A[r] = A[r], A[i]
            swaps.append((i, r))
            states.append(tuple(A))
            self.heapify_with_father_lr_recursive(A, r, states, swaps)

    def heapify_with_father_rl(self, A, i, states, swaps):
        """Min-heapify: heapify-with-father, right child first"""
        l = 2 * i + 1
        r = l + 1
        if r < len(A) and A[r] < A[i]:
            A[i], A[r] = A[r], A[i]
            swaps.append((i, r))
            states.append(tuple(A))

        if l < len(A) and A[l] < A[i]:
            A[i], A[l] = A[l], A[i]
            swaps.append((i, l))
            states.append(tuple(A))

    def heapify_with_father_rl_recursive(self, A, i, states, swaps):
        """Min-heapify: heapify-with-father, right child first, recursive"""
        l = 2 * i + 1
        r = l + 1
        if r < len(A) and A[r] < A[i]:
            A[i], A[r] = A[r], A[i]
            swaps.append((i, r))
            states.append(tuple(A))
            self.heapify_with_father_rl_recursive(A, r, states, swaps)

        if l < len(A) and A[l] < A[i]:
            A[i], A[l] = A[l], A[i]
            swaps.append((i, l))
            states.append(tuple(A))
            self.heapify_with_father_rl_recursive(A, l, states, swaps)


    def heapify_up(self, A, i, states, swaps):
        """Min-heapify: swap upwards towards root"""
        if (i < 0):
            return
        l = 2 * i + 1
        r = l + 1
        smallest = i
        if l < len(A) and A[l] < A[i]:
            smallest = l
        if r < len(A) and A[r] < A[smallest]:
            smallest = r
        if smallest != i:
            A[i], A[smallest] = A[smallest], A[i]
            swaps.append((i, smallest))
            states.append(tuple(A))
            self.heapify_up(A, (i - 1) // 2, states, swaps)

    def max_heapify(self, A, i, states, swaps):
        """Max-heapify"""
        l = 2 * i + 1
        r = l + 1
        greatest = i
        if l < len(A) and A[l] > A[i]:
            greatest = l
        if r < len(A) and A[r] > A[greatest]:
            greatest = r
        if greatest != i:
            A[i], A[greatest] = A[greatest], A[i]
            swaps.append((i, greatest))
            states.append(tuple(A))
            self.max_heapify(A, greatest, states, swaps)

    def wrong_duplicate(self, A, i, states, swaps):
        """Min-heapify: if both children are equal and father is greater than
        them, swap the right child with the father"""
        l = 2 * i + 1
        r = l + 1
        smallest = i
        if l < len(A) and A[l] < A[i]:
            smallest = l
        if r < len(A) and A[r] <= A[smallest]:
            smallest = r

        if smallest != i:
            A[i], A[smallest] = A[smallest], A[i]
            swaps.append((i, smallest))
            states.append(tuple(A))
            self.wrong_duplicate(A, smallest, states, swaps)


    def path_bubblesort(self, A, i, states, swaps):
        """Min-heapify: create a path from the smallest child of i to root.
        Then execute Bubblesort on the path."""

        path_indices = []

        l = 2 * i + 1
        r = l + 1
        smallest = i
        if l < len(A) and A[l] < A[i]:
            smallest = l
        if r < len(A) and A[r] < A[smallest]:
            smallest = r

        if (smallest != i):
            path_indices.append(smallest)

        path_indices.append(i)
        j = i
        while (j > 0):
            j = (j - 1) // 2
            path_indices.append(j)

        l = len(path_indices)
        for i in range(l - 1):
            for j in range(0, l - 1 - i):
                index1 = path_indices[j]
                index2 = path_indices[j + 1]
                if (A[index1] < A[index2]):
                    A[index1], A[index2] = A[index2], A[index1]
                    swaps.append((index2, index1))
                    states.append(tuple(A))

    def smallest_instantly_up(self, A, i, states, swaps):
        """Smallest-instantly-up: the tree is traversed in level order,
        swapping the traversed key with the smallest key found in the subtree
        rooted at the node being traversed."""

        # This heapify variant might work only with the Top-down (the same as
        # levelorder) loop variant.
        min_value = max(A) + 1
        min_index = -1
        (min_value, j) = self.subtree_min_index(A, i, min_value, min_index)
        if (i != j):
            A[i], A[j] = A[j], A[i]
            swaps.append((i, j))
            states.append(tuple(A))

    def subtree_min_index(self, A, i, min_value, min_index):
        """Searches for the minimum value in the subtree rooted at node
        with index i. Returns the index of the minimum value."""
        if (i >= len(A)):
            return (min_value, min_index)

        # Traverse in preorder
        if (A[i] < min_value):
            min_value = A[i]
            min_index = i
        (min_value, min_index) = self.subtree_min_index(A, 2 * i + 1,
            min_value, min_index)
        (min_value, min_index) = self.subtree_min_index(A, 2 * i + 2,
            min_value, min_index)

        return (min_value, min_index)

    #
    # Special features in student's sequence, not actual misconceived algorithms
    #

    def min_heap_property(self, A, i):
        """Tests whether min-heap property holds for heap array A beginning
        from index i.

        Returns:
            True or False
        """
        l = 2 * i + 1
        r = 2 * i + 2
        t = True
        if l < len(A):
            if A[i] > A[l]:
                return False
            else:
                t &= self.min_heap_property(A, l)
        if r < len(A):
            if A[i] > A[r]:
                return False
            else:
                t &= self.min_heap_property(A, r)
        return t

    def correct_with_extra_steps(self, student_states, correct_states):
        """Tests whether the student's solution is the correct solution with
        extra steps at the end."""
        s = len(student_states)
        c = len(correct_states)
        return (s > c) and (student_states[0:c] == correct_states[0:c])

    def swaps_resemble_build_heap(self, swaps, heap_size):
        if len(swaps) < 2:
            return False

        swap_i = 0
        main_loop_i = heap_size // 2 # maximum initial value + 1

        # index of previous child in chain of consecutive heapify swaps
        previous_child = -1
        for swap in swaps:
            parent, child = swap
            if (child - 1) // 2 != parent:
                # invalid swap
                return False
            if previous_child != parent:
                # Heapify chain does not continue from previous swap. This
                # should mean that the index in the main loop has decreased.
                if parent >= main_loop_i:
                    return False
                main_loop_i = parent
            # Heapify continues
            previous_child = child

        return True

    def swaps_are_legal(self, states, swaps, heap_size):
        """Examines each swap independently. The swap is 'legal' if
        (a) they are a parent-child pair by their indices, and
        (b) the swap is necessary (parent is less than its children), and
        (c) lesser child is swapped with parent, and
        (d) if children are equal, the left one is chosen.

        Returns: True or False: all swaps fulfill the 'legal swap' property.
        """
        for i in range(len(swaps)):
            parent_index, child_index = swaps[i]

            # Is first *index* of the swap the parent of the second index?
            if (child_index - 1) // 2 != parent_index:
                # invalid swap: not parent-child swap
                return False

            # Compare *values* of parent and its children. Is the minimum
            # of them swapped upwards, if necessary?
            l = 2 * parent_index + 1
            r = 2 * parent_index + 2
            min_index = parent_index
            if l < heap_size and states[i][l] < states[i][parent_index]:
                min_index = l
            if r < heap_size and states[i][r] < states[i][min_index]:
                min_index = r
            if min_index != child_index:
                return False

        return True

    def swaps_are_legal_by_index(self, swaps, heap_size):
        """Examines each swap independently. The swap is 'legal by index' if
        they are a parent-child pair by their indices.

        Returns: True or False: all swaps fulfill the 'legal by index'
                 property.
        """
        for i in range(len(swaps)):
            parent_index, child_index = swaps[i]

            # Is first *index* of the swap the parent of the second index?
            if (child_index - 1) // 2 != parent_index:
                # invalid swap: not parent-child swap
                return False

        return True


# Generates Build-heap / Heapify main loop variants
class MainLoopGenerator:
    
    def __init__(self):
        # heap levels: list of tuples (l, r) where l is the first
        # index and r is the last index of a heap element on one
        # level of the binary tree representation.
        # Example: [(0, 0), (1, 2), (3, 6), (7, 14), ...]
        self.levels = []
        
        # heap size for which self.levels is computed
        self.heap_size = 0
        
        # highest index of a node which has children
        self.last_i = 0                 
        
        
    def generate_levels(self, N):
        """Generates start and end indices of each level.
        
        Parameters:
        N    new heap size
        """
        
        self.levels = []
        if (N < 1):
            self.heap_size = 0
        else:
            self.heap_size = N        

        self.last_i = self.heap_size // 2 - 1
                
        level_width = 1
        l = 0
        while (l <= self.last_i):        
            r = min(self.last_i, l + level_width - 1)        
            self.levels.append((l, r))
            l = r + 1
            level_width *= 2

    def correct(self):        
        return [i for i in range(self.last_i, -1, -1)]
    
    def down_lr(self):
        return [i for i in range(self.last_i + 1)]
    
    
        
if __name__ == "__main__":
    m = BuildHeapMatcher()

    #              14                      14                      14
    #        ┌──────┴───┐            ┌──────┴───┐            ┌──────┴───┐
    #       17         13           17        (13)          (17)       11
    #    ┌───┴────┐   ┌─┴─┐      ┌───┴────┐   ┌─┴─┐      ┌───┴────┐   ┌─┴─┐
    #   15      (16) 12  11     15       10  12 (11)    15      (10) 12  13
    #  ┌─┴─┐   ┌──┘            ┌─┴─┐   ┌──┘            ┌─┴─┐   ┌──┘
    # 19  18 (10)             19  18  16              19  18  16
    #             (14)                     10
    #        ┌──────┴───┐            ┌──────┴───┐
    #      (10)        11           14         11
    #    ┌───┴────┐   ┌─┴─┐      ┌───┴────┐   ┌─┴─┐
    #   15       17  12  13     15       17  12  13
    #  ┌─┴─┐   ┌──┘            ┌─┴─┐   ┌──┘
    # 19  18  16              19  18  16

    states = [(14, 17, 13, 15, 16, 12, 11, 19, 18, 10),
              (14, 17, 13, 15, 10, 12, 11, 19, 18, 16),
              (14, 17, 11, 15, 10, 12, 13, 19, 18, 16),
              (14, 10, 11, 15, 17, 12, 13, 19, 18, 16),
              (10, 14, 11, 15, 17, 12, 13, 19, 18, 16)]
    swaps = [(4, 9), (2, 6), (1, 4), (0, 1)]
    #m.print_heap_sequence(states, swaps)
    #m.print_array_sequence(states, swaps)
