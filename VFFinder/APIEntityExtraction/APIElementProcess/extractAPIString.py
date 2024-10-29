

import javalang
import re
def extract_API_string_entity(api_entity:str):
    api_str = api_entity.source
    # 提取字符串和注释
    comment_pattern = re.compile(r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE)
    comments = comment_pattern.findall(api_str)

    # 使用javalang.tokenizer提取字符串
    tokens = list(javalang.tokenizer.tokenize(api_str))
    strings = [token.value.strip("\"") for token in tokens if isinstance(token, javalang.tokenizer.String)]

    string_literals = []
    for i in strings + comments:
        string_literals.extend(i.split(" "))
    return string_literals