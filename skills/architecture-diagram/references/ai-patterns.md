# AI / Agent Domain Pattern Presets

> 常見 AI/Agent 架構的 swim-lane + 節點配置範本。寫 blog 時當 starter recipe 用。
> 借鑑 fireworks-tech-graph AI 領域知識，對齊 Maki 的七位一體 / 記憶大廳語境。

## Pattern 1: RAG (Retrieval-Augmented Generation)

**Swim lanes**：Input → Retrieval → Generation → Output

**節點**：
- User (Actor)
- Query Embedder (Tool)
- Vector Store (Cylinder with rings, e.g. pgvector / Qdrant)
- Retrieved Chunks (Document icon × N)
- LLM (Double-border rect, e.g. Claude)
- Grounded Answer (Document)

**Arrow semantics**：
- User → Embedder：sync call (`#64748b`)
- Embedder → Vector Store：data read (`#22d3ee` dashed)
- Vector Store → LLM：context injection (`#34d399`)
- LLM → Answer：generate (sync, thick)

---

## Pattern 2: Mem0-style Memory Architecture

**Swim lanes**：Input → Memory Manager → Storage → Retrieval/Output

**節點**：
- AI App / Agent (Hexagon)
- mem0 Client (Tool)
- Memory Manager (Hexagon)
- Vector Store + Graph DB + Key-Value Store + History Store（平行 4 個 cylinder）
- Context Builder (Tool)
- LLM (Double-border rect)
- Personalized Response (Document)

**關鍵表達**：Memory Manager 用 `write` 綠色箭頭分流到四種 store；`read` 青色虛線從四種 store 聚合到 Context Builder。

---

## Pattern 3: Multi-Agent Collaboration

**Swim lanes**：Mission Control → Specialist Agents → Synthesis

**節點**：
- User Brief (Document)
- Coordinator Agent (Hexagon，大 r=44)
- Research Agent + Coding Agent + Review Agent（平行三個 hexagon）
- Shared Memory (Memory node，虛線框)
- Synthesis Engine (Tool)
- Final Response (Document)

**Arrow semantics**：
- Coordinator → 三 agents：delegation (`#fbbf24` + dot marker)
- 三 agents ↔ Shared Memory：read+write 雙向
- 三 agents → Synthesis：aggregate

---

## Pattern 4: Tool Call Flow

**Swim lanes**：User → Agent → Tool → Result

**節點**：
- User (Actor)
- Agent (Hexagon)
- LLM (Double-border rect)
- Tool 1 / Tool 2 / Tool N（平行 Tool boxes，可用 brand icon 如 Brave / GitHub）
- External API (API Gateway hexagon)
- Grounded Answer

**關鍵表達**：LLM → Tool 用 control arrow (`#fbbf24`)，Tool → LLM 回 data 用 read arrow。

---

## Pattern 5: Agentic Search

類似 RAG 但加入 **loop**：

- Agent 判斷是否需要更多 context（Decision diamond）
- Yes → 再次 embed + retrieve
- No → 給 LLM 生成

Decision diamond 用 `#fbbf24` 橘黃色，loop 箭頭用 control 語意。

---

## 應用建議

當使用者要求畫 AI 架構時，Claude 應：
1. 先判斷最接近哪一個 pattern（若完全對上則用 preset）
2. 若是混合型，拼接多個 pattern 的 swim lane
3. 使用 `brand-colors.json` 查產品實際品牌色，避免瞎配
4. 使用 `semantic-shapes.md` 的形狀約定，保持 LLM=雙框 / Agent=六邊形 / Memory=虛線 的一致性
