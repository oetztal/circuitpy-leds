# TODO: part of this code has been copied from https://github.com/Yottabits/102shows, this needs to be declared properly

def grayscale_correction(lightness: float, max_in: float = 255.0, max_out: int = 255):
    """\
    Corrects the non-linear human perception of the led brightness according to the CIE 1931 standard.
    This is commonly mistaken for gamma correction. [#gamma-vs-lightness]_

    .. admonition::  CIE 1931 Lightness correction [#cie1931-source]_

        The human perception of brightness is not linear to the duty cycle of an LED.
        The relation between the (perceived) lightness :math:`Y`
        and the (technical) lightness :math:`L^*` was described by the CIE:

        .. math::
            :nowrap:

            \\begin{align}
                Y & = Y_{max} \cdot g( ( L^* + 16) /  116 ) \\quad ,& \\quad 0 \\le L^* \\le 100 \\\\

                \\text{with} \\quad g(t) & =
                \\begin{cases}
                    3 \cdot \\delta^2 \cdot ( t - \\frac{4}{29}) & t \\le \\delta  \\\\
                    t^3                                          & t   >  \\delta
                \\end{cases}
                \\quad ,& \\quad \\delta = \\frac{6}{29}
            \\end{align}

        For more efficient computation, these two formulas can be simplified to:

        .. math::

            Y =
            \\begin{cases}
                L^* / 902.33           & L^* \le 8 \\\\
                ((L^* + 16) / 116)^3   & L^*  >  8
            \\end{cases} \\\\
            \\\\
            0 \\le Y \\le 1 \\qquad 0 \\le L^* \\le 100

    .. [#gamma-vs-lightness] For more information, read here: https://goo.gl/9Ji129
    .. [#cie1931-source] formula from
        `Wikipedia <https://en.wikipedia.org/wiki/Lab_color_space#Reverse_transformation>`_

    :param lightness: linear brightness value between 0 and max_in
    :param max_in: maximum value for lightness
    :param max_out: maximum output integer value (255 for 8-bit LED drivers)

    :return: the correct PWM duty cycle for humans to see the desired lightness as integer
    """

    # safeguard and shortcut
    if lightness <= 0:
        return 0
    elif lightness >= max_in:
        return max_out

    # apply the formula from aboce
    l_star = lightness / max_in * 100  # map from 0..max_in to 0..100

    if l_star <= 8:
        duty_cycle = l_star / 902.33
    else:
        duty_cycle = ((l_star + 16) / 116) ** 3

    return round(duty_cycle * max_out)  # this will be an integer!


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


def validate_color(color: list[int] | tuple) -> tuple:
    if isinstance(color, list):
        color = tuple(color)
    if len(color) != 3:
        raise ValueError("Color must contain three values")
    return color
