from .exception import *
from .math_function import MathFunction
from typing import Callable, TypedDict, List
import datetime


class MathFunctionSingleDict(TypedDict):

    math_function: MathFunction
    creator: str
    time: str
    description: str


class MathFunctionManager:


    _singleton = None
    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            cls._singleton = object.__new__(cls)
        return cls._singleton


    def __init__(self, math_functions: List[MathFunctionSingleDict], default_functions: dict) -> None:
        self.math_functions: List[MathFunctionSingleDict] = math_functions
        self.default_functions = default_functions
        for i in self.math_functions:
            i["math_function"] = MathFunction(i["math_function"])
        self.func_names_map = {i["math_function"].name:i["math_function"] for i in math_functions}
        for i in self.math_functions:
            self.set_function_available(i["math_function"])
    

    def add_function(self, expression, creator, description="") -> MathFunction:
        math_function = MathFunction(expression)
        if math_function.name in self.func_names_map.keys() or math_function.name in self.default_functions.keys():
            raise FuncSameNameError(math_function.name)
        self.set_function_available(math_function)
        self.math_functions.append({
            "math_function": math_function,
            "creator": creator,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": description
        })
        self.func_names_map[math_function.name] = math_function
        return math_function
    

    def remove_function(self, func_name):
        if func_name in self.func_names_map.keys():
            flag = [k for i,k in self.func_names_map.items() if func_name in k.determined_func]
            if not flag:
                self.math_functions.remove(self.math_functions[list(self.func_names_map.keys()).index(func_name)])
                flag = self.func_names_map[func_name]
                self.func_names_map.pop(func_name)
                return flag
            else:
                if len(flag) > 1:
                    raise FuncRemoveError("There are still some functions that depend on `{}`: `{}`, and you should remove them in advance.".format(func_name, "`,`".join(flag)))
                else:
                    raise FuncRemoveError("There is still a function that depends on `{}`: `{}`, and you should remove it in advance.".format(func_name, flag[0]))
        elif func_name in self.default_functions.keys():
            raise FuncRemoveError("The default function is not allowed to be removed.")
        else:
            raise FuncRemoveError("There is no function named `{}`.".format(func_name))

    

    def set_function_available(self, math_function: MathFunction):
        "Set used functions and format expression for a MathFunction object to make it available to calculate."
        math_function.set_used_functions({used_func:self.get_function(used_func) for used_func in math_function.get_used_functions() if self.do_function_exist(used_func)})
        math_function.format_expression()


    def do_function_exist(self, func_name: str):
        return func_name in self.default_functions.keys() or func_name in self.func_names_map.keys()
    

    def get_function(self, func_name: str) -> Callable | Exception:
        if func_name in self.default_functions.keys():
            return self.default_functions[func_name]
        return self.func_names_map[func_name]
    


