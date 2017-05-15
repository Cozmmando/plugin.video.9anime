import re
import math

# the + in the beginning parses text to a number
# a [] converts everything before into text -> therefore everythin before *10 or *100 or *1000
# '(+((!+[]+!![]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(+!![]+[])+(!+[]+!![]+[])))>>(!+[]+!![]+!![]+!![]+!![]+!![]+!![])'
# '(+((1+1+1+1+1+10)+(1+1+1+1+1+1+1+1+10)+(+10)+(1+10)))>>(1+1+1+1+1+1+1)'
# 0 is a marker for times 10 or more
# expands to
# '(+((1+1+1+1+1+1)*1000+(1+1+1+1+1+1+1+1+1)*100+(+1)*10+(1+1)*1))>>(1+1+1+1+1+1+1)'

class TokenDecoder:
    #_parentheses_group_regex = r"(\(\d+\))"
    _outer_parentheses_group_regex = r"\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)"
    _lines_regex_template = r"{}\(([^\,a]+)\)"

    def __init__(self):
        pass

    @classmethod
    def decode_token(cls, token):
        lines = cls._get_lines_to_decode(token)
        chars = map(lambda x: cls._decode_as_char(x), lines)
        result = ''.join(chars)
        return result

    @classmethod
    def _get_lines_to_decode(cls, text):
        function_name = cls._find_function_name(text)
        lines_regex = cls._lines_regex_template.format(function_name)
        matches = list(re.findall(lines_regex, text))
        return matches

    @classmethod
    def _decode_as_int(cls, text):
        return cls._get_token_number(text)

    @classmethod
    def _decode_as_char(cls, text):
        num = cls._decode_as_int(text)
        return chr(num)

    @classmethod
    def _get_token_number(cls, text):
        # !![] should be +!![] but im using the extra + so all 1 get accumulated
        # will result in (1+1+1+1+1+1) instead of (111111)
        replaced = text.replace('!+[]', '1').replace('!![]', '1').replace('+[]', '0')
        expanded = cls._recursive_token_multiplier(replaced)
        return eval(expanded)

    @classmethod
    def _recursive_token_multiplier(cls, text):
        matches = re.findall(cls._outer_parentheses_group_regex, text)
        result = text
        for valNum, val in enumerate(matches):
            if not val.endswith('0)'):
                result = result.replace(val, '(' +
                                        cls._recursive_token_multiplier(cls._remove_parenthesis(val)) + ')', 1)
            else:
                multiplier = int(math.pow(10, len(matches) - 1 - valNum))
                result = result.replace(val, val.replace('0)', ')*{}'.format(multiplier)), 1)

        return result

    @classmethod
    def _remove_parenthesis(cls, text):
        if text.startswith('(') and text.endswith(')'):
            return (text[1:])[:-1]
        return text

    @classmethod
    def _find_function_name(cls, text):
        start_of = text.find('=function(')
        return text[start_of - 1]
