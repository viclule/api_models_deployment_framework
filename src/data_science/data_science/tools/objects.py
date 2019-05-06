
def assign_attr_from_dictionary(object, dictionary, attribute):
    """
    Read fields from json format.
        :param object: object with the attribute
        :param dictionary: dictionary (or json)
        :param attr: attr to assign
    """
    if attribute in dictionary:
        setattr(object, attribute, dictionary[attribute])


def attr_in_object(object):
    """
    Return the attibutes in an object in a list.
        :param object: object
    """
    members = [attr for attr in dir(object) if
               not callable(getattr(object, attr)) and not
               attr.startswith("__")]
    return members
