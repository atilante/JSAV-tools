import copy
import math
from dtw import dtw

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

        self.heap_array_size = 10

        # List of heapify algorithms. These are used together with loop
        # variants.
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
            (10, 'Path-Bubblesort', self.path_bubblesort)
        )
        
        

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
                    elif options['similarity'] == 'dtw1':
                        m = self.dtw_similarity(algo_swaps, swaps, 1)
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

    def state_similarity(self, S_c, S_s):
        """Length of longest common subsequence for S1 and S2 by greedy approach.

        Parameters:
        S_c (list): candidate sequence produced by an algorithm
        S_s (list): student's sequence
        """

        i = 0   # index in candidate sequence; number of matched states
        j = 0   # index in student's sequence
        while i < len(S_c) and j < len(S_s):
            #print("i: {} j: {} ".format(i, j))
            # Skip states in student's sequence until a matching state is found
            # or end of student's sequence is reached.
            while j < len(S_s) and S_c[i] != S_s[j]:
                j += 1
            # Count a state in candidate sequence as matched if applicable.
            if j < len(S_s):
                i += 1
        return i

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
    
    def dtw_similarity(self, recorded_swaps, algo_swaps, distance_func_code):
        """Matches a sequence of swaps in the exercise recording against
        a sequence of swaps performed by some algorithm variant
        using Dynamic Time Warping"""
        
        # Upper bound for DTW value:
        # Denote size of heap array by N. When comparing two swaps, they are
        # pair of pair of integers: (s, t), (u, v) such that
        # 0 <= s, t, u, v < N. If the distance function is
        # sqrt((s-u)**2 + (t-v)**2), then its maximum value is less than
        # sqrt(N**2 + N**2) = N*sqrt(2) <= 2 * N.
        # Multiply this by the length of the longer sequence and you have an
        # upper bound. 
        
        longest_sequence = 100 # arbitrary large value
        upper_bound = 2 * self.heap_array_size * longest_sequence
        
        def d1(u, v):
            # u and v are swaps
            return math.sqrt( (u[0] - v[0]) ** 2 + (u[1] - v[1]) ** 2)
        
        if (distance_func_code == 1):
            return upper_bound - dtw(recorded_swaps, algo_swaps, d1)
    
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
        """Min-heapify with delayed recursion: recursive swaps where
        Min-heapify have called itself can be delayed.
        
                
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
    m.print_array_sequence(states, swaps)
