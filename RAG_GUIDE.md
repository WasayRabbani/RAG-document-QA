# RAG Configuration Guide: Chunking & Retrieval

This guide provides recommended settings for different types of documents to optimize your RAG pipeline's accuracy and context.

| Document Type | Chunk Size | Overlap | K (Retrieval) | Reasoning |
| :--- | :--- | :--- | :--- | :--- |
| **Educational/Textbooks** | 1000 - 1200 | 200 | 5 - 8 | Paragraphs are structured; requires enough context to keep lists and related concepts (like your Psychology PDF) together. |
| **Legal/Contracts** | 500 - 700 | 100 - 150 | 10+ | Legal language is dense. Smaller chunks prevent mixing different clauses. Higher K is needed to find all related "fine print." |
| **Technical Docs/Code** | 400 - 600 | 50 - 100 | 5 - 10 | Functions and documentation are usually short. Large chunks mix unrelated code logic. |
| **News Articles/Blogs** | 800 - 1000 | 100 | 3 - 5 | Typically focused on a single story. A few chunks usually capture the entire relevant section. |
| **Novels/Narratives** | 2000+ | 300 - 500 | 3 - 5 | Stories rely on long-form context and "scene" descriptions. Small chunks break the flow and confuse the AI. |

## Key Concepts to Remember:

### 1. Chunk Size (The "Window")
- **Large Chunks:** Better for "Theme" or "Summary" questions. Harder for specific fact-finding.
- **Small Chunks:** Better for "Exact Fact" or "Short Answer" questions. Risk losing the "Big Picture."

### 2. Chunk Overlap (The "Glue")
- Always aim for **15% - 20%** of your chunk size.
- If your chunks are 1000, use 200. If they are 500, use 100.
- **Why?** It prevents the "Sentence Cut-off" problem where a key name or date is split across two chunks.

### 3. K-Value (The "Breadth")
- **High K (8-12):** Use when the answer might be scattered across different pages (e.g., "Compare X and Y").
- **Low K (3-5):** Use when the answer is likely in one specific paragraph (e.g., "When was X born?").

## How to implement "Dynamic" Settings:
In the future, you can allow the user to select the "Document Type" and automatically pass these variables to your `TextChunker` and `QueryHandler` classes!
