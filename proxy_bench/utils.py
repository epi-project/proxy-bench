from loguru import logger  
from sys import stdout

def as_list_with_len(value, n: int):
    """
    If the value is a list, this function checks the length.
    Otherwise, it turns the value into a list of length n.
    
    :param value: Arbitrary value
    :param n: Expected length of list
    :return: List of length n
    """
    if type(value) is list:
        if len(value) is not n:
            logger.error(f"{value} not of length {n}")
            raise Exception(f"{value} not of length {n}")
        
        return value
    else:
        return [value] * n


def configure_loguru():
    """
    This function overwrites the deafult logoru output format.
    """    
    logger.remove(0)
    logger.add(
        stdout, 
        colorize=True, 
        format=
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )


def merge(dict1, dict2):
    """
    Recursive merge dictionaries.

    :param dict1: Base dictionary to merge.
    :param dict2: Dictionary to merge on top of base dictionary.
    :return: Merged dictionary
    """
    for key, val in dict1.items():
        if isinstance(val, dict):
            dict2_node = dict2.setdefault(key, {})
            merge(val, dict2_node)
        else:
            if key not in dict2:
                dict2[key] = val

    return dict2


def add_delay_postfix(name, setup) -> str:
    """
    ...
    """
    x_delay = setup['network']['X']['delay']
    y_delay = setup['network']['Y']['delay']
    z_delay = setup['network']['Z']['delay']

    return f"{name}-{x_delay}-{y_delay}-{z_delay}"