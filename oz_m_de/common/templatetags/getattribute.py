import re

from django import template

numeric_test = re.compile("^\d+$")
register = template.Library()


def getattribute(value, arg):
    """Gets an attribute of an object dynamically
    AND recursively from a string name"""
    if "__" in str(arg):
        firstarg = str(arg).split("__")[0]
        value = getattribute(value, firstarg)
        arg = "__".join(str(arg).split("__")[1:])
        return getattribute(value, arg)
    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key') and value.has_key(arg):
        return value[arg]
    elif numeric_test.match(str(arg)) and len(value) > int(arg):
        return value[int(arg)]
    else:
        # return settings.TEMPLATE_STRING_IF_INVALID
        return 'no attr.' + str(arg) + 'for:' + str(value)


register.filter('getattribute', getattribute)
