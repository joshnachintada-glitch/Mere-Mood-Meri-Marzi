import os
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

try:
    response = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("SUCCESS")
    print(response.choices[0].message.content)
except Exception as e:
    print("FAILED:", str(e))
