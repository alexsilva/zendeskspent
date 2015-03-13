__author__ = 'alex'


def float_number(value):
    converted = 0
    if isinstance(value, basestring):
        try:
            converted = float(value.replace(',', '.'))
        except ValueError:
            if value:
                raise
        except TypeError:
            converted = 0
    return converted