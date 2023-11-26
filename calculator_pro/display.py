import re, json
from .constants import PLUGIN_NAME

class Display:

    def color_parenthesis(string: str, color_code: list = ["§6","§d","§9"], end_code = "§r"):
        color_code_available = [re.fullmatch(r"§\w",i).group() for i in color_code]
        if len(color_code_available) == len(color_code):
            color_code_available = "".join(color_code_available)
        else:
            raise AttributeError("color_code")
        color_index = 0
        color_code_num = len(color_code)
        pattern = re.compile(r"(?<!§[{0}])\(((?:(?:§[{0}][\(\)])|[^\(\)])+(?<!§[{0}]))\)".format(color_code_available))
        for i in range(10):
            parenthesis_match = pattern.search(string)
            if parenthesis_match:
                parenthesis_match = parenthesis_match.group()
                color = color_code[color_index]
                string = pattern.sub(r"{0}({1}\1{0}){1}".format(color, end_code), string)
                print(string)
            else:
                return string
            color_index = (color_index+1)%color_code_num

    def is_pairing_parenthesis(string):
        while True:
            if re.search(r"\([^\(\)]*\)", string):
                string = re.sub(r"\([^\(\)]*\)", "", string)
            else:
                break
        if re.search(r"[\(\)]", string):
            return False
        else:
            return True

TITLE = "§e§l[%s]§r "%PLUGIN_NAME

HELP_MSG = {
    "!!calc+": [
        {"text":"%s使用帮助\n"%TITLE},
        {"text":"!!calc+ add ","color":"gray", "clickEvent":{"action":"run_command", "value":"!!calc+ add"}},
        {"text":"添加自定义函数\n"},
        {"text":"!!calc+ remove ", "color":"gray", "clickEvent":{"action":"run_command", "value":"!!calc+ remove"}},
        {"text":"移除自定义函数\n"},
        {"text":"!!calc+ calc ", "color":"gray", "clickEvent":{"action":"runc_command","value":"!!calc+ calc"}},
        {"text":"进行函数计算\n"},
        {"text":"!!calc+ search ", "color":"gray", "clickEvent":{"action":"run_command", "value":"!!calc+ search"}},
        {"text":"查找函数\n"},
        {"text":"!!calc+ info ", "color":"gray", "clickEvent":{"action":"run_command","value":"!!calc+ info"}},
        {"text":"查看函数详细信息\n"},
        {"text":"!!calc+ save-all ", "color":"gray", "clickEvent":{"action":"run_command", "value":"!!calc+ save-all"}},
        {"text":"保存自定义函数的数据信息"}
    ],
    "add": '''%s§d添加自定义函数§r
§7!!calc+ add <expression> [description]§r
参数说明
§6§l<expression> §r函数表达式 [必填]
  简单 : §efunc(§7变量§e)§r=§7表达式§r
  完整 : §efunc(§7变量1§r, §7变量2§r, §7...§e)§r=§7表达式§r, \\§7常量1§r=§7数值§r, §7常量2§r=§7数值§r
    通过在§b表达式§r结束后用§b','§r分隔并添加§7'\\a=1,b=2,c=3...'§r以指定函数中使用的§b常量§r
    §7例 : height(t)=1/2*gt^2, \g=9.8§r
    注 : 常量已自动支持§b自然对数e§r, 暂不支持§b圆周率pi§r
  §e[命名]§r 函数名至少有§c2§r个字符, 不得以§c数字§r开头
         §b变量§r与§b常量§r名只能为§c单个英文字符§r
  §e[表达式]§r 表达式已支持§b省略输入§r, 如:
    §7`完整表达式` §8->§7 `省略输入`§r
    `2§2*§ra§2*§rc§2^§r(3§2*§rb)` §8->§r `2ac§2^§r3b`
    `5§2*§rlog10(3.1§2*§rx)` §8->§r `5log10(3.1x)`
  §e[函数]§r 表达式中可调用其他函数, 如§bsin§r, §bcos§r等§b默认函数§r或其他§b自定义函数§r
    §7例 : 计算根号2 `sqrt(2)`§r
    注 : §bsin(x)§r等§b三角函数§r中, §bx§r为§b弧度§r; 若要计算角度请输入§7sin(x/180*3.1415926)§r, 其中§bpi§r位数取决于所需计算精度
§6§l[description] §r函数表述 [选填]
  一串不包含空格的字符, 用以描述函数用途'''%TITLE,
    "remove": '''%s§d移除自定义函数§r
§7!!calc+ remove <func_name>§r
§6§l<func_name> §r函数名'''%TITLE,
    "calc": '''%s§d进行函数计算§r
§7!!calc+ calc <expression>§r
§6§l<expression> §r计算表达式
  简单 : §efunc(§7值1§r, §7值2§r)
  复杂 : §efunc(§7值1§r, §7变量2§r=§7值2§r, §7常量1§r=§7值3§r)
    通过使用§7`变量/常量名=值`§r以指定某一§b变量§r的值, 或临时地修改某一§b常量§r的值
    例 : 
      函数 §7height(t)=1/2*gt^2, \g=9.8§r
      计算 §7height(2, g=3.2)§r : 此时§bt=2§r, §bg§r修改为§b3.2§r
    注 : 被指定的变量的优先级高于未指定的变量, 若一个变量被指定, 未指定的数值将按照余下变量的顺序依次传入计算
      §7如函数func(x,y,z), func(1,2,y=3)等效于func(x=1,z=2,y=3)'''%TITLE,
    "search": '''%s§d查找函数§r
§7!!calc+ search <func_name>§r
§6§l<func_name> §r函数名
  在默认函数和自定义函数中查找可能相关的函数'''%TITLE,
    "info": '''%s§d查看函数详细信息§r
§7!!calc+ remove <func_name>
§6§l<func_name> §r函数名
  若函数是一个自定义函数, 则显示该函数的详细信息
  若函数是一个默认函数, 则显示该函数的描述'''%TITLE,
}