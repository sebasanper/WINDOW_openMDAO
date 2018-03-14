from math import sqrt


def root_sum_square(array_deficits):
    #  This is one model, root sum square of individual wind speed deficits.
    total_deficit = sqrt(sum([deficit ** 2.0 for deficit in array_deficits]))
    return total_deficit


def multiplied(array_deficits):
    total_deficit = 1.0
    for element in array_deficits:
        total_deficit *= element
    return total_deficit


def summed(array_deficits):
    total_deficit = sum(array_deficits)
    if total_deficit > 1.0:
        total_deficit = 1.0
    return total_deficit


def maximum(array_deficits):
    return max(array_deficits)

if __name__ == '__main__':
    deficits = [0.3, 0.4]
    # print root_sum_square(deficits)
    # print multiplied(deficits)
    # print summed(deficits)
    # print maximum(deficits)
