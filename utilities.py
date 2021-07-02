# Shared functions.

def get_value(d, k, chars, fn=None):
    """
    Gets a value from a dict, given key. d may be None, k may not be present, chars need to be removed,
    and we have fn to remove anything else, like, the word "Acres"

    :param d: A dict
    :param k: The key
    :param chars: Chars to remove
    :param fn: A function to process the data
    :return: the value as an int, if parseable, else 0
    """
    if not d or k not in d:
        return 0
    value = d[k]
    for c in chars:
        value = value.replace(c, "")            # Can remove commas, percents signs, etc.
    v2 = value.strip()
    if not v2:
        return 0

    v3 = fn(v2) if fn is not None else v2   # Can remove words like "acres"
    v4 = v3.strip()
    if not v4:
        return 0

    v5 = int(v4)
    return v5

