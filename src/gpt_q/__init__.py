from typing import List

import httpx


INSTRUCT_TEMPLATE = """{% if 'role' in messages[0] %}
 {% for message in messages %}
  {% if message['role'] == 'user' %}
    {{'<|im_start|>user' + message['content'] + '<|im_end|>'}}
  {% elif message['role'] == 'assistant'%}
    {{'<|im_start|>assistant' + message['content'] + '<|im_end|>' }}
  {% else %}
    {{ '<|im_start|>system' + message['content'] + '<|im_end|>' }}
  {% endif %}
 {% endfor %}
{% endif %}"""


class Gpt:
    def __init__(self, api_base: str, api_token: str = None, model: str = None):
        self.api_base = api_base
        self.api_token = api_token
        self.model = model

    def _send(self, data):
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers.update({"Authorization": f"Bearer {self.api_token}"})

        with httpx.Client(verify=False) as client:
            response = client.post(f"{self.api_base}/chat/completions", json=data, timeout=120, headers=headers)

        gpt_answer = response.json()['choices'][0]['message']['content']
        return gpt_answer

    def req(self, prompt, sys_prompt=None):
        data = {
            "messages": [
                {"role": "system", "content": sys_prompt or ""},
                {"role": "user", "content": prompt}
            ],
            "mode": "instruct",
            "min_p": 0.2,
            # "max_tokens": 50,
            "instruction_template_str": INSTRUCT_TEMPLATE,
        }
        return self._send(data)

