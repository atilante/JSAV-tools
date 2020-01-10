# Prints binary tree representations of build-heap swap sequences

class BuildHeapPrinter:
    
    def print_heap_sequence_old(self, states):
        """Prints a UTF-8 encoded text visualisations a binary heap with 10
        elements.

        Parameters:
        states: a list of lists, each sublist has exactly 10 elements.

        Example:
                          12                [12 25 45 43 40 60 80 77 68 50]
                  ┌────────┴────────┐         0  1  2  3  4  5  6  7  8  9
                 25                45
            ┌─────┴─────┐        ┌──┴──┐
           43          40       60    80
         ┌──┴──┐     ┌──┘
        77    68    50

        """

        print("{} states:".format(len(states)))

        for A in states:
            s = ("                  {0:2}                " +
                 "[{0:2} {1:2} {2:2} {3:2} {4:2} {5:2} {6:2} {7:2} {8:2} {9:2}]\n"
                 "          ┌────────┴────────┐" +
                 "         0  1  2  3  4  5  6  7  8  9\n"
                 "         {1:2}                {2:2}\n" +
                 "    ┌─────┴─────┐        ┌──┴──┐\n" +
                 "   {3:2}          {4:2}       {5:2}    {6:2}\n" +
                 " ┌──┴──┐     ┌──┘\n" +
                 "{7:2}    {8:2}    {9:2}\n").format(
                A[0], A[1], A[2], A[3], A[4], A[5], A[6], A[7], A[8], A[9])
            print(s)

    def print_heap_sequence(self, states, swaps):

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

        state_pics = []
        for i in range(len(states)):
            state = states[i]
            e = []
            if (i < len(swaps)):
                swap = swaps[i]
                for j in range(len(state)):
                    if (j in swap):
                        e.append("({0:2})".format(state[j]))
                    else:
                        e.append(" {0:2} ".format(state[j]))


            else:
                e = [" {0:2} ".format(x) for x in state]


            rows = [
                "             {}      ".format(e[0]),
                "        ┌──────┴───┐   ",
                "      {}       {}  ".format(e[1], e[2]),
                "    ┌───┴────┐   ┌─┴─┐ ",
                "  {}     {}{}{}".format(e[3], e[4], e[5], e[6]),
                "  ┌─┴─┐   ┌──┘         ",
                "{}{}{}           ".format(e[7], e[8], e[9])]
            state_pics.append(rows)

        rows = [''] * 7
        for i in range(len(states)):
            end_char = "  "
            if (i % 3 == 2):
                end_char = ''
            for j in range(7):
                rows[j] += state_pics[i][j] + end_char
            if (i % 3 == 2):
                for r in rows:
                    print(r)
                print()
                rows = [''] * 7
        if (i % 3 != 2):
            for r in rows:
                print(r)

    def print_array_sequence(self, states, swaps):
        print("   0   1   2   3   4   5   6   7   8   9")
        for i in range(len(states)):
            state = states[i]
            e = []
            if (i < len(swaps)):
                swap = swaps[i]
                for j in range(len(state)):
                    if (j in swap):
                        e.append("({0:2})".format(state[j]))
                    else:
                        e.append(" {0:2} ".format(state[j]))


            else:
                e = [" {0:2} ".format(x) for x in state]
            row = '['
            for x in e:
                row += x
            row += ']'
            print(row)