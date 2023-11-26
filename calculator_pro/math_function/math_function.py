from typing import Any
import re, numpy
from .exception import *


# [step 1] >>> f = MathFunction(func_exp)
# [step 2] >>> f.set_used_functions({"func":callback})
#   e.g. If func "sin" and "convolve" is in your expression, `f.set_used_functions({"sin":math.sin, "convolve":numpy.convolve})`
# [step 3] >>> f.format_expression()
#   Now you can use `f.expression` to check if the expression for python to calculate is the same rule of yours.
# [step 4] >>> f.calc(variable1, variable2, ...)
#   Pass in variable(s) for calculation.


class MathFunction:


    def __init__(self, func_exp: str) -> None:
        '''Parameter

func_exp : str
- SIMPLE  : f(variable)=math_expression
- COMPLEX : f(variable1, variable2, ...)=math_expression, \constant1=value1, constant2=value2
e.g. f(h)=1/2*gh^2, \g=9.8'''
        name, variables, constants, expression = self._function_expression_processing(func_exp)
        self.name = name
        self.variables = variables # str "xyz"
        self.constants = "".join(constants.keys()) # str "abc"
        self.constants_map = constants # dict {"const1":value1}
        same_var_const = set(variables) & set(constants)
        if same_var_const:
            raise SameVarConstError(same_var_const)
        self.expression = expression
        self.separate()


    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.calc(*args, **kwargs)


    def _function_expression_processing(self, func_exp: str):
        func_exp = func_exp.replace(" ","") + ","
        re_match = re.fullmatch(r"([\w]+)\(([\w,]+)\)=([^\\]+)\\?((?:[\w+]=(?:\-|\+)?\d+(?:\.\d+)?,)+)",func_exp)
        if not re_match:
            raise MathExpressionError(func_exp)
        name, variables, expression, constants = re_match.groups()
        expression = expression[:-1] # del "," in the end, e.g. "1/2*gh^2," -> "1/2*gh^2"
        constants = {i:float(k) for i,k in re.findall(r"([\w+])=([.0-9]+)", constants)}
        if "e" not in constants.keys():
            constants.update({"e":numpy.e})
        
        return name, variables.replace(",",""), constants, expression


    def __repr__(self) -> str:
        func = f"{self.name}({','.join(self.variables)})={self.expression}"
        if self.constants:
            func = f"{func},\{','.join([f'{i}={k}' for i,k in self.constants_map.items()])}"
        return func


    def separate(self):
        '''separate possible func, determined func, multiplication of var & const'''
        possible_func = re.findall(r"(?<![{0}{1}])[{0}{1}]+(?=\()".format(self.variables,self.constants), self.expression)
        # "possible": e.g. SOMETIMES "sin" is a function but "s","i","n" are also constants or variables in this expresion...? So sin(further expression...) can represent function sin, or the multiplication of s,i,n.
        determined_func = list(set(re.findall(r"[a-zA-Z_]+[0-9a-zA-Z_]*(?=\()", self.expression)) - set(possible_func)) # e.g. "log10(x)" -> match "log10(" -> output "log10"
        letter_composed = set(re.findall(r"(?<![a-zA-Z_0-9])[0-9]*[a-zA-Z_]+[0-9a-zA-Z_]*(?![a-zA-Z_0-9\(])", self.expression)) # letter composed without `(` behind, e.g. 10ac, 4xy, ac2bc
        var_const_multi = [i for i in letter_composed if re.fullmatch(r"[0-9]*[{}{}]+".format(self.variables,self.constants), i)] # e.g. var:x,y, const:a -> "2ax" √; "3bz" ×
        if len(letter_composed) > len(var_const_multi):
            raise FuncOrMultiWrongError(set(letter_composed)-set(var_const_multi))
        self.possible_func, self.determined_func, self.letter_composed, self.var_const_multi = possible_func, determined_func, letter_composed, [i for i in var_const_multi if len(i) > 1]


    def get_used_functions(self):
        return self.possible_func+self.determined_func
    

    def set_used_functions(self, functions_map: dict):
        '''Parameter

functions_map : dict 
- A dict which maps the name of a function and its callback.'''
        lack_functions = set(self.determined_func) - set(functions_map.keys())
        if lack_functions:
            raise FuncMissingError(lack_functions)
        self.functions_map = functions_map
        self.determined_func = list(functions_map.keys())
        self.var_const_multi = list(set(self.possible_func) - set(self.determined_func) | set(self.var_const_multi))
        

    def format_expression(self): # e.g. 2ac(4b+d) -> 2*a*c*(4*b+d)
        if not hasattr(self, "functions_map"):
            raise MathFunctionError("Must set used functions first.")
        expression = self.expression
        multi_pack_prefix = "\^/"
        multi_pack_replace = []
        # e.g. xy^2ac -> [step 1] xy^(2ac) -> [step 2]: x*y**(2*a*c)
        for multi_pack in [i for i in self.var_const_multi if re.search(r"[{}]{}".format(multi_pack_prefix,i), expression)]: # [step 1.1] find "^2ac"
            index = 0
            while True:
                present_sep_expression = expression[index:]
                present_pack = re.search(r"[{}]{}".format(multi_pack_prefix, multi_pack), present_sep_expression)
                if not present_pack:
                    break
                present_pack = present_pack.group()
                index += present_sep_expression.index(present_pack)
                parenthesis = 0
                for index_search in range(index+len(present_pack), len(expression)):
                    if expression[index_search] in "+=*/" and parenthesis==0 or parenthesis ==-1:
                        break
                    if expression[index_search] == "(":
                        parenthesis += 1
                    elif expression[index_search] == ")":
                        parenthesis -= 1
                multi_pack_replace.append(expression[index:index_search])
                index += len(present_pack)
        for multi_pack in multi_pack_replace: # [step 1.2] "^2ac" -> "^(2ac)"
            expression = expression.replace(multi_pack, "{}({})".format(multi_pack[0], multi_pack[1:]))
        expression = expression.replace("^","**") # [step 2.1] "^" -> "**"
        for multi in self.var_const_multi: # [step 2.2] xy -> x*y; 2ac -> 2*a*c
            expression = expression.replace(multi, "*".join(multi))
            # ((?<![a-zA-Z0-9])[0-9]*[{}{}]*)\(
        expression = re.sub(r"((?<![a-zA-Z0-9])(?:(?:[0-9]*[{0}{1}]+)|(?:[0-9]+[{0}{1}]*)))\(".format(self.variables, self.constants), r"\1*(", expression) # [step 2.3] e.g. 2(a+c) -> 2*(a+c)
        expression = re.sub(r"([0-9]+)([a-zA-Z]+[0-9]*\()", r"\1*\2", expression)
        self.expression = expression
    

    def calc(self, *args, **kwargs):
        '''Parameters

*args : int | float
- Set the value of variable.

*kwargs : name of var or const = int | float
- Set the value of variable or constant by keyword argument, which has a higher priority than *args.'''
        variables_values = self.constants_map.copy()
        variables_values.update(kwargs)
        lack_var = [i for i in self.variables if i in set(self.variables)-set(kwargs.keys())]

        if len(args) > len(lack_var):
            raise VarBeyondError()
        elif len(args) < len(lack_var):
            raise VarMissingError(list(lack_var)[len(args):])
        elif (set(kwargs.keys()) - set(list(self.variables)+list(self.constants_map.keys()))):
            raise VarBeyondError()
        
        variables_values.update({i:k for i,k in zip(lack_var, args)})
        variables_values.update(self.functions_map)
        return eval(self.expression, {}, variables_values)