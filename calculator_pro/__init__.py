from .constants import DEFAULT_DATA, PLUGIN_NAME
from .math_function.manager import MathFunctionManager, MathFunctionSingleDict, MathFunction
from .math_function.exception import MathFunctionError
from .display import HELP_MSG
import os, json, importlib, difflib, re, copy
from typing import List, TypedDict
from mcdreforged.api.all import SimpleCommandBuilder, CommandSource, CommandContext, Text, PluginServerInterface


class FunctionData(TypedDict):

    default_functions: dict
    defined_functions: List[MathFunctionSingleDict]
    

class FunctionProxy():
     
    def __init__(self, server: PluginServerInterface) -> None:
        self.server = server
        self.title = "§e§l[%s]§r "%PLUGIN_NAME

        data: FunctionData = server.load_config_simple("data.json", DEFAULT_DATA)

        for pkg in data["default_functions"]:
            exec("{0}=importlib.import_module('{0}')".format(pkg), globals())

        self.manager = MathFunctionManager(data["defined_functions"], {func:eval("{}.{}".format(pkg, func), globals()) for pkg, funcs in data["default_functions"].items() for func in funcs.keys()})
        self.default_func_description = {key:value for i in data["default_functions"].values() for key, value in i.items()}
        self.data = data


    def add(self, source: CommandSource, context: CommandContext):
        if source.is_player:
            creator = source.player
        else:
            creator = "[Server]"
        try:
            result = self.manager.add_function(expression=context["expression"], creator=creator, description=context["description"])
            source.reply("%s§a添加成功§r: §b%s§f"%(self.title, result.name))
        except MathFunctionError as e:
            source.reply("§c%s"%e)
        except Exception as e:
            source.reply("§cUnexpected error: %s"%e)
            raise e
            
    
    def remove(self, source: CommandSource, context: CommandContext):
        try:
            result = self.manager.remove_function(context["func_name"])
            source.reply("%s§a移除成功§r: §b%s§f"%(self.title, result.name))
        except MathFunctionError as e:
            source.reply("§c%s"%e)
        except Exception as e:
            source.reply("§cUnexpected error: %s"%e)
            raise e
    

    def search(self, source: CommandSource, context: CommandContext):
        try:
            result = [i for i in list(self.manager.func_names_map.keys())+list(self.manager.default_functions.keys()) if difflib.SequenceMatcher(None, context["func_name"], i).quick_ratio() > 0.5]
            if not result:
                source.reply("§c无搜索结果")
                return
            source.reply("%s找到§b%s§f个相关函数: §e%s"%(self.title, len(result), ",§e".join(result)))
        except Exception as e:
            source.reply("§cUnexpected error: %s"%e)
            raise e
    

    def info(self, source: CommandSource, context: CommandContext):
        try:
            func = context["func_name"]
            if not self.manager.do_function_exist(func):
                source.reply("§c未知的函数")
                return
            if func in self.manager.default_functions.keys():
                source.reply("默认函数 §b%s\n - §f%s"%(func, self.default_func_description[func]))
            elif func in self.manager.func_names_map.keys():
                func : MathFunctionSingleDict = self.manager.math_functions[list(self.manager.func_names_map.keys()).index(func)]
                source.reply("\n§f".join([
                    self.title,
                    "函数详情 §b%s"%func["math_function"].name,
                    "§e[表达式] §f%s"%func["math_function"].expression,
                    "§e[常量值] §f%s"%(",".join(["%s=%s"%(i, k) for i,k in func["math_function"].constants_map.items()])),
                    "§e[创建] §f%s, %s"%(func["time"], func["creator"]),
                    "§e[描述] §f%s"%func["description"]
                ]))
        except Exception as e:
            source.reply("§cUnexpected error: %s"%e)
            raise e
    

    def calc(self, source: CommandSource, context: CommandContext):
        try:
            re_match = re.fullmatch("([\w]+)\(([\w,=/*+\-\^\. ]+)\)",context["expression"])
            if not re_match:
                source.reply("§c错误的计算表达式 !!calc+ calc 以查看计算帮助")
                return
            func, values = re_match.groups()
            self.server.logger.info(values)
            source.reply("%s=%s"%(func, eval("self.manager.get_function(func).__call__(%s)"%values)))
        except MathFunctionError as e:
            source.reply("§c%s"%e)
        except Exception as e:
            source.reply("§c计算出错: %s"%e)
            raise e
    

    def _save(self):
        self.data["defined_functions"] = self.manager.math_functions.copy()
        self.server.save_config_simple(json.loads(json.dumps(self.data, default=lambda obj: str(obj) if isinstance(obj, MathFunction) else obj)), "data.json")


    def saveall(self, source: CommandSource, context: CommandContext):
        try:
            self._save()
            source.reply("%s§a数据已保存"%self.title)
        except Exception as e:
            source.reply("§c数据保存失败: %s"%e)
            raise e

    def help_key(self, source: CommandSource, context: CommandContext, key: str):
        if key in HELP_MSG.keys():
            if key == "!!calc+":
                self.server.execute("tellraw %s %s"%(source.player, json.dumps(HELP_MSG[key])))
                return
            source.reply(HELP_MSG[key])
        else:
            source.reply("§e未知指令§r: §e!!calc+ §4%s<--"%key)
    

def on_load(server: PluginServerInterface, prev_module):
    global proxy
    proxy = FunctionProxy(server)
    builder = SimpleCommandBuilder()
    builder.arg("<expression>", Text)
    builder.arg("<description>", Text)
    builder.arg("<func_name>", Text)
    builder.command("!!calc+", lambda source, context :proxy.help_key(source, context, key="!!calc+"))
    builder.command("!!calc+ add", lambda source, context :proxy.help_key(source, context, key="add"))
    builder.command("!!calc+ add <expression>", proxy.add)
    builder.command("!!calc+ add <expression> <description>", proxy.add)
    builder.command("!!calc+ remove", lambda source, context :proxy.help_key(source, context, key="remove"))
    builder.command("!!calc+ remove <func_name>", proxy.remove)
    builder.command("!!calc+ calc", lambda source, context :proxy.help_key(source, context, key="calc"))
    builder.command("!!calc+ calc <expression>", proxy.calc)
    builder.command("!!calc+ info", lambda source, context :proxy.help_key(source, context, key="info"))
    builder.command("!!calc+ info <func_name>", proxy.info)
    builder.command("!!calc+ search", lambda source, context :proxy.help_key(source, context, key="search"))
    builder.command("!!calc+ search <func_name>", proxy.search)
    builder.command("!!calc+ save-all", proxy.saveall)
    builder.register(server)
    server.register_help_message("!!calc+","支持函数的计算器pro")

def on_unload(server: PluginServerInterface):
    proxy._save()