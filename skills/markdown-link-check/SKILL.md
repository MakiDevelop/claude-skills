---
name: markdown-link-check
description: Check local Markdown links, images and heading anchors. Use for broken README links, Markdown link checks or 文件連結檢查.
argument-hint: "[Markdown file or documentation directory]"
allowed-tools: Read, Glob, Grep, Bash(python3*), Bash(rg *)
author: Maki
version: "1.0.0"
tags: [documentation, markdown, validation, developer]
required_env: []
required_bins: []
platforms: [macos, linux, windows]
safety_level: safe
---

# Check Markdown links

## Workflow

1. Establish the root and Markdown files to inspect; default to the supplied file,
   not the entire home directory. Read repository docs for the target renderer
   (GitHub, MkDocs, etc.). Do not follow symlinks outside the authorized root.
2. Use an available Markdown parser to collect inline links, image links and
   reference-style definitions/usages, excluding fenced/inline code and comments.
   If only regex/manual inspection is available, disclose limited coverage; regex
   alone is not a complete Markdown parser. Do not auto-install a parser.
3. Classify each target:
   - relative path: resolve against the containing Markdown file, percent-decode
     once and preserve case; strip query and fragment before filesystem checks;
   - same-document fragment: resolve against headings for the selected renderer;
   - cross-document fragment: verify target file and then its heading;
   - root-relative path: resolve only when the site root is known, otherwise mark
     unresolved; do not assume filesystem root or repository root;
   - http(s), mailto, data, custom schemes: record but do not contact externally.
4. Verify existence and file/directory type with read-only checks. Detect paths
   escaping the root before opening them. For anchors, respect duplicate headings,
   Unicode, punctuation, explicit IDs and renderer-specific slugging. If renderer
   behavior cannot be established, mark anchor unverified instead of broken.
5. Report a table: source path/line, target, status (valid/broken/unverified/skipped),
   reason and proposed minimal correction. Summarize checked vs skipped coverage.
6. If asked to fix, change only verified broken targets or missing reference
   definitions, preserve link labels and recheck. Do not create placeholder
   documents merely to make links pass.

## Examples

- README.md links to `docs/setup.md#configuration`: check the file and heading.
- `[guide][setup]` without a `[setup]: ...` definition: report missing reference.
- `[example](missing.md)` inside a code fence: skip as an example.
- A network URL is skipped in this local-only workflow; it is not declared valid.

## Quality Gates

- [ ] Links and images resolve relative to their source document.
- [ ] Code examples do not create false broken-link reports.
- [ ] Anchors are checked using the actual renderer, including duplicate headings.
- [ ] External and out-of-root targets are not fetched.
- [ ] Unsupported syntax/renderer behavior is unverified, never a silent pass.
- [ ] No source changes unless the user requested fixes.
