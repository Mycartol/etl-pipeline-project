# Content Change Summarization Module (LLM Summarizer)

A microservice for generating summaries of content changes using LLM (OpenAI or LLama2).

## Endpoint

`POST /summarize`

### Input
```json
{
    "content": "new or modified content"
}
```
