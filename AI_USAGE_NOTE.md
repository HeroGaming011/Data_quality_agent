# AI Usage Note - AI Data Quality Agent

This document outlines the design principles, prompt engineering, data privacy measures, and best practices for using the **OpenRouter AI integration** in the **AI Data Quality Agent** project.

---

## 🔒 Privacy-First Architecture

A key architectural feature of this agent is its **privacy-conscious design**. The application does **not** upload your entire dataset to external AI servers. 

### What is sent to OpenRouter?
Only a minimal metadata footprint is sent:
1. **Rule Engine Logs**: Programmatic warnings (e.g. `• Row 3: Age is -5`).
2. **Column Attributes Summary**: Summary types and completeness percentages (e.g. `Age, Numeric (Integer), 100%`).
3. **Data Preview**: Only the **first 5 rows** (`df.head(5)`) of the CSV to establish structural context and header mapping.

> [!NOTE]
> By keeping the actual bulk of your data local and only sending structural diagnostics and sample records, the app preserves data confidentiality, remains highly secure, and minimizes API token consumption.

---

## 🧠 LLM Integration Specifications

- **Endpoint Provider**: OpenRouter (`https://openrouter.ai/api/v1`)
- **Default Model**: `nex-agi/nex-n2-pro:free`
- **Output Format**: Enforced JSON Object (`response_format={"type": "json_object"}`)

### Enforced JSON Schema
To guarantee reliable frontend rendering and prevent LLM parsing crashes, the model is instructed to output an object with exactly three keys:
```json
{
  "diagnosis": "A concise explanation of why the anomalies occurred and pattern analysis.",
  "suggestions": "Step-by-step guidance on how to fix these anomalies.",
  "cleanup_script": "A complete, ready-to-run Python script using Pandas."
}
```

---

## 💡 Best Practices & Cost Mitigation

1. **Free Tier Utilization**: The default model is `nex-agi/nex-n2-pro:free` which runs on OpenRouter's free tier, meaning zero API cost for validation.
2. **Rate Limits**: Free models on OpenRouter may be subject to stricter rate limiting. If you encounter timeout or queue errors, wait 10 seconds before uploading another file.
3. **Model Swap**: If you wish to migrate to a paid commercial model (e.g. `openai/gpt-4o-mini` or `anthropic/claude-3-haiku`), you can swap the model ID in `llm_helper.py` in line 82:
   ```python
   model="openai/gpt-4o-mini"
   ```

---

## ⚠️ Limitations & Disclaimers

- **Sample Bias**: Because the LLM only sees the first 5 rows, the generated python script relies on the programmatic validation engine's logs to know about errors occurring deep inside the dataset (e.g. row 500). If the local validator misses an anomaly, the LLM will not be aware of it unless it appears in the 5-row preview.
- **Code Execution Warning**: 
  > [!WARNING]
  > The python cleanup scripts generated in the "AI Suggestions" panel are written dynamically by AI. **Always inspect the code** before running it on production datasets or overriding your original CSV files.
