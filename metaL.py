
import os,sys

class Frame:
    def __init__(self,V):
        self.type  = self.__class__.__name__.lower()
        self.val   = V
        self.slot  = {}
        self.nest  = []
        self.immed = False
        
    def __repr__(self):
        return self.dump()
    def dump(self,depth=0,prefix='',voc=True):
        tree = self._pad(depth) + self.head(prefix)
        if not depth: Frame._dumped = []
        if self in Frame._dumped: return tree + ' _/'
        else: Frame._dumped.append(self)
        if voc:
            for i in self.slot:
                tree += self.slot[i].dump(depth+1,prefix=i+' = ')
        for j in self.nest:
            tree += j.dump(depth+1)
        return tree
    def head(self,prefix=''):
        return '%s<%s:%s> @%x' % (prefix,self.type,self._val(),id(self))
    def _val(self):
        return str(self.val)
    def _pad(self,depth):
        return '\n' + ' '*4 * depth
    
    def __iter__(self): return (i for i in self.nest)
    
    def __getitem__(self,key):
        if isinstance(key,str): return self.slot[key]
#         if isinstance(key,int): return self.nest[key]
        raise SyntaxError(type(key))
    def __setitem__(self,key,that):
        self.slot[key] = that ; return self
    def __lshift__(self,that):
        self.slot[that.val] = that ; return self
        
    def __floordiv__(self,that):
        return self.push(that)
    def push(self,that):
        self.nest.append(that) ; return self
    def pop(self):
        return self.nest.pop()
    def top(self):
        return self.nest[-1]
    def dropall(self):
        self.nest = []
    def dup(self):
        self // self.top()
    def drop(self):
        self.pop()
    
    def eval(self,vm):
        vm // self

class Primitive(Frame): pass
class Symbol(Primitive): pass
class String(Primitive): pass

class Container(Frame): pass
class Vector(Container): pass
class Stack(Container): pass
class Dict(Container): pass

class Active(Frame): pass

class Cmd(Active):
    def __init__(self,F,I=False):
        Frame.__init__(self, F.__name__)
        self.fn = F
        self.immed = I
    def eval(self,vm):
        self.fn(vm)
        
class VM(Active):
#     def __init__(self,V):
#         Active.__init__(self, V)
#         self.defs = self
#         self.use  = [self]
    def __setitem__(self,key,F):
        if callable(F): self[key] = Cmd(F) ; return self 
        else: return Active.__setitem__(self, key, F)
    def __lshift__(self,F):
        if callable(F): return self << Cmd(F)
        else: return Active.__lshift__(self, F)
        
class Seq(Active):
    def eval(self,vm):
        for i in self.nest: i.eval(vm)
        
class Meta(Frame): pass
class Group(Meta): pass
class Class(Meta): pass

import ply.lex as lex

tokens = ['symbol','string']

t_ignore = ' \t\r\n'
t_ignore_comment = r'[#\\].*'

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
    r'[`]|[^ \t\r\n\#\\]+'
    return Symbol(t.value)

def t_ANY_error(t):
    raise SyntaxError(t)

lexer = lex.lex()

vm = VM('metaL') ; vm << vm

def BYE(vm): sys.exit(0)
vm << BYE

def Q(vm): print vm.dump(voc=False)
vm['?'] = Cmd(Q,True)

def QQ(vm): print vm.dump() ; BYE(vm)
vm['??'] = Cmd(QQ,True)

def DROPALL(vm): vm.dropall()
vm['.'] = DROPALL

def DUP(vm): vm.dup()
vm << DUP

def DROP(vm): vm.drop()
vm << DROP

def PUSH(vm): vm.pop() // vm.pop()
vm['//'] = PUSH

def EQ(vm): addr = vm.pop().val ; vm[addr] = vm.pop()
vm['='] = EQ 

def LL(vm): vm.pop() << vm.pop() # target = vm.pop() ; vm // ( target << vm.pop() )
vm['<<'] = LL

def VOC(vm): voc = Dict(vm.pop().val) ; vm // voc 
vm << VOC

# def DEFS(vm): vm.defs = vm.pop()
# vm << DEFS
def USE(vm): vm.use.append(vm.top())
vm << USE 

vm['DEFS'] = vm
vm['USE'] = ( Vector('search') // vm ) 

def QUOTE(vm): WORD(vm)
vm['`'] = Cmd(QUOTE,True)

def WORD(vm):
    token = lexer.token()
    if token: vm // token
    return token

def FIND(vm):
    token = vm.pop()
    print token
    for voc in vm['USE']:#.nest:
        try:
            vm // voc[token.val]
            if token.val == '??': print 'x',voc[token.val],vm
        except KeyError:
            vm // voc[token.val.upper()] # case fallback

def EVAL(vm): vm.pop().eval(vm)

def INTERPRET(vm):
    while True:
        if not WORD(vm): break
        if isinstance(vm.top(),Symbol): FIND(vm)
        EVAL(vm)

def GROUP(vm): vm << Group(vm.pop().val)
vm << GROUP

def CLASS(vm):
    cls = Class(vm.pop().val) ; vm['DEFS'] << cls ; vm // cls
vm << CLASS

def SUPER(vm): sup = vm.pop() ; vm.pop()['super'] = sup
vm << SUPER

if __name__ == '__main__':
    with open('model.met') as src: lexer.input(src.read())
    INTERPRET(vm)
