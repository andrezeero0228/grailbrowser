"""A parser for SGML, using the derived class as static DTD.


"""
__version__ = "$Revision: 1.3 $"
# $Source: /cvsroot/grail/grail/src/sgml/SGMLParser.py,v $

# XXX There should be a way to distinguish between PCDATA (parsed
# character data -- the normal case), RCDATA (replaceable character
# data -- only char and entity references and end tags are special)
# and CDATA (character data -- only end tags are special).


from SGMLLexer import SGMLLexer, SGMLError
import string


# SGML parser class -- find tags and call handler functions.
# Usage: p = SGMLParser(); p.feed(data); ...; p.close().
# The dtd is defined by deriving a class which defines methods
# with special names to handle tags: start_foo and end_foo to handle
# <foo> and </foo>, respectively, or do_foo to handle <foo> by itself.


class SGMLParser(SGMLLexer):

    doctype = ''			# 'html', 'sdl', ...

    def __init__(self, verbose = 0):
	self.verbose = verbose
	SGMLLexer.__init__(self)

    # Interface -- reset this instance.  Loses all unprocessed data.
    def reset(self):
	SGMLLexer.reset(self)
	self.normalize(1)		# normalize NAME token to lowercase
	self.restrict(1)		# impose user-agent compatibility
	self.omittag = 1		# default to HTML style
	self.stack = []
	self.cdata = 0

    #  The following methods are the interface subclasses need to
    #  override to support any special handling of tags, data, or
    #  anomalous conditions.

    # Example -- handle entity reference, no need to override
    entitydefs = \
	       {'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"'}

    def handle_entityref(self, name):
	table = self.entitydefs
	if table.has_key(name):
	    self.handle_data(table[name])
	else:
	    self.unknown_entityref(name)


    def handle_data(self, data):
	"""
	"""
	pass

    def handle_endtag(self, tag, method):
	"""
	"""
	method()

    def handle_starttag(self, tag, method, attributes):
	"""
	"""
	method(attributes)

    def unknown_charref(self, ordinal):
	"""
	"""
	pass

    def unknown_endtag(self, tag):
	"""
	"""
	pass

    def unknown_entityref(self, ref):
	"""
	"""
	pass

    def unknown_namedcharref(self, ref):
	"""
	"""
	pass

    def unknown_starttag(self, tag, attrs):
	"""
	"""
	pass

    def report_unbalanced(self, tag):
	"""
	"""
	pass


    #  The remaining methods are the internals of the implementation and
    #  interface with the lexer.  Subclasses should rarely need to deal
    #  with these.

    # For derived classes only -- enter literal mode (CDATA)
    def setliteral(self, *args):
	self.cdata = 1 #@@ finish implementing this...

    def lex_data(self, string):
	self.handle_data(string)

    def lex_starttag(self, tag, attrs):
	#print 'received start tag', `tag`
	if not tag:
	    if self.omittag and self.stack:
		tag = self.lasttag
	    elif not self.omittag:
		self.lex_endtag('')
		return
	    elif not self.stack:
		tag = self.doctype
		if not tag:
		    raise SGMLError, \
			  'Cannot start the document with an empty tag.'
	attrs = attrs.items()	# map to list of tuples for now
	try:
	    method = getattr(self, 'start_' + tag)
	except AttributeError:
	    try:
		method = getattr(self, 'do_' + tag)
	    except AttributeError:
		self.unknown_starttag(tag, attrs)
		return -1
	    self.handle_starttag(tag, method, attrs)
	    return 0
	else:
	    self.lasttag = tag
	    self.stack.append(tag)
	    self.handle_starttag(tag, method, attrs)

    def lex_endtag(self, tag):
	#print 'received end tag', `tag`
	if not tag:
	    found = len(self.stack) - 1
	    if found < 0:
		self.unknown_endtag(tag)
		return
	else:
	    if tag not in self.stack:
		try:
		    method = getattr(self, 'end_' + tag)
		except AttributeError:
		    self.unknown_endtag(tag)
		self.report_unbalanced(tag)
		return			# should raise SGMLError ???
	    found = len(self.stack)
	    for i in range(found):
		if self.stack[i] == tag: found = i
	while len(self.stack) > found:
	    tag = self.stack[-1]
	    try:
		method = getattr(self, 'end_' + tag)
	    except AttributeError:
		self.unknown_endtag(tag)
	    else:
		self.handle_endtag(tag, method)
	    del self.stack[-1]


    named_characters = {'re' : '\r',
			'rs' : '\n',
			'space' : ' '}

    def lex_namedcharref(self, name):
	if self.named_characters.has_key(name):
	    self.handle_data(self.named_characters[name])
	else:
	    self.unknown_namedcharref(name)

    def lex_charref(self, ordinal):
	if 0 < ordinal < 256:
	    self.handle_data(chr(ordinal))
	else:
	    self.unknown_charref(ordinal)

    def lex_entityref(self, name):
	self.handle_entityref(name)

    def lex_declaration(self, strings):
	print 'Declaration:'
	print strings



#  The test code is now located in test_parser.py.