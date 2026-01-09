from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("AZURE_AI_KEY"),
    base_url=os.getenv("AZURE_AI_ENDPOINT")
)

response = client.chat.completions.create(
    model=os.getenv("AZURE_AI_MODEL"),
    messages=[{"role": "user", "content": "Hello"}]
)

print(response.choices[0].message.content)
