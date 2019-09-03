import sys

sys.stdout = log = open(sys.argv[0]+'.log','w')

class Frame:
    def __init__(self, V):
        self.type = self.__class__.__name__.lower()
        self.val  = V
        self.slot = {}
        self.nest = []

    def __repr__(self):
        return self.dump()
    def dump(self,depth=0):
        tree = self._pad(depth) + self.head()
        for j in self.nest:
            tree += j.dump(depth+1)
        return tree
    def head(self):
        return '<%s:%s> @%x' % (self.type,self._val(),id(self))
    def _pad(self,depth):
        return '\n' + '\t' * depth
    def _val(self):
        return str(self.val)

    def __getitem__(self,key):
        return self.slot[key]
    def __floordiv__(self,obj):
        self.nest.append(obj) ; return self

    def pop(self):
        return self.nest.pop(-1)
    def top(self):
        return self.nest[-1]

class Primitive(Frame): pass
class Symbol(Primitive): pass
class String(Primitive): pass

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
    return Symbol(t.value)

def t_error(t): raise SyntaxError(t)

def WORD(ctx):
    token = ctx.lexer.token()
    if token: ctx // token
    return token

def FIND(ctx):
    token = ctx.pop()
    ctx // ctx[token.val] ; return True
    ctx // token ; return False    

def INTERPRET(ctx):
    ctx.lexer = lex.lex() ; ctx.lexer.input(ctx.pop().val)
    while True:
        if not WORD(ctx): break
        if isinstance(ctx.top(),Symbol):
            if not FIND(ctx): raise SyntaxError(ctx)
        print ctx

with open(sys.argv[0]+'.src') as F:
    vm // String(F.read())
    INTERPRET(vm)
    F.close()
