def add_tuples(tuple1: tuple, tuple2: tuple):
    """
    Add two tuples component-wise

    :param tuple1: summand
    :param tuple2: summand

    :return: sum
    """

    if len(tuple1) is not len(tuple2):
        return None  # this type of addition is not defined for tuples with different lengths
    # calculate sum
    sum_of_two = []
    for i in range(len(tuple1)):
        sum_of_two.append(tuple1[i] + tuple2[i])
    return tuple(sum_of_two)


def linear_dim(undimmed: tuple, factor: float) -> tuple:
    """
    Multiply all components of undimmed with factor

    :param undimmed: the vector
    :param factor: the factor to multiply the components of the vector byy

    :return: resulting RGB color vector
    """
    dimmed = ()
    for i in undimmed:
        i *= factor
        dimmed += i,  # merge tuples
    return dimmed


def wheel(wheel_pos: float):
    """
    Get a color from a color wheel: Green -> Red -> Blue -> Green

    :param wheel_pos: numeric from 0 to 254

    :return: RGB color tuple
    """

    if wheel_pos > 254:
        wheel_pos = 254  # Safeguard
    if wheel_pos < 85:  # Green -> Red
        color = (wheel_pos * 3, 255 - wheel_pos * 3, 0)
    elif wheel_pos < 170:  # Red -> Blue
        wheel_pos -= 85
        color = (255 - wheel_pos * 3, 0, wheel_pos * 3)
    else:  # Blue -> Green
        wheel_pos -= 170
        color = (0, wheel_pos * 3, 255 - wheel_pos * 3)

    return color

