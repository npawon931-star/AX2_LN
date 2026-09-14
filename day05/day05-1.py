from openai import OpenAI

#client = OpenAI(api_key="YOUR_API_KEY")
#response = client.chat.completions.create(
#   model="gpt-4o-mini",
#   messages=[
#        {"role":"system", "content":"You are a helpful assistant"},]
#)
#print(response.choices[0].message.content)

from openai import OpenAI

def ask_llm(api_key, model, question):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "친절한도우미"},
            {"role": "user", "content": question}, # 보통 질문은 user 역할로 전달하는 것이 좋습니다.
        ]
    )
    return response.choices[0].message.content, response.usage

my_api_key = "YOUR_API_KEY"

# 함수를 올바르게 호출하여 반환된 두 값을 각각 변수에 저장합니다.
answer, usage = ask_llm(my_api_key, "gpt-4o-mini", "안녕하세요. 오늘 날씨가 어떤가요?")

print("Answer:", answer)

