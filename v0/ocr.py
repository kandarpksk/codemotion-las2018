from helpers import *

# recognize text with tesseract


# ignore non-code segments

import keyword as kw
big_kws = [word for word in kw.kwlist if len(word) > 3]
# assert, break, class, continue, elif, else, except, exec, finally, from, global, import, lambda, pass, print, raise, return, while, with, yield
med_kws = [word for word in kw.kwlist if len(word) == 3]
# and, def, del, for, not, try
sml_kws = [word for word in kw.kwlist if len(word) < 3]
# as, if, in, is, or

import re
# test_string = 'if NOT inside a string'

# finds words ("with" keywords)	# see if keeping duplicates is fine
def loose_check(string):
	# finds keywords (anywhere)
	kws = [keyword for keyword in kw.kwlist if keyword in string]
	return flatten([[w for w in test_string.split() if k in w] for k in kws])

# regular (pun intended) check
def check_for_keywords(string):
	# find words (with keyword as prefix)
	kws_re = re.compile(r'\b(' + '|'.join(kw.kwlist) + r')([a-z]*)')
	return [''.join(w) for w in kws_re.findall(string)]

def strict_check(string):
	# finds keywords (strictly)
	return [word for word in kw.kwlist if word in string.split()]

# print loose_check(test_string)
# print check_for_keywords(test_string)
# print strict_check(test_string)