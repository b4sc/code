from expr import *

class SMTtoSExpr:
    def __init__(self):
        pass


######


import z3
class Z3SMTtoSExpr(SMTtoSExpr):

    def getSort(self,sort):
        if str(sort) == "Bool":
            return Sort.Bool
        elif str(sort) == "String":
            return Sort.Bool
        elif str(sort) == "Int":
            return Sort.Int
        elif str(sort) == "ReSort(String)":
            return Sort.RegEx
        return None

    def getZ3AST(self,file_path):
        return z3.parse_smt2_file(file_path)

    def getAST(self,file_path):
        z3ast = self.getZ3AST(file_path)
        ast = ASTRef()
        if type(z3ast) in [z3.z3.AstVector]:
            for e in z3ast:
                ast.add_node(self.translateExpr(e))
        return ast

    def _extractOpName(self,op):
        return str(op.sexpr()).split(" ")[1]

    # HOL functions
    hofunc = ["At","str.substr","PrefixOf","SuffixOf","Contains","IndexOf","Replace","IntToStr","StrToInt"]
    def _determineKind(self,expr,is_variable,is_const):
        if is_variable:
            return Kind.VARIABLE
        if is_const:
            return Kind.CONSTANT

        children = expr.children()
        if str(expr.decl()) in self.hofunc:
            return Kind.HOL_FUNCTION
        elif str(expr.decl()) == "InRe":
            return Kind.REGEX_CONSTRAINT
        elif type(expr) == z3.z3.BoolRef and len(children) == 2 and str(children[0].sort()) == "String" and children[0].sort() == children[1].sort():
            return Kind.WEQ
        elif type(expr) == z3.z3.BoolRef and len(children) == 2 and str(children[0].sort()) == "Int" and children[0].sort() == children[1].sort():
            return Kind.LENGTH_CONSTRAINT
        else:
            return Kind.OTHER


    def translateExpr(self,expr):
        sort = self.getSort(expr.sort())
        children = [self.translateExpr(c) for c in expr.children()]
        is_variable = z3.is_const(expr) and expr.decl().kind() == z3.Z3_OP_UNINTERPRETED
        is_const = not is_variable and len(children) == 0
        op = self._extractOpName(expr.decl())
        kind = self._determineKind(expr,is_variable,is_const)
        
        if is_const:
            params = [expr.sexpr()]
        else:
            params = expr.params()

        if type(expr) == z3.z3.SeqRef:
            return StringExpr(children,params,str(op),kind)  
        elif type(expr) == z3.z3.BoolRef:
            return BoolExpr(children,params,str(op),kind)
        elif type(expr) == z3.z3.ReRef:
            return ReExpr(children,params,str(op),kind)
        elif type(expr) == z3.z3.ArithRef:
            return IntExpr(children,params,str(op),kind)
        elif type(expr) == z3.z3.IntNumRef:
            return IntExpr(children,params,str(op),kind)


        # Fall back
        return ExprRef(children,[],str(op),kind) 