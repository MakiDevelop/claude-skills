---
name: generate-image
description: 使用 Gemini Nano Banana 2 產生圖片。當用戶說「產圖」「生成圖片」「generate image」「畫一張圖」時使用。
argument-hint: "[圖片描述 prompt，或留空進入互動模式]"
allowed-tools: Bash(python3*), Bash(echo*), Read, Write
author: Maki
version: "1.0.0"
tags: [image, gemini, ai]
required_env:
  - GEMINI_API_KEY
---

# Gemini Nano Banana 2 圖片生成

## 目標

透過 Google Gemini 最新圖像模型（Nano Banana 2）生成圖片，儲存到本機。

## 流程

### Step 0: 檢查 Gemini API Key

在做任何事之前，先確認用戶有 API Key。依序檢查：

```bash
python3 -c "
import os
key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or ''
if key:
    print('KEY_FOUND')
else:
    print('KEY_NOT_FOUND')
"
```

- **找到** → 繼續 Step 1
- **沒找到** → 告訴用戶：

```
找不到 Gemini API Key。請提供你的 API Key：

1. 到 https://aistudio.google.com/apikey 申請（免費）
2. 然後用以下任一方式提供：
   a) 直接貼給我（本次 session 有效）
   b) 加到 shell 環境：export GEMINI_API_KEY="your-key-here"
   c) 加到 .env 檔案：echo 'GEMINI_API_KEY=your-key-here' >> ~/.env
```

等用戶提供 key 後，用他給的值繼續。**不要在沒有 key 的情況下嘗試呼叫 API。**

### Step 1: 確認圖片需求

根據 `$ARGUMENTS` 判斷：

- **有 prompt** → 直接使用
- **空** → 詢問用戶想要什麼圖片，引導他描述：
  - 主題 / 場景
  - 風格（寫實、插畫、極簡、水彩...）
  - 色調偏好
  - 用途（blog feature image、social media、簡報...）

### Step 2: 優化 Prompt

將用戶描述優化為英文 prompt（Gemini 對英文 prompt 效果最好）。遵循原則：

- 具體描述構圖、光線、色調
- 指定風格關鍵字（e.g., minimalist, watercolor, isometric, flat design）
- 指定比例（16:9 for blog, 1:1 for social, 4:3 for presentation）
- 避免過於抽象的描述

**Prompt 範例：**
```
Clean modern tech blog illustration, 16:9 aspect ratio, minimalist style.
Visual metaphor for AI-powered knowledge management.
Cool blue and grey tones with warm orange accent colors.
Abstract geometric shapes representing data flow, no text, no human faces.
```

向用戶展示優化後的 prompt，確認後繼續。

### Step 3: 呼叫 Gemini API 生成圖片

```bash
python3 << 'PYEOF'
import json, os, sys, base64, urllib.request, urllib.error

# --- API Key ---
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "USER_PROVIDED_KEY_HERE"

# --- 設定 ---
PROMPT = """USER_PROMPT_HERE"""
OUTPUT_PATH = "/tmp/generated-image.png"
MODEL = "gemini-3.1-flash-image-preview"  # Gemini 圖像生成（穩定版）

# --- 呼叫 Gemini API ---
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

payload = {
    "contents": [{
        "parts": [{"text": PROMPT}]
    }],
    "generationConfig": {
        "responseModalities": ["TEXT", "IMAGE"]
    }
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"API Error {e.code}: {body}", file=sys.stderr)
    sys.exit(1)

# --- 從回應中提取圖片 ---
saved = False
for candidate in result.get("candidates", []):
    for part in candidate.get("content", {}).get("parts", []):
        if "inlineData" in part:
            img_data = base64.b64decode(part["inlineData"]["data"])
            mime = part["inlineData"].get("mimeType", "image/png")
            ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}.get(mime, ".png")
            out = OUTPUT_PATH.rsplit(".", 1)[0] + ext
            with open(out, "wb") as f:
                f.write(img_data)
            print(f"IMAGE_SAVED:{out} ({len(img_data)} bytes)")
            saved = True
            break
    if saved:
        break

if not saved:
    # 印出回應以便 debug
    print("No image in response. Full response:")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
    sys.exit(1)
PYEOF
```

**重要替換：**
- `USER_PROVIDED_KEY_HERE` → 用戶提供的 API Key（如果環境變數沒有的話）
- `USER_PROMPT_HERE` → Step 2 優化後的 prompt
- `OUTPUT_PATH` → 依用途調整檔名

### Step 4: 展示結果

圖片生成後：

1. 用 Read tool 讀取圖片檔案，展示給用戶看
2. 告知檔案位置和大小
3. 詢問是否滿意：
   - **滿意** → 詢問是否要搬到特定目錄
   - **不滿意** → 調整 prompt 重新生成（最多重試 2 次）

```
圖片已生成！

檔案：/tmp/generated-image.png
大小：{size}
Prompt：{prompt}

滿意嗎？如果要調整，告訴我哪裡需要修改。
```

### Step 5: 儲存到目標位置（可選）

如果用戶指定了儲存位置：

```bash
cp /tmp/generated-image.png "{TARGET_PATH}"
```

## 可用模型

| 模型 ID | 特性 |
|---------|------|
| `gemini-3.1-flash-image-preview`（預設） | 最新圖像生成，品質好 |
| `gemini-2.0-flash-preview-image-generation` | 備用（舊版） |

> 模型 ID 可能隨 Google 更新而變動。如果遇到 404 錯誤，請查閱
> https://ai.google.dev/gemini-api/docs/image-generation 確認最新模型 ID。

## 常見問題

### API 回應沒有圖片
- Gemini 有時會因為 safety filter 拒絕生成
- 調整 prompt 避免敏感內容，重新嘗試

### 403 / 401 錯誤
- API Key 無效或過期
- 確認 Key 有啟用 Generative Language API

### 429 Too Many Requests
- 免費額度用完，等一分鐘後重試
- 或升級為付費方案

## 注意事項

- Gemini 免費方案有每分鐘請求限制（通常 15 RPM）
- 生成的圖片版權歸用戶所有（依 Google ToS）
- 不要用來生成真人照片、有害內容、或侵權素材
- API Key 不會被記錄或儲存到任何檔案中
