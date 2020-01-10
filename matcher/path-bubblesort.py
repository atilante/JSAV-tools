def path_bubblesort(A, i):
    """Min-heapify: execute Bubblesort on the path from current node to
    root."""

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

    print("path_indices: {}".format(path_indices))

    l = len(path_indices)
    for i in range(l - 1):
        for j in range(0, l - 1 - i):
            index1 = path_indices[j]
            index2 = path_indices[j + 1]
            if (A[index1] < A[index2]):
                A[index1], A[index2] = A[index2], A[index1]
                print("{} {}: swapped. {}".format(index1, index2, A))
            else:
                print("{} {}: no swap".format(index1, index2))

A = [47, 95, 41, 65, 36, 87, 24, 60, 11, 32]

path_bubblesort(A, 4)
path_bubblesort(A, 3)
path_bubblesort(A, 2)
path_bubblesort(A, 1)
path_bubblesort(A, 0)
