import cnf
import copy
class Formula(object):
    def __init__(self, subs = []):
        self.m_subf = subs
    def subf(self):
        return self.m_subf
    def eval(self, i):
        return False
    def toString(self):
        return "INVALID"
    def toCnf(self):
        """ Vrati reprezentaciu formuly v CNF tvare. """
        return cnf.Cnf()
class Variable(Formula):
    def __init__(self, name):
        Formula.__init__(self)
        self.name = name
    def eval(self, i):
        return i[self.name]
    def toString(self):
        return self.name
    def toCnf(self):
        return cnf.Cnf([cnf.CnfClause([cnf.CnfLit(self.name)])])
class Negation(Formula):
    def __init__(self, orig):
        Formula.__init__(self, [orig])
    def originalFormula(self):
        return self.subf()[0]
    def eval(self, i):
        return not self.originalFormula().eval(i)
    def toString(self):
        return "-%s" % (self.originalFormula().toString())
    def product(self,clauses,level,selectedLiterals):
        if level<len(clauses):
            for lit in clauses[level]:
                selectedLiterals.append(lit)
                self.product(clauses, level+1, selectedLiterals)
                selectedLiterals.pop()

        else:
            self.resCnf.append(cnf.CnfClause(selectedLiterals))
        
    def toCnf(self):
        ocnf = self.originalFormula().toCnf()
        for cls in ocnf:
            for lit in cls:
                lit.neg = not lit.neg
        self.resCnf = cnf.Cnf()
        self.product(ocnf,0,[])
        return self.resCnf
                
class Disjunction(Formula):
    def __init__(self, subs):
        Formula.__init__(self, subs)
    def eval(self, i):
        for f in self.subf():
            if f.eval(i):
                return True
        return False
    def toString(self):
        return '(' + '|'.join([f.toString() for f in self.subf()]) + ')'
    def doProduct(self, cnfs, level, rClause, rCnf):
        if level < len(cnfs):
            for clause in cnfs[level]:
                extRClause = copy.deepcopy(rClause)
                extRClause.extend(copy.deepcopy(clause))
                self.doProduct(cnfs, level+1, extRClause, rCnf)
        else:
            rCnf.append(rClause)
    def toCnf(self):
        # prevedieme vsetky podrofmuly do cnf
        cnfs = []
        for sf in self.subf():
            cnfs.append(sf.toCnf())
        # roznmasobime ich, pricom vzniknute klauzy
        # ukladame do f
        c = cnf.Cnf()
        self.doProduct(cnfs, 0, cnf.CnfClause(), c)
        return c
class Conjunction(Formula):
    def __init__(self, subs):
        Formula.__init__(self, subs)
    def eval(self, i):
        for f in self.subf():
            if not f.eval(i):
                return False
        return True
    def toString(self):
        return '(' + '&'.join([f.toString() for f in self.subf()]) + ')'
    def toCnf(self):
        c = cnf.Cnf()
        for f in self.subf():
            cf = f.toCnf()
            for clause in cf:
                c.append(clause)
        return c
class Binary(Formula):
    def __init__(self, left, right, conj):
        Formula.__init__(self, [left, right])
        self.conj = conj
    def left(self):
        return self.subf()[0]
    def right(self):
        return self.subf()[1]
    def toString(self):
        return '(%s%s%s)' % (self.left().toString(), self.conj, self.right().toString())
class Implication(Binary):
    def __init__(self, left, right):
        Binary.__init__(self, left, right, '=>')
    def eval(self, i):
        return (not self.left().eval(i)) or self.right().eval(i)
    def toCnf(self):
        return Disjunction([Negation(self.left()),self.right()]).toCnf()
class Equivalence(Binary):
    def __init__(self, left, right):
        Binary.__init__(self, left, right, '<=>')
    def eval(self, i):
        return self.left().eval(i) == self.right().eval(i)
    def toCnf(self):
        return Conjunction([Implication(self.left(),self.right()),
                           Implication(self.right(),self.left())]).toCnf()
    
# vim: set sw=4 ts=4 sts=4 et :
