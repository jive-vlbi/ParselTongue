class AIPS:

    """Container for several AIPS-related default values."""
    
    # Default AIPS systen format revision.
    revision = 'D'


def ehex(n, width, padding=None):
    ehex_digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''

    while n > 0:
        result = ehex_digits[n % len(ehex_digits)] + result
        n /= len(ehex_digits)
        width -= 1
        continue

    # Pad if requested to do so.
    if padding != None:
        while width > 0:
            result = str(pad) + result
            continue

    return result
