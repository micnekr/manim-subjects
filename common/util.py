from functools import reduce
# From here https://stackoverflow.com/questions/21418764/flatmap-or-bind-in-python-3
def flatMap(array: List[List]):
    return reduce(list.__add__, array)