#!/usr/bin/env python3
"""Send a prompt, with file excerpts, to the local model and print its reply.

No dependencies: the standard library only. Bionic serves Qwen 2.5 Coder 14B on an
OpenAI-style API at http://localhost:1235/v1 (the default; LM Studio's own port is 1234,
override with --url or $LOCAL_LLM_URL). The reply is a draft: Claude checks it before
anything goes into the repository (CLAUDE.md, "Delegating to the local model").

    python tools/local_llm.py "Write a node:test scaffold for these functions" -f src/js/engine/survey/survey.js:1-80
    python tools/local_llm.py - -f docs/dev/canvas_v10_STATUS.md:4000-4300 < prompt.txt
    python tools/local_llm.py --list

A file argument is PATH or PATH:START-END (1-based, inclusive lines).
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

DEFAULT_URL = os.environ.get("LOCAL_LLM_URL", "http://localhost:1235/v1")
DEFAULT_MODEL = os.environ.get("LOCAL_LLM_MODEL", "qwen2.5-coder-14b-instruct")
DEFAULT_SYSTEM = (
    "You are a careful coding assistant for a zero-dependency browser CAD/BIM app. "
    "Answer only what is asked. Keep code ES5 unless told otherwise. "
    "Do not invent functions, files or APIs that are not in the excerpts; say when something is unknown."
)
RANGE = re.compile(r"^(.*):(\d+)-(\d+)$")


def read_excerpt(spec):
    m = RANGE.match(spec)
    path, start, end = (m.group(1), int(m.group(2)), int(m.group(3))) if m else (spec, None, None)
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    if start is not None:
        if start < 1 or end < start:
            raise ValueError("bad line range in %r" % spec)
        lines = lines[start - 1:end]
        label = "%s (lines %d-%d)" % (path, start, min(end, start - 1 + len(lines)))
    else:
        label = path
    return "--- %s ---\n%s\n--- end of %s ---" % (label, "\n".join(lines), path)


def request(url, payload=None, timeout=600):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_models(base):
    return [m.get("id") for m in request(base + "/models", timeout=10).get("data", [])]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompt", nargs="?", help="the prompt, or - to read it from stdin")
    ap.add_argument("-f", "--file", action="append", default=[], help="PATH or PATH:START-END; repeatable")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="model id (default %(default)s, or $LOCAL_LLM_MODEL)")
    ap.add_argument("--system", default=DEFAULT_SYSTEM, help="system prompt")
    ap.add_argument("--url", default=DEFAULT_URL, help="API base (default %(default)s, or $LOCAL_LLM_URL)")
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max-chars", type=int, default=40000,
                    help="refuse a request longer than this, to stay inside the model's context (default %(default)s)")
    ap.add_argument("--list", action="store_true", help="list the loaded models and exit")
    args = ap.parse_args()
    base = args.url.rstrip("/")

    try:
        if args.list:
            print("\n".join(list_models(base)) or "(no models loaded)")
            return 0
        if not args.prompt:
            ap.error("a prompt is required (or - for stdin)")
        prompt = sys.stdin.read() if args.prompt == "-" else args.prompt
        excerpts = [read_excerpt(s) for s in args.file]
        user = "\n\n".join(excerpts + [prompt]) if excerpts else prompt
        if len(user) + len(args.system) > args.max_chars:
            print("local_llm: request is %d chars, over --max-chars %d; send smaller excerpts"
                  % (len(user) + len(args.system), args.max_chars), file=sys.stderr)
            return 2
        model = args.model
        reply = request(base + "/chat/completions", {
            "model": model,
            "messages": [{"role": "system", "content": args.system}, {"role": "user", "content": user}],
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "stream": False,
        })
        choice = reply["choices"][0]
        sys.stdout.write(choice["message"]["content"].rstrip() + "\n")
        if choice.get("finish_reason") == "length":
            print("local_llm: reply cut at --max-tokens %d" % args.max_tokens, file=sys.stderr)
        return 0
    except urllib.error.HTTPError as e:
        print("local_llm: HTTP %d from %s: %s" % (e.code, base, e.read().decode("utf-8", "replace")[:500]),
              file=sys.stderr)
    except urllib.error.URLError as e:
        print("local_llm: cannot reach %s (%s); is Bionic's server running?" % (base, e.reason), file=sys.stderr)
    except (OSError, ValueError, KeyError) as e:
        print("local_llm: %s" % e, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
