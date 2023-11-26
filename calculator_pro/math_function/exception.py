class MathFunctionError(Exception):
    ...

class MathExpressionError(MathFunctionError):

    def __init__(self, expression) -> None:
        self.expression = expression
        # super().__init__("Wrong format expression: `{}`".format(expression))
        super().__init__("表达式格式错误: `{}`".format(expression))

class SameVarConstError(MathFunctionError):

    def __init__(self, same_var_const) -> None:
        self.same_var_const = same_var_const
        # super().__init__("A variable cannot be a constant at the same time, but `{}`".format("`,`".join(same_var_const)))
        super().__init__("一个变量不能同时是一个常量, 在 `{}`".format("`,`".join(same_var_const)))

class VarMissingError(MathFunctionError):

    def __init__(self, missing_var) -> None:
        self.missing_var = missing_var
        # super().__init__("Variable missing: `{}`".format("`,`".join(missing_var)))
        super().__init__("变量缺失: `{}`".format("`,`".join(missing_var)))

class VarBeyondError(MathFunctionError):

    def __init__(self) -> None:
        # super().__init__("Too many variables.")
        super().__init__("输入变量数超出函数定义的变量数")

class FuncMissingError(MathFunctionError):

    def __init__(self, missing_func) -> None:
        self.missing_func = missing_func
        # super().__init__("Missing function `{}`".format("`,`".join(missing_func)))
        super().__init__("缺少依赖函数: `{}`".format("`,`".join(missing_func)))

class FuncConstMissingError(MathFunctionError):

    def __init__(self, missing_func, missing_const) -> None:
        self.missing_func, self.missing_const = missing_func, missing_const
        # super().__init__("Missing function `{}` or constant `{}`".format("`,`".join(missing_func), "`,`".join(missing_const)))
        super().__init__("函数 `{}` 或常量 `{}` 缺失".format("`,`".join(missing_func), "`,`".join(missing_const)))

class FuncSameNameError(MathFunctionError):

    def __init__(self, func_name: str) -> None:
        # super().__init__("Cannot add a function with the same name `{}`.".format(func_name))
        super().__init__("已存在相同名称的函数 `{}`.".format(func_name))

class FuncOrMultiWrongError(MathFunctionError):

    def __init__(self, wrong_func_or_multi) -> None:
        self.wrong_func_or_multi = wrong_func_or_multi
        # super().__init__("Unrecognized function or multiplication: `{}`".format("`,`".join(wrong_func_or_multi)))
        super().__init__("无法识别的函数或变量相乘: `{}`".format("`,`".join(wrong_func_or_multi)))

class FuncRemoveError(MathFunctionError):

    pass