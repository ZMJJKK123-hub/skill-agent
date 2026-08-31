# -*- coding: utf-8 -*-
"""一次性连通性自检：Coding Plan 端点 + GLM-5.3-Flash。"""
import os
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ["DSH_NO_ENV_FILE"] = "1"

from dotenv import load_dotenv
load_dotenv(".env")

import httpx
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url=os.environ["DSH_BASE_URL"],
    http_client=httpx.Client(trust_env=False, verify=False, timeout=120.0),
)
model = os.environ["DSH_MODEL"]
print("BASE_URL:", os.environ["DSH_BASE_URL"])
print("MODEL:", model)
r = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "回复两个字：连通"}],
    max_tokens=512,
)
print("REPLY:", (r.choices[0].message.content or "").strip())
print("USAGE:", r.usage)
print("CONNECTIVITY_OK")
