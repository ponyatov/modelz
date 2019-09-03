import sys

sys.stdout = log = open(sys.argv[0]+'.log','w')

class Frame:
    def __init__(self, V, line=None):
        self.type = self.__class__.__name__.lower()
        self.val  = V
        self.slot = {}
        self.nest = []
        if line: self.line = line

    def __repr__(self):
        return self.dump()
    def dump(self,depth=0,prefix=''):
        tree = self._pad(depth) + self.head(prefix)
        for i in self.slot:
            tree += self.slot[i].dump(depth+1,prefix='%s = '%i)
        for j in self.nest:
            tree += j.dump(depth+1)
        return tree
    def head(self,prefix=''):
        return '%s<%s:%s> @%x' % (prefix,self.type,self._val(),id(self))
    def _pad(self,depth):
        return '\n' + '\t' * depth
    def _val(self):
        return str(self.val)

    def __getitem__(self,key):
        return self.slot[key]
    def __setitem__(self,key,that):
        self.slot[key] = that ; return self
    def __floordiv__(self,that):
        self.nest.append(that) ; return self

    def pop(self):
        return self.nest.pop(-1)
    def top(self):
        return self.nest[-1]

class Error(Frame):
    def __init__(self,V,ctx):
        Frame.__init__(self,V)
        self['context'] = ctx
        self['top'] = ctx.top()
        self['line'] = Number(ctx.top().line)

class Primitive(Frame): pass
class Symbol(Primitive): pass
class String(Primitive): pass
class Number(Primitive): pass

class Active(Frame): pass
class Cmd(Active): pass
class VM(Active): pass

vm = VM('metaL')

import ply.lex as lex

tokens = ['symbol']

t_ignore = ' \t\r\n'
t_ignore_comment = r'[\#\\].*'

def t_symbol(t):
    r'[^ \t\r\n\#\\]+'
    return Symbol(t.value,line=t.lineno)

def t_error(t): raise SyntaxError(t)

def WORD(ctx):
    token = ctx.lexer.token()
    if token: ctx // token
    return token

def FIND(ctx):
    token = ctx.pop()
    try: ctx // ctx[token.val] ; return True
    except KeyError: ctx // token ; return False    

def INTERPRET(ctx):
    ctx.lexer = lex.lex() ; ctx.lexer.input(ctx.pop().val)
    while True:
        if not WORD(ctx): break
        if isinstance(ctx.top(),Symbol):
            if not FIND(ctx): raise Error("not found",ctx=ctx)
        print ctx

with open(sys.argv[0]+'.src') as F:
    vm // String(F.read())
    INTERPRET(vm)
    F.close()
