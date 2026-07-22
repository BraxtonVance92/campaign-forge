# CF-02 Phase 2 — model candidate ranking (real GMI account, 2026-07-22)

Source: real `GET https://api.gmi-serving.com/v1/models` call (see
`docs/verification/CF-02-experiment-receipt.md`), ~85 models. No model in
the list is explicitly labeled vision/multimodal/omni/video in its name --
including no Qwen-VL variant (only text-oriented `Qwen3.x` names are
present), so no Qwen candidate is selected; picking one would be a guess
with zero supporting evidence. Candidates below are ranked by native
multimodal reputation on each model family's own platform, request-shape
compatibility with this endpoint's already-OpenAI-shaped `messages`/
`content` array, likely relative cost, and suitability for a detailed
creator-analysis task.

1. **openai/gpt-4o-mini** -- OpenAI's cheapest natively multimodal model.
   OpenAI's own `image_url` content-block convention is exactly what this
   app already sends, so if GMI proxies faithfully, this is the most
   likely to work with zero shape changes. Tested first: cheapest
   plausible option.
2. **google/gemini-3.1-flash-lite-preview** -- Google's lightest/cheapest
   current Gemini tier; Gemini is natively multimodal on Google's own API.
   Tested second.
3. **openai/gpt-4o** -- same family as #1, full-size. Tested only if #1
   fails for a reason suggesting a per-model (not per-family) issue.
4. **google/gemini-3-flash-preview** -- same family as #2, non-lite.
   Tested only if #2 shows partial promise.
5. **anthropic/claude-haiku-4.5** -- Anthropic's cheap tier. Vision-capable
   on Anthropic's own API, but Anthropic's native content-block shape
   (`{"type": "image", "source": {"type": "base64", "media_type": ...,
   "data": ...}}`) differs from the OpenAI `image_url` shape already sent
   here -- a failure for this candidate may reflect shape mismatch rather
   than a true capability gap, and is reported as such if it occurs.

Probe design: one extracted frame (`frame_03.jpg`, 84,190 bytes, from the
same real authorized video, timestamp ~00:00:25) sent as a base64
`image_url` data URI, a short objectively-checkable prompt, `max_tokens`
capped low (150) to bound cost. Stop testing a candidate immediately on a
decisive unsupported-input response (e.g. another "no matching target
server" 404, or an explicit "does not support images" message).
