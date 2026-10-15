---
name: generate-image
description: Generate an image with the Gemini API. Use for image generation, illustrations, or 產圖 requests.
argument-hint: "[image description]"
allowed-tools: Bash(python3*), Read, Write
author: Maki
version: "1.1.0"
tags: [image, gemini, ai]
required_env: [GEMINI_API_KEY]
required_bins: [python3]
platforms: [macos, linux, windows]
safety_level: cautious
---

# Generate an image

Generate an image from the user's brief and save it locally. This uses Google's
external API: the prompt leaves the device and usage may be billed.

## Workflow

1. Take the subject, style, intended use and any requested text from the request.
   Ask only for missing details that materially affect the result. Preserve the
   user's language and requested text; do not claim English always works better.
2. Check whether `GEMINI_API_KEY` or the alias `GOOGLE_API_KEY` is present
   without printing its value. If absent, direct the user to configure an
   environment variable privately. Never ask them to paste a key into chat or
   write it into source, shell history, a prompt file or a URL.
3. Save the final prompt to a UTF-8 text file. Treat it as data, never interpolate
   it into Python or shell source. Use a new output basename for every request.
4. Resolve `scripts/generate.py` relative to this skill's directory, then run:

   ```bash
   python3 "/absolute/path/to/generate-image/scripts/generate.py" --prompt-file "/absolute/path/to/prompt.txt" --output "/absolute/path/to/result"
   ```

   The script defaults to `gemini-nano-banana-2.1`, verified in Google's model
   lifecycle table on 2026-10-15. `GEMINI_IMAGE_MODEL` can override it.
   Model availability and pricing may change; do not silently fall back.
5. Inspect and display the saved image. Report the actual output path and model.
   Report a refusal or missing image as a failure, never as a saved image.
6. Revise only when requested. Stop after two failed attempts at the same error.
   For 401/403, check account/key permissions; for 404, verify the model; for 429,
   inspect quota/billing rather than assuming a free tier or a fixed wait.

## Quality Gates

- [ ] Prompt and output path are passed as data; no credentials in chat or files.
- [ ] Existing files are never overwritten.
- [ ] The actual MIME type determines the output extension.
- [ ] Image is inspected before claiming success.
- [ ] No promise of free usage, fixed rate limits, or blanket copyright ownership.

## References

- https://ai.google.dev/gemini-api/docs/image-generation
- https://ai.google.dev/gemini-api/docs/deprecations
- https://ai.google.dev/gemini-api/docs/pricing
