from __future__ import annotations
# Copyright (c) Lineaje, Inc. All rights reserved.
# Lineaje UnifAI guardrail  version=2.0.0-alpha
def _lineaje_load_gr_client():
    """Lineaje-added: load gr_stub_client.py (missing / broken: a pass-through client)."""
    import sys, importlib.util as u, pathlib
    n = "_lineaje_gr_stub_client"
    if n in sys.modules: return sys.modules[n]
    try:
        h = pathlib.Path(__file__).resolve().parent
        s = u.spec_from_file_location(n, next(p for p in (d / "gr_stub_client.py" for d in [h, *h.parents][:8]) if p.is_file()))
        m = sys.modules[n] = u.module_from_spec(s); s.loader.exec_module(m); return m
    except Exception:
        sys.modules.pop(n, None); return __import__('types').SimpleNamespace(STUB_API=999999, GuardrailUnavailableError=type('GuardrailUnavailableError', (PermissionError,), {}), SiteDescriptor=lambda *a, **k: None, new_interaction_id=lambda *a, **k: None, enforce=lambda _s, _p, *a, **k: _p, enforce_request=lambda _s, _p, *a, **k: _p, enforce_reply=lambda _s, _p, *a, **k: _p)


from datetime import datetime
from pprint import pformat
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, SystemMessage, ToolMessage

import config


COLORS = {
    "blue": "\033[94m",
    "cyan": "\033[96m",
    "green": "\033[92m",
    "magenta": "\033[95m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "dim": "\033[2m",
    "reset": "\033[0m",
}


def _enabled() -> bool:
    return bool(getattr(config, "EXECUTION_LOGGING_ENABLED", True))


def _color(text: str, color: str) -> str:
    if not getattr(config, "EXECUTION_LOG_USE_COLOR", True):
        # LINEAJE: runtime guardrail checks `text` as it flows from the agent to the user interface, before it leaves the application (in _color).
        #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `text` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:55b8185735e564862692853b67c5bd640e13380595feabf1aa2840fe79886215'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:55b8185735e564862692853b67c5bd640e13380595feabf1aa2840fe79886215', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/core/execution_logger.py', 'line': 30, 'function': '_color'}, 'file': 'project/core/execution_logger.py', 'line': 30, 'function': '_color', 'agent_name': '_color', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
        try:
            text = _gr_client.enforce(_gr_site, text, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return text
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def _truncate(value: Any, max_chars: int | None = None) -> str:
    text = "" if value is None else str(value)
    limit = max_chars or getattr(config, "EXECUTION_LOG_MAX_CHARS", 1200)
    if len(text) <= limit:
        # LINEAJE: runtime guardrail checks `text` as it flows from the agent to the user interface, before it leaves the application (in _truncate).
        #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `text` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:ccde6caa6bbe68e436a6ec264757b90e9599b298e6fddc5472ce688b292c5843'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:ccde6caa6bbe68e436a6ec264757b90e9599b298e6fddc5472ce688b292c5843', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/core/execution_logger.py', 'line': 38, 'function': '_truncate'}, 'file': 'project/core/execution_logger.py', 'line': 38, 'function': '_truncate', 'agent_name': '_truncate', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
        try:
            text = _gr_client.enforce(_gr_site, text, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return text
    return f"{text[:limit]}... [truncated {len(text) - limit} chars]"


def _message_role(message: Any) -> str:
    if isinstance(message, HumanMessage):
        return "human"
    if isinstance(message, AIMessage):
        return "ai"
    if isinstance(message, ToolMessage):
        return "tool"
    if isinstance(message, SystemMessage):
        return "system"
    if isinstance(message, RemoveMessage):
        return "remove"
    return message.__class__.__name__


def _message_preview(message: Any) -> dict[str, Any]:
    preview = {
        "type": _message_role(message),
        "id": getattr(message, "id", None),
    }

    if isinstance(message, RemoveMessage):
        # LINEAJE: runtime guardrail checks `preview` as it flows from a tool to the user interface, before it leaves the application (in _message_preview).
        #   Detected: this statement moves data from a tool to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012, AI_DAT_SEC_027; sensitive values in `preview` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:c73300aa8aaf7c9c5d53317d99746148831e55a20be6c7dded5f0d4c3a52be08'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:c73300aa8aaf7c9c5d53317d99746148831e55a20be6c7dded5f0d4c3a52be08', phase='data_egress', boundary={'source': 'tool_result', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='tool', destination_type='user_interface', components={'invocation': {'file': 'project/core/execution_logger.py', 'line': 63, 'function': '_message_preview'}, 'file': 'project/core/execution_logger.py', 'line': 63, 'function': '_message_preview', 'agent_name': '_message_preview', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
        try:
            preview = _gr_client.enforce(_gr_site, preview, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return preview

    content = getattr(message, "content", "")
    if content:
        preview["content"] = _truncate(content)

    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        preview["tool_calls"] = [
            {
                "name": call.get("name"),
                "args": call.get("args"),
                "id": call.get("id"),
            }
            for call in tool_calls
        ]

    tool_name = getattr(message, "name", None)
    if tool_name:
        preview["name"] = tool_name

    tool_call_id = getattr(message, "tool_call_id", None)
    if tool_call_id:
        preview["tool_call_id"] = tool_call_id

    # LINEAJE: runtime guardrail checks `preview` as it flows from a tool to the user interface, before it leaves the application (in _message_preview).
    #   Detected: this statement moves data from a tool to the user interface with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_012, AI_DAT_SEC_027; sensitive values in `preview` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:45045203d14e201cc328beaef5f5af6500636e27fca8588311a972d657d86e10'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:45045203d14e201cc328beaef5f5af6500636e27fca8588311a972d657d86e10', phase='data_egress', boundary={'source': 'tool_result', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='tool', destination_type='user_interface', components={'invocation': {'file': 'project/core/execution_logger.py', 'line': 88, 'function': '_message_preview'}, 'file': 'project/core/execution_logger.py', 'line': 88, 'function': '_message_preview', 'agent_name': '_message_preview', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        preview = _gr_client.enforce(_gr_site, preview, content_type='text/plain')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    return preview


def _messages_preview(messages: list[Any]) -> dict[str, Any]:
    return {
        "count": len(messages),
        "last_messages": [_message_preview(message) for message in messages[-4:]],
    }


def state_preview(state: Any) -> dict[str, Any]:
    if not isinstance(state, dict):
        return {"value": _truncate(state)}

    preview: dict[str, Any] = {}

    for key, value in state.items():
        if key == "messages":
            preview[key] = _messages_preview(value or [])
        elif key in {"conversation_summary", "context_summary", "final_answer"}:
            preview[key] = _truncate(value)
        elif key == "agent_answers":
            preview[key] = {
                "count": len(value or []),
                "items": [
                    {
                        "index": item.get("index"),
                        "question": _truncate(item.get("question", ""), 240),
                        "answer": _truncate(item.get("answer", ""), 500),
                    }
                    for item in (value or [])[:3]
                    if isinstance(item, dict)
                ],
            }
        elif isinstance(value, set):
            preview[key] = sorted(value)
        else:
            preview[key] = value

    # LINEAJE: runtime guardrail checks `preview` as it flows from a tool to the user interface, before it leaves the application (in state_preview).
    #   Detected: this statement moves data from a tool to the user interface with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_012, AI_DAT_SEC_027; sensitive values in `preview` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:8406ab002d2153a2c5626c888818ba647be8782e5c43d66039c240096a72f43d'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:8406ab002d2153a2c5626c888818ba647be8782e5c43d66039c240096a72f43d', phase='data_egress', boundary={'source': 'tool_result', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='tool', destination_type='user_interface', components={'invocation': {'file': 'project/core/execution_logger.py', 'line': 127, 'function': 'state_preview'}, 'file': 'project/core/execution_logger.py', 'line': 127, 'function': 'state_preview', 'agent_name': 'state_preview', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        preview = _gr_client.enforce(_gr_site, preview, content_type='text/plain')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    return preview


def update_preview(update: Any) -> Any:
    if not isinstance(update, dict):
        return _truncate(update)

    preview: dict[str, Any] = {}
    for key, value in update.items():
        if key == "messages":
            preview[key] = [_message_preview(message) for message in value]
        elif key in {"conversation_summary", "context_summary", "final_answer"}:
            preview[key] = _truncate(value)
        elif key == "agent_answers":
            preview[key] = state_preview({"agent_answers": value})["agent_answers"]
        elif isinstance(value, set):
            preview[key] = sorted(value)
        else:
            preview[key] = value
    # LINEAJE: runtime guardrail checks `preview` as it flows from a tool to the user interface, before it leaves the application (in update_preview).
    #   Detected: this statement moves data from a tool to the user interface with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_012, AI_DAT_SEC_027; sensitive values in `preview` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:6544afbb9ee4dca816937de18929b9b755f4cf0626567ed85cb31afa55f47a98'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:6544afbb9ee4dca816937de18929b9b755f4cf0626567ed85cb31afa55f47a98', phase='data_egress', boundary={'source': 'tool_result', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='tool', destination_type='user_interface', components={'invocation': {'file': 'project/core/execution_logger.py', 'line': 146, 'function': 'update_preview'}, 'file': 'project/core/execution_logger.py', 'line': 146, 'function': 'update_preview', 'agent_name': 'update_preview', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        preview = _gr_client.enforce(_gr_site, preview, content_type='text/plain')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    return preview


def _print_block(title: str, payload: Any, color: str) -> None:
    if not _enabled():
        return

    timestamp = datetime.now().strftime("%H:%M:%S")
    _lineaje_payload = _color(f"\n[{timestamp}] {title}", color)
    # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the application log, before it is written to the log (in _print_block).
    #   Detected: this statement moves data from the agent to the application log with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_010; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:a5a3f338e9b001c2c23e202042a6ae5beecb1e3c77a02e202a8ffdcf32d2d298'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:a5a3f338e9b001c2c23e202042a6ae5beecb1e3c77a02e202a8ffdcf32d2d298', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', components={'invocation': {'file': 'project/core/execution_logger.py', 'line': 154, 'function': '_print_block'}, 'file': 'project/core/execution_logger.py', 'line': 154, 'function': '_print_block', 'agent_name': '_print_block', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    print(_lineaje_payload)
    _lineaje_payload = _color("-" * 80, "dim")
    # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the application log, before it is written to the log (in _print_block).
    #   Detected: this statement moves data from the agent to the application log with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_010; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:04e919e6b124f6ec1ae301f4b0dfde1ff2464ae1828d2c33d7aaf408495f4c8b'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:04e919e6b124f6ec1ae301f4b0dfde1ff2464ae1828d2c33d7aaf408495f4c8b', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', components={'invocation': {'file': 'project/core/execution_logger.py', 'line': 155, 'function': '_print_block'}, 'file': 'project/core/execution_logger.py', 'line': 155, 'function': '_print_block', 'agent_name': '_print_block', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    print(_lineaje_payload)
    _lineaje_payload = pformat(payload, width=120, sort_dicts=False)
    # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the application log, before it is written to the log (in _print_block).
    #   Detected: this statement moves data from the agent to the application log with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_010; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:badedfc7c748ac0f24be05ba405ce8f0da8fd25f960085257ecd3cd13f6007d8'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:badedfc7c748ac0f24be05ba405ce8f0da8fd25f960085257ecd3cd13f6007d8', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', components={'invocation': {'file': 'project/core/execution_logger.py', 'line': 156, 'function': '_print_block'}, 'file': 'project/core/execution_logger.py', 'line': 156, 'function': '_print_block', 'agent_name': '_print_block', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    print(_lineaje_payload)


def log_chat_start(message: str, thread_id: str, has_pending_interrupt: bool) -> None:
    _print_block(
        "USER QUERY",
        {
            "thread_id": thread_id,
            "pending_interrupt": has_pending_interrupt,
            "message": _truncate(message),
        },
        "blue",
    )


def log_chat_end(state: Any) -> None:
    _print_block("FINAL GRAPH STATE", state_preview(state), "blue")


def log_node_start(name: str, state: Any) -> None:
    _print_block(f"NODE START: {name}", state_preview(state), "cyan")


def log_node_end(name: str, update: Any) -> None:
    _print_block(f"NODE OUTPUT: {name}", update_preview(update), "green")


def log_route(name: str, decision: Any, state: Any | None = None) -> None:
    payload = {"decision": _truncate(decision)}
    if state is not None:
        payload["state"] = state_preview(state)
    _print_block(f"ROUTE: {name}", payload, "yellow")


def log_tool_start(name: str, args: dict[str, Any]) -> None:
    _print_block(f"TOOL START: {name}", args, "magenta")


def log_tool_end(name: str, output: Any) -> None:
    _print_block(f"TOOL OUTPUT: {name}", {"output": _truncate(output)}, "magenta")


def log_error(scope: str, error: Exception) -> None:
    _print_block(f"ERROR: {scope}", {"type": error.__class__.__name__, "message": str(error)}, "red")


def logged_node(name: str, fn):
    def _wrapped(state, *args, **kwargs):
        log_node_start(name, state)
        try:
            result = fn(state, *args, **kwargs)
        except Exception as exc:
            log_error(name, exc)
            raise
        log_node_end(name, result)
        # LINEAJE: runtime guardrail checks `result` as it flows from the agent to the user interface, before it leaves the application (in _wrapped).
        #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `result` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:fa3617a4cd669c84ae082c09ce6f0dccfbf46ad4aa9bd59ea634c788d58f85fe'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:fa3617a4cd669c84ae082c09ce6f0dccfbf46ad4aa9bd59ea634c788d58f85fe', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/core/execution_logger.py', 'line': 211, 'function': 'logged_node._wrapped'}, 'file': 'project/core/execution_logger.py', 'line': 211, 'function': '_wrapped', 'agent_name': '_wrapped', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
        try:
            result = _gr_client.enforce(_gr_site, result, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return result

    # LINEAJE: runtime guardrail checks `_wrapped` as it flows from the agent to the user interface, before it leaves the application (in logged_node).
    #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `_wrapped` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:3c776c6411af6725cf8ce5da8c10d2f4c3e8f21c92477c88c596918fd871b2cc'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:3c776c6411af6725cf8ce5da8c10d2f4c3e8f21c92477c88c596918fd871b2cc', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/core/execution_logger.py', 'line': 213, 'function': 'logged_node'}, 'file': 'project/core/execution_logger.py', 'line': 213, 'function': 'logged_node', 'agent_name': 'logged_node', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        _wrapped = _gr_client.enforce(_gr_site, _wrapped, content_type='text/plain')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    return _wrapped
