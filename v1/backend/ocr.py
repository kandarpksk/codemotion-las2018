from helpers import *

# recognize text with tesseract


# ignore non-code segments

import keyword as kw
cpp_kwlist = ['alignas', 'alignof', 'and', 'and_eq', 'asm',
		'atomic_cancel', 'atomic_commit', 'atomic_noexcept',
		'auto', 'bitand', 'bitor', 'bool', 'break', 'case',
		'catch', 'char', 'char16_t', 'char32_t', 'class',
		'compl', 'concept', 'const', 'constexpr', 'const_cast',
		'continue', 'decltype', 'default', 'delete', 'do',
		'double', 'dynamic_cast', 'else', 'enum', 'explicit',
		'export', 'extern', 'false', 'float', 'for', 'friend',
		'goto', 'if', 'import', 'inline', 'int', 'long',
		'module', 'mutable', 'namespace', 'new', 'noexcept',
		'not', 'not_eq', 'nullptr', 'operator', 'or', 'or_eq',
		'private', 'protected', 'public', 'register',
		'reinterpret_cast', 'requires', 'return', 'short',
		'signed', 'sizeof', 'static', 'static_assert',
		'static_cast', 'struct', 'switch', 'synchronized',
		'template', 'this', 'thread_local', 'throw', 'true',
		'try', 'typedef', 'typeid', 'typename', 'union',
		'unsigned', 'using', 'virtual', 'void', 'volatile',
		'wchar_t', 'while', 'xor', 'xor_eq']

py_big_kws = [word for word in kw.kwlist if len(word) > 3]
# assert, break, class, continue, elif, else, except, exec,
# finally, from, global, import, lambda, pass, print, raise,
# return, while, with, yield
cpp_big_kws = [word for word in cpp_kwlist if len(word) > 3]

py_med_kws = [word for word in kw.kwlist if len(word) == 3]
# and, def, del, for, not, try
cpp_med_kws = [word for word in cpp_kwlist if len(word) == 3]

py_sml_kws = [word for word in kw.kwlist if len(word) < 3]
# as, if, in, is, or
cpp_sml_kws = [word for word in cpp_kwlist if len(word) < 3]

import re
# test_string = 'if NOT inside a string'

# finds words ("with" keywords)	# see if keeping duplicates is fine
def loose_check(string):
	# finds keywords (anywhere)
	kws = [keyword for keyword in set(kw.kwlist+cpp_kwlist) if keyword in string]
	return flatten([[w for w in test_string.split() if k in w] for k in kws])

# regular (pun intended) check
def check_for_keywords(string):
	# find words (with keyword as prefix)
	kws_re = re.compile(r'\b(' + '|'.join(set(kw.kwlist+cpp_kwlist)) + r')([a-z]*)')
	return [''.join(w) for w in kws_re.findall(string)]

def strict_check(string):
	# finds keywords (strictly)
	return [word for word in set(kw.kwlist+cpp_kwlist) if word in string.split()]

# print loose_check(test_string)
# print check_for_keywords(test_string)
# print strict_check(test_string)
