# Semantic Shape Vocabulary

> 形狀即語意：LLM、Agent、Vector Store 等元件用固定形狀表達，讀者一眼辨認。
> 來源借鑑 fireworks-tech-graph (MIT)，已改寫對齊 dark-theme palette。

## 核心約定

| 元件 | 形狀 | 視覺訊號 |
|---|---|---|
| LLM / Model | 圓角矩形 + **雙邊框** | 「智慧節點」 |
| Agent / Orchestrator | **六邊形** | 決策者 |
| Vector Store / Database | 圓柱（頂底橢圓） | 持久化儲存 |
| Memory (short-term) | 圓角矩形 + **虛線邊框** | 非持久 |
| Tool / Function | 矩形 + ⚙ 圖示 | 可呼叫能力 |
| Queue / Stream | 水平管道 | 訊息流 |
| User / Actor | 頭+肩 stickfigure | 人類觸發 |
| Decision | 菱形 | 條件判斷 |
| API Gateway | 小六邊形 | 入口 |

搭配現有 dark palette（SKILL.md §Color Palette）：fill 用對應語意色的 `rgba(..., 0.4)`，stroke 用 `*-400` 色。

---

## LLM / Model Node（雙邊框圓角矩形）

```xml
<!-- 外框（實） -->
<rect x="x" y="y" width="w" height="h" rx="10"
      fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="2.5"/>
<!-- 內框（弱） -->
<rect x="x+3" y="y+3" width="w-6" height="h-6" rx="8"
      fill="none" stroke="#a78bfa" stroke-width="0.8" opacity="0.5"/>
<text x="cx" y="cy-4" text-anchor="middle" font-size="14">⚡</text>
<text x="cx" y="cy+12" text-anchor="middle" fill="white" font-size="12" font-weight="600">GPT-4o</text>
```

## Agent / Orchestrator（六邊形，r=36）

```xml
<polygon points="cx,cy-r  cx+r*0.866,cy-r*0.5  cx+r*0.866,cy+r*0.5  cx,cy+r  cx-r*0.866,cy+r*0.5  cx-r*0.866,cy-r*0.5"
         fill="rgba(6, 78, 59, 0.4)" stroke="#34d399" stroke-width="1.5"/>
<text x="cx" y="cy+5" text-anchor="middle" fill="white" font-size="12" font-weight="600">Agent</text>
```

## Vector Store / Database（圓柱 w=80, h=70）

```xml
<ellipse cx="cx" cy="top" rx="40" ry="12"
         fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1.5"/>
<rect x="cx-40" y="top" width="80" height="50" fill="rgba(76, 29, 149, 0.4)" stroke="none"/>
<line x1="cx-40" y1="top" x2="cx-40" y2="top+50" stroke="#a78bfa" stroke-width="1.5"/>
<line x1="cx+40" y1="top" x2="cx+40" y2="top+50" stroke="#a78bfa" stroke-width="1.5"/>
<!-- Vector Store 加內環 -->
<ellipse cx="cx" cy="top+17" rx="40" ry="12" fill="none" stroke="#a78bfa" stroke-width="0.7" opacity="0.5"/>
<ellipse cx="cx" cy="top+34" rx="40" ry="12" fill="none" stroke="#a78bfa" stroke-width="0.7" opacity="0.5"/>
<ellipse cx="cx" cy="top+50" rx="40" ry="12" fill="rgba(30, 41, 59, 0.6)" stroke="#a78bfa" stroke-width="1.5"/>
```

## Memory Node（虛線邊框）

```xml
<rect x="x" y="y" width="w" height="h" rx="8"
      fill="rgba(30, 41, 59, 0.5)" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="6,3"/>
<text x="cx" y="cy-6" text-anchor="middle" fill="#94a3b8" font-size="9" opacity="0.7" letter-spacing="0.05em">MEMORY</text>
<text x="cx" y="cy+10" text-anchor="middle" fill="white" font-size="12">Short-term</text>
```

## Tool / Function Call

```xml
<rect x="x" y="y" width="w" height="h" rx="6"
      fill="rgba(8, 51, 68, 0.4)" stroke="#22d3ee" stroke-width="1.5"/>
<text x="cx" y="cy-4" text-anchor="middle" font-size="16">⚙</text>
<text x="cx" y="cy+12" text-anchor="middle" fill="white" font-size="11">search_web</text>
```

## Queue / Stream（水平管道）

```xml
<ellipse cx="x1" cy="cy" rx="10" ry="16" fill="rgba(30, 41, 59, 0.6)" stroke="#fb923c" stroke-width="1.5"/>
<rect x="x1" y="cy-16" width="x2-x1" height="32" fill="rgba(251, 146, 60, 0.3)" stroke="none"/>
<line x1="x1" y1="cy-16" x2="x2" y2="cy-16" stroke="#fb923c" stroke-width="1.5"/>
<line x1="x1" y1="cy+16" x2="x2" y2="cy+16" stroke="#fb923c" stroke-width="1.5"/>
<ellipse cx="x2" cy="cy" rx="10" ry="16" fill="rgba(251, 146, 60, 0.3)" stroke="#fb923c" stroke-width="1.5"/>
```

## User / Actor

```xml
<circle cx="cx" cy="cy-18" r="10" fill="rgba(30, 41, 59, 0.5)" stroke="#94a3b8" stroke-width="1.2"/>
<path d="M cx-14,cy+16 Q cx-14,cy-4 cx,cy-4 Q cx+14,cy-4 cx+14,cy+16"
      fill="rgba(30, 41, 59, 0.5)" stroke="#94a3b8" stroke-width="1.2"/>
<text x="cx" y="cy+30" text-anchor="middle" fill="white" font-size="11">User</text>
```

## Decision Diamond

```xml
<polygon points="cx,cy-hh  cx+hw,cy  cx,cy+hh  cx-hw,cy"
         fill="rgba(120, 53, 15, 0.3)" stroke="#fbbf24" stroke-width="1.5"/>
<text x="cx" y="cy+5" text-anchor="middle" fill="white" font-size="11">Retry?</text>
```

## Swim Lane Container（分層背景）

```xml
<rect x="x" y="y" width="w" height="h" rx="6"
      fill="#1e293b" fill-opacity="0.15" stroke="#475569" stroke-width="1" stroke-dasharray="6,4"/>
<text x="x+12" y="y+16" fill="#94a3b8" font-size="10" font-weight="600" letter-spacing="0.08em">STORAGE LAYER</text>
```

---

## Semantic Arrow System（顏色+虛線編碼語意）

| 語意 | Stroke | Dash | Marker |
|---|---|---|---|
| Sync call (default) | `#64748b` | 無 | arrowhead |
| Async / Event | `#fb923c` | `stroke-dasharray="4,2"` | arrowhead |
| Auth / Security | `#fb7185` | `stroke-dasharray="4,4"` | arrowhead |
| Data write | `#34d399` | 無 | arrowhead-filled |
| Data read | `#22d3ee` | `stroke-dasharray="6,3"` | arrow-open |
| Control / Loop | `#fbbf24` | 無 | dot |

多個 marker 用 unique id：
```xml
<defs>
  <marker id="arrow-write" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#34d399"/>
  </marker>
  <marker id="arrow-read-open" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
    <path d="M 0 0 L 10 4 L 0 8" fill="none" stroke="#22d3ee" stroke-width="1.5"/>
  </marker>
</defs>
```
