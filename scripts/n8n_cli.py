#!/usr/bin/env python3
"""
Small CLI helper for the n8n Public API.

Examples:
  N8N_BASE_URL=https://n8n.example.com N8N_API_KEY=... \\
    scripts/n8n_cli.py workflows list --limit 5 --summary
  scripts/n8n_cli.py workflows get 40SS8mGRTskhuOCs
  scripts/n8n_cli.py executions list --workflow-id 40SS8mGRTskhuOCs --summary
  scripts/n8n_cli.py executions retry 4672 --load-workflow
  scripts/n8n_cli.py webhook trigger --url https://n8n.example.com/webhook/my-hook \\
    --data '{"hello":"world"}'
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_TIMEOUT = 30


def die(message: str, code: int = 2) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError("Expected true/false")


def stringify_query_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def load_json_payload(raw: str | None, path: str | None) -> object | None:
    if raw and path:
        die("Provide only one of --data or --data-file.")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            die(f"Invalid JSON passed to --data: {exc}")
    if path:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            die(f"Data file not found: {path}")
        except json.JSONDecodeError as exc:
            die(f"Invalid JSON in {path}: {exc}")
    return None


def build_api_base(base_url: str) -> str:
    base_url = base_url.rstrip("/")
    if base_url.endswith("/api/v1"):
        return base_url
    return f"{base_url}/api/v1"


def request_json(
    method: str,
    url: str,
    headers: dict[str, str],
    payload: object | None,
    timeout: int,
) -> tuple[int, str, object | None, str]:
    data = None
    request_headers = dict(headers)
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    request_headers.setdefault("Accept", "application/json")

    req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            content_type = response.headers.get("Content-Type", "")
            parsed = None
            if "application/json" in content_type and body:
                parsed = json.loads(body)
            return response.status, body, parsed, content_type
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        content_type = exc.headers.get("Content-Type", "")
        return exc.code, body, None, content_type
    except urllib.error.URLError as exc:
        die(f"Request failed: {exc}")


def print_payload(body: str, parsed: object | None, raw: bool) -> None:
    if raw:
        if body:
            print(body)
        return
    if parsed is None:
        if body:
            print(body)
        return
    print(json.dumps(parsed, indent=2, ensure_ascii=True))


def print_workflow_summary(parsed: dict) -> None:
    data = parsed.get("data", [])
    for item in data:
        workflow_id = item.get("id", "")
        name = item.get("name", "")
        active = "active" if item.get("active") else "inactive"
        print(f"{workflow_id}\t{active}\t{name}")
    next_cursor = parsed.get("nextCursor")
    if next_cursor:
        print(f"nextCursor={next_cursor}")


def print_execution_summary(parsed: dict) -> None:
    data = parsed.get("data", [])
    for item in data:
        execution_id = item.get("id", "")
        status = item.get("status", "")
        workflow_id = item.get("workflowId", "")
        started_at = item.get("startedAt", "")
        print(f"{execution_id}\t{status}\t{workflow_id}\t{started_at}")
    next_cursor = parsed.get("nextCursor")
    if next_cursor:
        print(f"nextCursor={next_cursor}")


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--base-url",
        help="n8n base URL (e.g. https://n8n.example.com). Can also use N8N_BASE_URL.",
    )
    parser.add_argument(
        "--api-key",
        help="n8n API key. Can also use N8N_API_KEY.",
    )
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--raw", action="store_true", help="Print raw response body.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="n8n Public API helper")
    add_common_args(parser)
    subparsers = parser.add_subparsers(dest="resource", required=True)

    workflows = subparsers.add_parser("workflows", help="Manage workflows")
    workflows_sub = workflows.add_subparsers(dest="action", required=True)

    wf_list = workflows_sub.add_parser("list", help="List workflows")
    wf_list.add_argument("--active", type=parse_bool)
    wf_list.add_argument("--tags")
    wf_list.add_argument("--name")
    wf_list.add_argument("--project-id")
    wf_list.add_argument("--limit", type=int)
    wf_list.add_argument("--cursor")
    wf_list.add_argument("--summary", action="store_true")

    wf_get = workflows_sub.add_parser("get", help="Fetch workflow by id")
    wf_get.add_argument("id")

    wf_activate = workflows_sub.add_parser("activate", help="Activate workflow")
    wf_activate.add_argument("id")
    wf_activate.add_argument("--version-id")
    wf_activate.add_argument("--name")
    wf_activate.add_argument("--description")

    wf_deactivate = workflows_sub.add_parser("deactivate", help="Deactivate workflow")
    wf_deactivate.add_argument("id")

    executions = subparsers.add_parser("executions", help="Inspect executions")
    executions_sub = executions.add_subparsers(dest="action", required=True)

    exec_list = executions_sub.add_parser("list", help="List executions")
    exec_list.add_argument("--include-data", action="store_true")
    exec_list.add_argument("--status")
    exec_list.add_argument("--workflow-id")
    exec_list.add_argument("--project-id")
    exec_list.add_argument("--limit", type=int)
    exec_list.add_argument("--cursor")
    exec_list.add_argument("--summary", action="store_true")

    exec_get = executions_sub.add_parser("get", help="Fetch execution by id")
    exec_get.add_argument("id")
    exec_get.add_argument("--include-data", action="store_true")

    exec_retry = executions_sub.add_parser("retry", help="Retry execution by id")
    exec_retry.add_argument("id")
    exec_retry.add_argument("--load-workflow", action="store_true")

    webhook = subparsers.add_parser("webhook", help="Trigger webhook workflows")
    webhook_sub = webhook.add_subparsers(dest="action", required=True)

    webhook_trigger = webhook_sub.add_parser("trigger", help="Trigger a webhook URL")
    webhook_trigger.add_argument("--url")
    webhook_trigger.add_argument("--path")
    webhook_trigger.add_argument("--method", default="POST")
    webhook_trigger.add_argument("--data")
    webhook_trigger.add_argument("--data-file")
    webhook_trigger.add_argument(
        "--header",
        action="append",
        default=[],
        help="Extra header, e.g. 'Authorization: Bearer <token>'",
    )

    return parser


def require_api_key(api_key: str | None, resource: str) -> None:
    if not api_key:
        die(f"{resource} requires an API key. Set N8N_API_KEY or pass --api-key.")


def parse_headers(extra_headers: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for header in extra_headers:
        if ":" not in header:
            die(f"Invalid header format: {header}")
        key, value = header.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    base_url = args.base_url or os.environ.get("N8N_BASE_URL")
    api_key = args.api_key or os.environ.get("N8N_API_KEY")
    if not base_url and args.resource != "webhook":
        die("Set N8N_BASE_URL or pass --base-url.")
    if args.resource != "webhook":
        require_api_key(api_key, args.resource)

    timeout = args.timeout

    if args.resource == "webhook":
        if args.action != "trigger":
            die("Unsupported webhook action.")
        if not args.url and not args.path:
            die("Provide --url or --path.")
        if args.url and args.path:
            die("Provide only one of --url or --path.")
        if args.path:
            if not base_url:
                die("--path requires --base-url or N8N_BASE_URL.")
            path = args.path if args.path.startswith("/") else f"/{args.path}"
            url = f"{base_url.rstrip('/')}{path}"
        else:
            url = args.url
        payload = load_json_payload(args.data, args.data_file)
        headers = parse_headers(args.header)
        status, body, parsed, _ = request_json(
            args.method.upper(),
            url,
            headers=headers,
            payload=payload,
            timeout=timeout,
        )
        if status >= 400:
            die(f"HTTP {status} from webhook: {body}", code=1)
        print_payload(body, parsed, args.raw)
        return

    api_base = build_api_base(base_url)
    headers = {"X-N8N-API-KEY": api_key}

    if args.resource == "workflows":
        if args.action == "list":
            query = {
                "active": args.active,
                "tags": args.tags,
                "name": args.name,
                "projectId": args.project_id,
                "limit": args.limit,
                "cursor": args.cursor,
            }
            query = {k: stringify_query_value(v) for k, v in query.items() if v is not None}
            url = f"{api_base}/workflows"
            if query:
                url = f"{url}?{urllib.parse.urlencode(query)}"
            status, body, parsed, _ = request_json("GET", url, headers, None, timeout)
            if status >= 400:
                die(f"HTTP {status}: {body}", code=1)
            if args.summary and isinstance(parsed, dict):
                print_workflow_summary(parsed)
            else:
                print_payload(body, parsed, args.raw)
            return
        if args.action == "get":
            url = f"{api_base}/workflows/{args.id}"
            status, body, parsed, _ = request_json("GET", url, headers, None, timeout)
            if status >= 400:
                die(f"HTTP {status}: {body}", code=1)
            print_payload(body, parsed, args.raw)
            return
        if args.action == "activate":
            payload = {
                "versionId": args.version_id,
                "name": args.name,
                "description": args.description,
            }
            payload = {k: v for k, v in payload.items() if v is not None}
            url = f"{api_base}/workflows/{args.id}/activate"
            status, body, parsed, _ = request_json("POST", url, headers, payload, timeout)
            if status >= 400:
                die(f"HTTP {status}: {body}", code=1)
            print_payload(body, parsed, args.raw)
            return
        if args.action == "deactivate":
            url = f"{api_base}/workflows/{args.id}/deactivate"
            status, body, parsed, _ = request_json("POST", url, headers, None, timeout)
            if status >= 400:
                die(f"HTTP {status}: {body}", code=1)
            print_payload(body, parsed, args.raw)
            return

    if args.resource == "executions":
        if args.action == "list":
            query = {
                "includeData": True if args.include_data else None,
                "status": args.status,
                "workflowId": args.workflow_id,
                "projectId": args.project_id,
                "limit": args.limit,
                "cursor": args.cursor,
            }
            query = {k: stringify_query_value(v) for k, v in query.items() if v is not None}
            url = f"{api_base}/executions"
            if query:
                url = f"{url}?{urllib.parse.urlencode(query)}"
            status, body, parsed, _ = request_json("GET", url, headers, None, timeout)
            if status >= 400:
                die(f"HTTP {status}: {body}", code=1)
            if args.summary and isinstance(parsed, dict):
                print_execution_summary(parsed)
            else:
                print_payload(body, parsed, args.raw)
            return
        if args.action == "get":
            query = {}
            if args.include_data:
                query["includeData"] = "true"
            url = f"{api_base}/executions/{args.id}"
            if query:
                url = f"{url}?{urllib.parse.urlencode(query)}"
            status, body, parsed, _ = request_json("GET", url, headers, None, timeout)
            if status >= 400:
                die(f"HTTP {status}: {body}", code=1)
            print_payload(body, parsed, args.raw)
            return
        if args.action == "retry":
            payload = {"loadWorkflow": True} if args.load_workflow else None
            url = f"{api_base}/executions/{args.id}/retry"
            status, body, parsed, _ = request_json("POST", url, headers, payload, timeout)
            if status >= 400:
                die(f"HTTP {status}: {body}", code=1)
            print_payload(body, parsed, args.raw)
            return

    die("Unsupported command.")


if __name__ == "__main__":
    main()
