import datetime
import math
import random

VALID_CHARS = "123456789ACDEFGHJKMNPRTUVWXY"
LEN = 3

def today():
    return datetime.datetime.now()

def getBaseCharacters():
    '''Return base characters'''
    return VALID_CHARS


def getIdentifierLength():
    '''Return Identifier Length'''
    return LEN


def generate(id_without_check):
    '''Append Check digit '''
    checkdigit = computeCheckDigit(id_without_check)
    return id_without_check + checkdigit


def computeCheckDigit(identifier):
        '''Compute CheckDigit for a passed identifier'''
        valid_chars = getBaseCharacters()
        mod = len(valid_chars)

        # Remove leading or trailing whitespace, convert to uppercase
        identifier = identifier.strip().upper()

        # This will be a running total
        sum = 0

        # loop through digits from right to left
        for n, char in enumerate(reversed(identifier)):
            if not valid_chars.count(char):
                raise Exception('InvalidIDException')

            # Point
            code_point = valid_chars.index(char)

            # weight will be the current digit's contribution to
            # the running total
            weight = None
            if (n % 2 == 0):
                weight = (2 * code_point)
            else:
                weight = code_point

            weight = (weight / mod) + (weight % mod)
            # keep a running total of weights
            sum += weight

        # return check digit
        remainder = sum % mod
        checkCodePoint = mod - remainder
        try:
            checkdigit = valid_chars[checkCodePoint]
        except:
            checkdigit = valid_chars[0]

        return checkdigit


def validateCheckDigit(identifier):
        '''Compute CheckDigit for a passed identifier'''
        valid_chars = getBaseCharacters()
        mod = len(valid_chars)

        # remove leading or trailing whitespace, convert to uppercase
        identifier = identifier.strip().upper()

        # this will be a running total
        sum = 0
        # loop through digits from right to left
        for n, char in enumerate(reversed(identifier)):
            if not valid_chars.count(char):
                # raise Exception('InvalidIDException')
                return False

            # Point
            code_point = valid_chars.index(char)
            # weight will be the current digit's contribution to
            # the running total
            weight = None
            if (n % 2 == 0):
                weight = code_point
            else:
                weight = (2 * code_point)

            weight = (weight / mod) + (weight % mod)
            # keep a running total of weights
            sum += weight

        # return check digit
        remainder = sum % mod
        return (remainder == 0)


def generateIdentifier():
    char = getBaseCharacters()
    slen = getIdentifierLength()
    identifier = ''.join([random.choice(char) for i in range(0, slen - 1)])
    p = generate(identifier)
    print p
    if p.isdigit() or p.isalpha():
        generateIdentifier()
    return p
