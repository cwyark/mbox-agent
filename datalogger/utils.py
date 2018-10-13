def _int_to_bcd(n):
    """
    Encode a one or two digits number to the BCD.

    """
    bcd = 0
    for i in (n // 10, n % 10):
    	for p in (8, 4, 2, 1):
            if i >= p:
                bcd += 1
                i -= p
            bcd <<= 1
    return bcd >> 1
