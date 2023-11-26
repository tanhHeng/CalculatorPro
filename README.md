# CalculatorPro
MCDR插件，可在游戏内自定义函数并进行计算，支持numpy常用数学函数

**[!] 需要numpy支持**

若启动MCDR时未安装numpy, 则可能需要重启MCDR以应用环境

`pip3 install numpy scipy matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple`

---

## 指令

`!!calc+` 查看使用帮助

`!!calc+ add <expression> [description]` 添加自定义函数

`!!calc+ remove <func_name>` 移除自定义函数

`!!calc+ calc <expression>` 进行函数计算

`!!calc+ search <func_name>` 查找函数

`!!calc+ info <func_name>` 查看函数详情

`!!calc+ save-all` 手动保存自定义函数的数据信息 *(插件会在被卸载时自动保存)*

## 参数

*完整的指令帮助请在游戏内输入对应指令(不输入参数)以查看*

### !!calc+ add

`<expression>` 函数表达式, 必填

简单 ： `func(var)=expression`

完整 :  `func(var1, var2, ...) = expression, \const1=value1, const2=value2`

- 通过在表达式结束后用`,`分隔并添加`\a=1,b=2,c=3...`以指定函数中使用的常量
- 常量已自动支持`自然对数e`, 暂不支持`圆周率pi`
- 表达式支持简写省略符号, 如 `2ac^3b` `5log10(3.1x)`
- 表达式中可调用其他函数
- `sin(x)` 等三角函数中, `x`为弧度; 计算角度请输入`sin(x/180*3.1415926)`, 其中`pi`位数取决于所需计算精度

`<description>` 函数描述, 选填

### !!calc+ remove/search/info

`<func_name>` 函数名, 必填

### !!calc+ calc

`<expression>` 计算表达式, 必填

简单 :  `func(value)`

复杂 :  `func(value1, var2=value2, const1=value3)`

- 通过使用`var/const=value`以指定某一变量的值, 或临时地修改某一常量的值
- 被指定的变量的优先级高于未指定的变量, 若一个变量被指定, 未指定的数值将按照余下变量的顺序依次传入计算, 例如: `func(x,y,z), func(1,2,y=3)`等效于`func(x=1,z=2,y=3)`

## Data.json

默认函数与自定义函数的数据默认存储在`config/calculator_pro/data.json`

你可以通过修改这一文件来增加/删除默认函数

### 说明

```
{
    "default_functions": {  // 默认函数
        "numpy": {  // 引用的库
            "sin": "正弦函数, element-wise.",  // 引用的函数及对应描述
            // ...
        },
        "other_module": {
            // ...
        }
    },
    "defined_functions": [
        {
            "math_function": "expression",
            "creator": "player",
            "time": "%Y-%m-%d %H:%M:%S",
            "description": "description"
        },
        {
            // ...
        }
    ]
}
