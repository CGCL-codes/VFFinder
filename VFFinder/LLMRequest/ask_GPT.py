

import openai
from CommonUtils.network_util import crawl_with_timeout_retry

openai.api_base = ""

api_key = ''

api_key_list = []

@crawl_with_timeout_retry(max_retries=2, init_delay=3, timeout=30)
def query_chat_gpt(message)->str:

    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model="gpt-3.5-trubo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    )

    # 解析并返回回复
    if 'choices' in response:
        return response['choices'][0]['message']['content']
    else:
        raise Exception('ChatGPT API请求失败: {}'.format(response))


@crawl_with_timeout_retry(max_retries=2, init_delay=3, timeout=20)
def query_chat_gpt_api_key(message, api_key)->str:
    openai.api_key = api_key


    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    )

    if 'choices' in response:
        return response['choices'][0]['message']['content']
    else:
        raise Exception('ChatGPT API请求失败: {}'.format(response))