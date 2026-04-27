import os
from openai import OpenAI

client = OpenAI(
    api_key="sk-7937004b940245358ba5885b06e2fc21",
    base_url="https://api.deepseek.com"
)

messages = [{"role": "system", "content": "你是一个实用助手"}]

print("DeepSeek V4 Pro 对话（输入 quit 退出）")
while True:
    user_input = input("\n你：")
    if user_input.lower() == "quit":
        break
    messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=messages,
        reasoning_effort="max",
        extra_body={"thinking": {"type": "enabled"}},
    )
    
    reply = response.choices[0].message.content
    print(f"V4：{reply}")
    messages.append({"role": "assistant", "content": reply})


