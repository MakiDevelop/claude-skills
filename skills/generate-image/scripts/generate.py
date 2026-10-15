#!/usr/bin/env python3
"""Generate one Gemini image; credentials only from environment."""
import argparse
import base64
import binascii
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

DEFAULT_MODEL = "gemini-nano-banana-2.1"
EXTENSIONS = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


def first_image(result):
    if not isinstance(result, dict) or not isinstance(result.get("candidates", []), list):
        raise ValueError("Invalid provider response")
    for candidate in result.get("candidates", []):
        if not isinstance(candidate, dict) or not isinstance(candidate.get("content", {}), dict):
            continue
        for part in candidate.get("content", {}).get("parts", []):
            if not isinstance(part, dict):
                continue
            inline = part.get("inlineData")
            if not inline:
                continue
            mime = inline.get("mimeType")
            if mime not in EXTENSIONS:
                raise ValueError("Unsupported image MIME type")
            data = base64.b64decode(inline["data"], validate=True)
            if not data:
                raise ValueError("Empty image")
            return data, EXTENSIONS[mime]
    raise ValueError("No image returned; inspect the prompt or provider safety response")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="Output basename")
    args = parser.parse_args()
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        parser.error("Configure GEMINI_API_KEY privately in your environment")
    model = os.environ.get("GEMINI_IMAGE_MODEL", DEFAULT_MODEL)
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", model):
        parser.error("Invalid model identifier")
    try:
        prompt = args.prompt_file.read_text(encoding="utf-8")
        if not prompt.strip():
            raise ValueError("Prompt must not be empty")
        # Check every supported output suffix before making a potentially paid call.
        if any(Path(str(args.output) + ext).exists() for ext in EXTENSIONS.values()):
            raise ValueError("Output exists; choose a new basename")
        payload = {"contents": [{"parts": [{"text": prompt}]}],
                   "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}}
        request = urllib.request.Request(
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + model + ":generateContent",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": key},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
        data, extension = first_image(result)
        output = Path(str(args.output) + extension)
        with output.open("xb") as handle:
            handle.write(data)
        print(json.dumps({"path": str(output.resolve()), "bytes": len(data),
                          "model": model}, ensure_ascii=False))
    except urllib.error.HTTPError as exc:
        # Provider payloads may echo input. Do not dump them or request headers.
        print("Gemini HTTP " + str(exc.code) + "; check model, access, billing or quota",
              file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, binascii.Error) as exc:
        # Avoid rendering arbitrary provider error bodies or local input contents.
        print("Generation failed (" + type(exc).__name__ + "); no success claimed",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
