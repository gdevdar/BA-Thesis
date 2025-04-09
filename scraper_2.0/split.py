def split(a, n):
    """
    :param a: List to split into smaller lists
    :param n: Number of parts to split the list
    :return: returns smaller lists of the original list
    """
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))