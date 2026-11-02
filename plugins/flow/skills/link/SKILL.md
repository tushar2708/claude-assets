---
name: link
description: Find a requested file location and return one clickable absolute path with its line number. Use only when explicitly invoked.
disable-model-invocation: true
---

# Link to Code

Find the file and exact line requested by the user. Return only one absolute-path link in the host’s native clickable format. When a `file:///ABSOLUTE_PATH:LINE` URI is supported, use it; otherwise return an absolute Markdown file link with the line number. Do not add explanation.
