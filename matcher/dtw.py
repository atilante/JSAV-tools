import array

def dtw(X, Y, d, return_array=False):
    """Dynamic time warping (DTW) similarity of X and Y.
    
    Parameters:
    X: first sequence
    Y: second sequence
    d: function (x,y) -> zero or positive Real value; distance between
       x and y, where x is member of X and y is member of Y
    
    Returns:
    0 if X == Y
    positive value otherwise. The lower the value, the more similar X and Y
    are.
    
    Reference:
    Hiroaki Sakoe and Seibi Chiba. Dynamic Programming Algorithm
    Optimizatino for Spoken Word Recognition. IEEE transactions on 
    acoustics, speech, and signal processing, vol. ASSP-26, no. 1,
    February 1978, pages 43-49. DOI 10.1109/TASSP.1978.1163055.
    """
    M = len(X)
    N = len(Y)
    
    if M == 0 or N == 0:
        return 0
    
    # Cost array g:
    #
    #              i
    #         0 1 2 ... M
    #         -----------
    #      0 |
    #      1 |
    #   j  2 |
    #     ...|
    #      N |
    #
    # Array g is logically two-dimensional: G[i][j], where 0 <= i < M
    # and 0 <= j < N. This is mapped to one-dimensional array:
    # g[k] = j * M + i
    g = array.array('f', [0] * M * N)
    
    # Initial cell
    g[0] = 2 * d(X[0], Y[0])
    
    # top row: j = 0 (all samples of X against Y[0])
    for i in range(1, M):
        g[i] = g[i - 1] + d(X[i], Y[0])
    
    # leftmost column: i = 0 (all samples of Y against X[0])
    for j in range(1, N):
        g[j * M] = g[(j - 1) * M] + d(X[0], Y[j])
    
    # Cells 1 <= i < M and 1 <= j < N
    for j in range(1, N):
        for i in range(1, M):
            d_ = d(X[i], Y[j])
            v1 = g[(j - 1) * M + i] + d_
            v2 = g[(j - 1) * M + i - 1] + 2 * d_
            v3 = g[j * M + i - 1] + d_
            g[j * M + i] = min(v1, v2, v3)
          
    if (return_array):
        return g
    else:
        return g[M * N - 1]

    