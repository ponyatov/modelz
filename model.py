
import os,sys

class Frame:
    def __init__(self,V):
        self.type = self.__class__.__name__.lower()
        self.val  = V
        self.slot = {}
        self.nest = []
        self.immed = False
        
    def __repr__(self):
        return self.dump()
    def dump(self,depth=0,prefix='',voc=True):
        tree = self._pad(depth) + self.head(prefix)
        if voc:
            for i in self.slot:
                tree += self.slot[i].dump(depth+1,prefix=i+' = ')
        for j in self.nest:
            tree += i.dump(depth+1)
        return tree
    def head(self,prefix=''):
        return '%s<%s:%s> @%x' % (prefix,self.type,self._val(),id(self))
    def _val(self):
        return str(self.val)
    def _pad(self,depth):
        return '\n' + ' '*4 * depth
    
    def __getitem__(self,key):
        return self.slot[key]
    def __setitem__(self,key,that):
        self.slot[key] = that ; return self
        
    def __floordiv__(self,that):
        return self.push(that)
    def push(self,that):
        self.nest.append(that) ; return self
    def pop(self):
        return self.nest.pop()
    def top(self):
        return self.nest[-1]
    
    def eval(self,vm):
        vm // self

class Symbol(Frame): pass
class String(Frame): pass

class Stack(Frame): pass
class Dict(Frame): pass

class Cmd(Frame):
    def __init__(self,F,I=False):
        Frame.__init__(self, F.__name__)
        self.fn = F
        self.immed = I
    def eval(self,vm):
        self.fn(vm)
        
class VM(Frame):
    def __setitem__(self,key,F):
        if callable(F): self[key] = Cmd(F) ; return self 
        else: return Frame.__setitem__(self, key, F)

import ply.lex as lex

tokens = ['symbol','string']

t_ignore = ' \t\r\n'
t_ignore_comment = '\#.*'

states = (('str','exclusive'),)

t_str_ignore = ''
def t_str(t):
    r'\''
    t.lexer.push_state('str')
    t.lexer.string = ''
def t_str_str(t):
    r'\''
    t.lexer.pop_state()
    return String(t.lexer.string)
def t_str_any(t):
    r'.'
    t.lexer.string += t.value

def t_symbol(t):
    r'[`]|[^ \t\r\n\#]+'
    return Symbol(t.value)

def t_ANY_error(t):
    raise SyntaxError(t)

lexer = lex.lex()

vm = VM('metaL')

def BYE(vm): sys.exit(0)
vm['BYE'] = BYE

def Q(vm): print vm.dump(voc=False)
vm['?'] = Q

def QQ(vm): print vm.dump() ; BYE(vm)
vm['??'] = QQ

def QUOTE(vm): WORD(vm)
vm['`'] = QUOTE

def EQ(vm): vm[vm.pop().val] = vm.pop()
vm['='] = EQ 

def WORD(vm):
    token = lexer.token()
    if token: vm // token
    return token

def FIND(vm):
    token = vm.pop()
    vm // vm[token.val] ; return True
    return False

def EVAL(vm): vm.pop().eval(vm)

def INTERPRET(vm):
    while True:
        if not WORD(vm): break
        if isinstance(vm.top(),Symbol):
            if not FIND(vm): raise SyntaxError(vm)
        EVAL(vm)

# if __name__ == '__main__':
with open('model.met') as src: lexer.input(src.read())
INTERPRET(vm)
