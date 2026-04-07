"""
Tool call utilities for OpenAI-compatible function calling.

Provides prompt-based emulation of tool calls by injecting tool definitions
into the system prompt and parsing structured responses.

Includes message pre-processing utilities inspired by 9router's toolCallHelper.js
and CLIProxyAPI's websocket tool call repair patterns.
"""

import json
import logging
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool call ID validation (pattern from 9router toolCallHelper.js)
# ---------------------------------------------------------------------------

_TOOL_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def _generate_tool_call_id() -> str:
    """Generate a valid tool call ID."""
    return f"call_{uuid.uuid4().hex[:24]}"


def _sanitize_tool_id(raw_id: str) -> Optional[str]:
    """Sanitize a tool call ID, returning None if unfixable."""
    if not raw_id:
        return None
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "", raw_id)
    if sanitized and len(sanitized) <= 64:
        return sanitized
    if sanitized:
        return sanitized[:64]
    return None


def ensure_tool_call_ids(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate and fix tool call IDs and argument types in-place.

    Ensures:
    - Every tool_call has a valid ``id`` field
    - Every tool_call has ``type`` = "function"
    - ``function.arguments`` is always a JSON *string*, not an object
    - Every tool message has a valid ``tool_call_id``

    Modeled after 9router's ``ensureToolCallIds()`` (toolCallHelper.js:18-63).
    """
    if not messages or not isinstance(messages, list):
        return messages

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "")

        # Fix assistant tool_calls
        if role == "assistant" and isinstance(msg.get("tool_calls"), list):
            for tc in msg["tool_calls"]:
                if not isinstance(tc, dict):
                    continue
                # Ensure valid ID
                tc_id = tc.get("id")
                if not tc_id or not _TOOL_ID_RE.match(str(tc_id)):
                    sanitized = _sanitize_tool_id(str(tc_id) if tc_id else "")
                    tc["id"] = sanitized or _generate_tool_call_id()
                # Ensure type
                if not tc.get("type"):
                    tc["type"] = "function"
                # Ensure arguments is JSON string
                func = tc.get("function")
                if isinstance(func, dict):
                    args = func.get("arguments")
                    if args is not None and not isinstance(args, str):
                        try:
                            func["arguments"] = json.dumps(args, ensure_ascii=False)
                        except (TypeError, ValueError):
                            func["arguments"] = str(args)

        # Fix tool message tool_call_id
        if role == "tool":
            tc_id = msg.get("tool_call_id")
            if tc_id and not _TOOL_ID_RE.match(str(tc_id)):
                sanitized = _sanitize_tool_id(str(tc_id))
                msg["tool_call_id"] = sanitized or _generate_tool_call_id()

    return messages


def fix_missing_tool_responses(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Insert empty tool results when assistant has tool_calls but next message lacks them.

    Prevents the model from seeing unresolved tool calls in multi-turn conversations.
    Modeled after 9router's ``fixMissingToolResponses()`` (toolCallHelper.js:111-143).
    """
    if not messages or not isinstance(messages, list):
        return messages

    new_messages: List[Dict[str, Any]] = []

    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            new_messages.append(msg)
            continue

        new_messages.append(msg)

        # Check if this assistant message has tool_calls
        if msg.get("role") != "assistant":
            continue
        tool_calls = msg.get("tool_calls")
        if not isinstance(tool_calls, list) or not tool_calls:
            continue

        # Collect expected tool_call IDs
        expected_ids = set()
        for tc in tool_calls:
            if isinstance(tc, dict) and tc.get("id"):
                expected_ids.add(tc["id"])
        if not expected_ids:
            continue

        # Check which IDs are satisfied by subsequent tool messages
        satisfied_ids = set()
        for j in range(i + 1, len(messages)):
            next_msg = messages[j]
            if not isinstance(next_msg, dict):
                continue
            if next_msg.get("role") == "tool" and next_msg.get("tool_call_id") in expected_ids:
                satisfied_ids.add(next_msg["tool_call_id"])
            elif next_msg.get("role") in ("user", "assistant"):
                # Stop looking once we hit the next turn
                break

        # Insert empty tool results for unsatisfied IDs
        missing_ids = expected_ids - satisfied_ids
        if missing_ids:
            logger.debug(f"Inserting {len(missing_ids)} empty tool responses for missing IDs")
            for tc in tool_calls:
                if isinstance(tc, dict) and tc.get("id") in missing_ids:
                    func = tc.get("function", {})
                    tool_name = func.get("name", "unknown") if isinstance(func, dict) else "unknown"
                    new_messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": tool_name,
                        "content": "",
                    })

    return new_messages


def build_tool_prompt(
    tools: List[Dict[str, Any]],
    tool_choice: Optional[Any] = None,
    parallel_tool_calls: bool = True,
) -> str:
    """Generate a system prompt block describing available tools.

    Uses adaptive truncation based on the number of tools:
    - <= 20 tools: full descriptions (300 chars) + full parameter schemas
    - 21-30 tools: shorter descriptions (200 chars) + full parameter schemas
    - > 30 tools: shorter descriptions (150 chars) + parameter schemas omitted

    Args:
        tools: List of OpenAI-format tool definitions.
        tool_choice: "auto", "required", "none", or {"type":"function","function":{"name":"..."}}.
        parallel_tool_calls: Whether multiple tool calls are allowed.

    Returns:
        System prompt string to prepend to the conversation.
    """
    if not tools:
        return ""

    # tool_choice="none" means don't mention tools at all
    if tool_choice == "none":
        return ""

    # Count actual function tools for adaptive truncation
    func_tools = [t for t in tools if t.get("type") == "function"]
    tool_count = len(func_tools)

    # Adaptive limits based on tool count
    if tool_count > 30:
        desc_limit = 150
        include_params = False
    elif tool_count > 20:
        desc_limit = 200
        include_params = True
    else:
        desc_limit = 300
        include_params = True

    lines = [
        "# TOOL CALLING INSTRUCTIONS",
        "",
        "You have access to external tools. When a user asks you to perform an action, you MUST call the appropriate tool.",
        "",
        "RULES:",
        "- Call tools IMMEDIATELY when an action is requested.",
        "- Do NOT say 'I will...' or describe what you plan to do. Just call the tool.",
        "- Do NOT use your internal tools (code_execution, web_search, browse_page, chatroom_send, search_images). They are disabled and will be filtered.",
        "- ONLY use the tools listed below.",
        "- Each tool call MUST be exactly once per action. Do NOT repeat the same tool call.",
        "",
    ]

    # Describe each tool
    lines.append("## Available Tools")
    lines.append("")
    for tool in func_tools:
        func = tool.get("function", {})
        name = func.get("name", "")
        desc = func.get("description", "")
        params = func.get("parameters", {})

        lines.append(f"### {name}")
        if desc:
            short_desc = desc[:desc_limit] + "..." if len(desc) > desc_limit else desc
            lines.append(f"{short_desc}")
        if include_params and params:
            lines.append(f"Parameters: {json.dumps(params, ensure_ascii=False)}")
        lines.append("")

    if not include_params and tool_count > 30:
        lines.append(f"*({tool_count} tools available — parameter schemas omitted for brevity. Infer parameters from tool names and descriptions.)*")
        lines.append("")

    lines.append("## Tool Call Format")
    lines.append("")
    lines.append("To call a tool, output this EXACT format (no code fences, no markdown):")
    lines.append("<tool_call>")
    lines.append('{"name": "tool_name", "arguments": {"param": "value"}}')
    lines.append("</tool_call>")
    lines.append("")
    lines.append("### Examples")
    lines.append('User: "create hello.py" →')
    lines.append("<tool_call>")
    lines.append('{"name": "write_file", "arguments": {"path": "hello.py", "content": "print(\'hello\')"}}')
    lines.append("</tool_call>")
    lines.append("")
    lines.append('User: "run ls -la" →')
    lines.append("<tool_call>")
    lines.append('{"name": "bash", "arguments": {"command": "ls -la"}}')
    lines.append("</tool_call>")
    lines.append("")
    lines.append("IMPORTANT: code_execution is NOT available. To run ANY command, you MUST use the bash tool with <tool_call> tags as shown above.")
    lines.append("")

    if parallel_tool_calls:
        lines.append("You may use multiple <tool_call> blocks in one response.")
        lines.append("")

    # Handle tool_choice directives
    if tool_choice == "required":
        lines.append("You MUST call at least one tool in your response.")
    elif isinstance(tool_choice, dict):
        func_info = tool_choice.get("function", {})
        forced_name = func_info.get("name", "")
        if forced_name:
            lines.append(f"You MUST call the '{forced_name}' tool.")
    else:
        # "auto" or default
        lines.append("Call tools when the user requests an action. After the tool result, you may provide a brief explanation.")

    return "\n".join(lines)


_TOOL_CALL_RE = re.compile(
    r"<tool_call>\s*(.*?)\s*</tool_call>",
    re.DOTALL,
)


def _strip_code_fences(text: str) -> str:
    if not text:
        return text
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _extract_json_object(text: str) -> str:
    if not text:
        return text
    start = text.find("{")
    if start == -1:
        return text
    end = text.rfind("}")
    if end == -1:
        return text[start:]
    if end < start:
        return text
    return text[start : end + 1]


def _remove_trailing_commas(text: str) -> str:
    if not text:
        return text
    return re.sub(r",\s*([}\]])", r"\1", text)


def _balance_braces(text: str) -> str:
    if not text:
        return text
    open_count = 0
    close_count = 0
    in_string = False
    escape = False
    for ch in text:
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            open_count += 1
        elif ch == "}":
            close_count += 1
    if open_count > close_count:
        text = text + ("}" * (open_count - close_count))
    return text


def _repair_json(text: str) -> Optional[Any]:
    if not text:
        return None
    cleaned = _strip_code_fences(text)
    cleaned = _extract_json_object(cleaned)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = cleaned.replace("\n", " ")
    cleaned = _remove_trailing_commas(cleaned)
    cleaned = _balance_braces(cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def parse_tool_call_block(
    raw_json: str,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    if not raw_json:
        return None
    parsed = None
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError:
        parsed = _repair_json(raw_json)
    if not isinstance(parsed, dict):
        return None

    name = parsed.get("name")
    arguments = parsed.get("arguments", {})
    if not name:
        return None

    valid_names = set()
    if tools:
        for tool in tools:
            func = tool.get("function", {})
            tool_name = func.get("name")
            if tool_name:
                valid_names.add(tool_name)
    if valid_names and name not in valid_names:
        return None

    if isinstance(arguments, dict):
        arguments_str = json.dumps(arguments, ensure_ascii=False)
    elif isinstance(arguments, str):
        arguments_str = arguments
    else:
        arguments_str = json.dumps(arguments, ensure_ascii=False)

    return {
        "id": f"call_{uuid.uuid4().hex[:24]}",
        "type": "function",
        "function": {"name": name, "arguments": arguments_str},
    }


def parse_tool_calls(
    content: str,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]]]:
    """Parse tool call blocks from model output.

    Detects ``<tool_call>...</tool_call>`` blocks, parses JSON from each block,
    and returns OpenAI-format tool call objects.

    Args:
        content: Raw model output text.
        tools: Optional list of tool definitions for name validation.

    Returns:
        Tuple of (text_content, tool_calls_list).
        - text_content: text outside <tool_call> blocks (None if empty).
        - tool_calls_list: list of OpenAI tool call dicts, or None if no calls found.
    """
    if not content:
        return content, None

    matches = list(_TOOL_CALL_RE.finditer(content))
    if not matches:
        return content, None

    tool_calls = []
    for match in matches:
        raw_json = match.group(1).strip()
        tool_call = parse_tool_call_block(raw_json, tools)
        if tool_call:
            tool_calls.append(tool_call)

    if not tool_calls:
        return content, None

    # Extract text outside of tool_call blocks
    text_parts = []
    last_end = 0
    for match in matches:
        before = content[last_end:match.start()]
        if before.strip():
            text_parts.append(before.strip())
        last_end = match.end()
    trailing = content[last_end:]
    if trailing.strip():
        text_parts.append(trailing.strip())

    text_content = "\n".join(text_parts) if text_parts else None

    return text_content, tool_calls


def format_tool_history(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert assistant messages with tool_calls and tool role messages into text format.

    Since Grok's web API only accepts a single message string, this converts
    tool-related messages back to a text representation for multi-turn conversations.

    Uses structured XML-like format that mirrors what the model produces:
    - Assistant tool calls: ``<tool_call>{"name":...,"arguments":...}</tool_call>``
    - Tool results: ``<tool_result name="..." call_id="...">content</tool_result>``

    This consistent format helps the model understand the conversation pattern
    and produce correct tool calls in subsequent turns.

    Args:
        messages: List of OpenAI-format messages that may contain tool_calls and tool roles.

    Returns:
        List of messages with tool content converted to text format.
    """
    result = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content")
        tool_calls = msg.get("tool_calls")
        tool_call_id = msg.get("tool_call_id")
        name = msg.get("name")

        if role == "assistant" and tool_calls:
            # Convert assistant tool_calls to XML text representation
            parts = []
            if content:
                parts.append(content if isinstance(content, str) else str(content))
            for tc in tool_calls:
                if not isinstance(tc, dict):
                    continue
                func = tc.get("function", {})
                if not isinstance(func, dict):
                    func = {}
                tc_name = func.get("name", "")
                tc_args = func.get("arguments", "{}")
                # Ensure arguments is valid JSON string for embedding
                if isinstance(tc_args, (dict, list)):
                    try:
                        tc_args = json.dumps(tc_args, ensure_ascii=False)
                    except (TypeError, ValueError):
                        tc_args = str(tc_args)
                elif not isinstance(tc_args, str):
                    tc_args = str(tc_args)
                # Build the tool_call block matching the model's expected format
                try:
                    tool_obj = json.loads(tc_args) if isinstance(tc_args, str) else tc_args
                    tool_json = json.dumps({"name": tc_name, "arguments": tool_obj}, ensure_ascii=False)
                except (json.JSONDecodeError, TypeError):
                    tool_json = f'{{"name":"{tc_name}","arguments":{tc_args}}}'
                parts.append(f"<tool_call>{tool_json}</tool_call>")
            result.append({
                "role": "assistant",
                "content": "\n".join(parts),
            })

        elif role == "tool":
            # Convert tool result to structured XML text format
            tool_name = name or "unknown"
            call_id = tool_call_id or ""
            if isinstance(content, str):
                content_str = content
            elif content is not None:
                try:
                    content_str = json.dumps(content, ensure_ascii=False)
                except (TypeError, ValueError):
                    content_str = str(content)
            else:
                content_str = ""
            # Use XML-like format that the model can parse and follow
            result.append({
                "role": "user",
                "content": f'<tool_result name="{tool_name}" call_id="{call_id}">\n{content_str}\n</tool_result>',
            })

        else:
            result.append(msg)

    return result


__all__ = [
    "build_tool_prompt",
    "parse_tool_calls",
    "format_tool_history",
    "parse_tool_call_block",
    "ensure_tool_call_ids",
    "fix_missing_tool_responses",
]
