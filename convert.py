import os, sys, json, re, logging, datetime
from dateutil import parser
from keywords import *

mapping = {
    int: INT,
    float: FLOAT,
    str: STRING,
    bool: BOOLEAN,
    type(None): OBJECT
}

inner = []

def clean(string):
    return re.sub("[^A-Za-z0-9_]+", "", string).lstrip("[^0-9]+")


def autoindent(pojo):
    def tab(line):
        return "\t" + line

    pojo[1: - 1] = list(map(tab, pojo[1: -1]))
    return pojo


def format(pojo):
    return "\n".join(pojo)


def get_if_date(string):
    try:
        parser.parse(string)
        return DATE
    except parser.ParserError:
        return STRING


def get_leading_and_trailing_underscores(string):
    leading_ = " "
    trailing_ = ""

    while string[0] == UNDERSCORE:
        leading_ += UNDERSCORE
        string = string[1:]

    while string[-1] == UNDERSCORE:
        trailing_ += UNDERSCORE
        string = string[:-1]
    trailing_ += DELIMITER

    return leading_, trailing_, string


def to_camel_case(snake_case):
    snake_case = clean(snake_case)
    leading_, trailing_, snake_case = get_leading_and_trailing_underscores(snake_case)
    camelCase = snake_case.split(UNDERSCORE)
    if len(camelCase) > 1:
        camelCase = camelCase.pop(0).lower() + "".join(map(str, [word.title() for word in camelCase]))
    else:
        camelCase = camelCase[0]

    return leading_ + camelCase + trailing_


def to_pascal_case(snake_case):
    snake_case = clean(snake_case)
    leading_, trailing_, snake_case = get_leading_and_trailing_underscores(snake_case)
    leading_, trailing_ = leading_[1:], trailing_[:-1]
    PascalCase = snake_case.split(UNDERSCORE)

    PascalCase = "".join(map(str, [word.title() for word in PascalCase]))

    return leading_ + PascalCase + trailing_


def add_class(obj, classname):
    inner.append(json2pojo(obj, classname=classname))
    return classname


def list2pojo(obj, datatype, name):
    try:
        pytype = type(obj[0])
    except IndexError:
        return datatype.format(OBJECT)

    if pytype == list:
        return list2pojo(obj[0], datatype.format(LIST), name)
    elif pytype == dict:
        return datatype.format(add_class(obj[0], name))
    else:
        javatype = mapping.get(pytype)
        if javatype == None:
            raise TypeError("Unknown datatype: {}".format(pytype))
        elif javatype == STRING:
            javatype = get_if_date(obj[0])
        return datatype.format(javatype)


def json2pojo(obj, classname):
    pojo = list()
    pojo.append(PUBLIC + CLASS + classname + OPEN_BRACE)
    for key, value in obj.items():
        pytype = type(value)
        if pytype == list:
            javatype = list2pojo(value, LIST, to_pascal_case(key))
        elif pytype == dict:
            javatype = add_class(value, to_pascal_case(key))
        else:
            javatype = mapping.get(pytype)
            if javatype == None:
                raise TypeError("Unknown datatype: {}".format(pytype))
            elif javatype == STRING:
                javatype = get_if_date(value)
        
        varname = to_camel_case(key)
        if not varname[1: -1] == key:
            pojo.append(JSON_PROPERTY.format(key))
        pojo.append(PRIVATE + javatype + varname)

    pojo.append(CLOSE_BRACE)
    return pojo


if __name__ == "__main__":
    path = sys.argv[1]
    if len(sys.argv) > 2:
        classname = clean(sys.argv[2])
    else:
        classname = "POJO"

    if os.path.exists(path):
        file = open(path)
        string = file.read()

    try:
        parsed = json.loads(string)
    except Exception:
        logging.error("Failed to parse json. Check if the json is valid")

    inner.append(json2pojo(parsed, classname))
    pojos = list(map(autoindent, inner))
    pojos = [format(pojo) for pojo in pojos]

    for pojo in pojos:
        print(pojo)
