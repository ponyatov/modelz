import sys

with open(sys.argv[0]+'.src') as F:
    vm // F.read() ; INTERPRET(vm) ; F.close()
