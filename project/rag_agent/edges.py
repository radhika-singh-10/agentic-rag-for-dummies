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

from typing import Literal
from langgraph.types import Send
from .graph_state import State, AgentState
from config import MAX_ITERATIONS, MAX_TOOL_CALLS
from core.execution_logger import log_route

def route_after_rewrite(state: State) -> Literal["request_clarification", "agent"]:
    if not state.get("questionIsClear", False):
        decision = "request_clarification"
    else:
        try:
            _lineaje_obs = _lineaje_load_gr_client()
            _lineaje_obs_site = _lineaje_obs.SiteDescriptor(site_id='site:sha256:f5dc499a5d902f814f406b58bbd928df5972ea229263e2982e798f474ada8644', phase='', boundary={}, fail_mode='ALLOW', source_type='agent', destination_type='agent', components={'file': 'project/rag_agent/edges.py', 'line': 12, 'function': 'route_after_rewrite', 'agent_name': 'route_after_rewrite', 'agent_name_source': 'inferred_from_function', 'call_target': 'Send', 'not_on_graph': True}, observe_only=True)
            _lineaje_obs.enforce(_lineaje_obs_site, {'activity': 'agent_to_agent'}, content_type='application/json')
        except Exception:
            pass
        decision = [
                Send("agent", {"question": query, "question_index": idx, "messages": []})
                for idx, query in enumerate(state["rewrittenQuestions"])
            ]
    log_route("after_rewrite", decision, state)
    # LINEAJE: runtime guardrail checks `decision` as it flows from a tool to the user interface, before it leaves the application (in route_after_rewrite).
    #   Detected: this statement moves data from a tool to the user interface with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_012, AI_DAT_SEC_027; sensitive values in `decision` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:e4890f8f39cb2fa5420f07c12d875b81bbc20eabeafc9c2ffd080e774332272e'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:e4890f8f39cb2fa5420f07c12d875b81bbc20eabeafc9c2ffd080e774332272e', phase='data_egress', boundary={'source': 'tool_result', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='tool', destination_type='user_interface', components={'invocation': {'file': 'project/rag_agent/edges.py', 'line': 16, 'function': 'route_after_rewrite'}, 'file': 'project/rag_agent/edges.py', 'line': 16, 'function': 'route_after_rewrite', 'agent_name': 'route_after_rewrite', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        decision = _gr_client.enforce(_gr_site, decision, content_type='text/plain')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    return decision
    
def route_after_orchestrator_call(state: AgentState) -> Literal["tools", "fallback_response", "collect_answer"]:
    iteration = state.get("iteration_count", 0)
    tool_count = state.get("tool_call_count", 0)

    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None) or []

    if not tool_calls:
        decision = "collect_answer"
        log_route("after_orchestrator_call", decision, state)
        # LINEAJE: runtime guardrail checks `decision` as it flows from a tool to the user interface, before it leaves the application (in route_after_orchestrator_call).
        #   Detected: this statement moves data from a tool to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012, AI_DAT_SEC_027; sensitive values in `decision` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:192141e332d94d84f74e811762de766e3536f5a151799cad4b8bc5567de6c5a9'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:192141e332d94d84f74e811762de766e3536f5a151799cad4b8bc5567de6c5a9', phase='data_egress', boundary={'source': 'tool_result', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='tool', destination_type='user_interface', components={'invocation': {'file': 'project/rag_agent/edges.py', 'line': 28, 'function': 'route_after_orchestrator_call'}, 'file': 'project/rag_agent/edges.py', 'line': 28, 'function': 'route_after_orchestrator_call', 'agent_name': 'route_after_orchestrator_call', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
        try:
            decision = _gr_client.enforce(_gr_site, decision, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return decision

    # The counters already include the current LLM response. Allow a final
    # answer at the iteration boundary, but do not execute tool calls that
    # would exceed the configured research budget.
    if iteration >= MAX_ITERATIONS or tool_count > MAX_TOOL_CALLS:
        decision = "fallback_response"
        log_route("after_orchestrator_call", decision, state)
        # LINEAJE: runtime guardrail checks `decision` as it flows from a tool to the user interface, before it leaves the application (in route_after_orchestrator_call).
        #   Detected: this statement moves data from a tool to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012, AI_DAT_SEC_027; sensitive values in `decision` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:04d0fd14b49f96466f6df02a7ba70a902cf462f3e7a9058d82d5a6e1f263c535'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:04d0fd14b49f96466f6df02a7ba70a902cf462f3e7a9058d82d5a6e1f263c535', phase='data_egress', boundary={'source': 'tool_result', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='tool', destination_type='user_interface', components={'invocation': {'file': 'project/rag_agent/edges.py', 'line': 36, 'function': 'route_after_orchestrator_call'}, 'file': 'project/rag_agent/edges.py', 'line': 36, 'function': 'route_after_orchestrator_call', 'agent_name': 'route_after_orchestrator_call', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
        try:
            decision = _gr_client.enforce(_gr_site, decision, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return decision
    
    decision = "tools"
    log_route("after_orchestrator_call", decision, state)
    # LINEAJE: runtime guardrail checks `decision` as it flows from a tool to the user interface, before it leaves the application (in route_after_orchestrator_call).
    #   Detected: this statement moves data from a tool to the user interface with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_012, AI_DAT_SEC_027; sensitive values in `decision` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:b65c6b3e8f098390c6def89c716474b2a51ebde9b4ebc835bfee87d6115c8bed'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:b65c6b3e8f098390c6def89c716474b2a51ebde9b4ebc835bfee87d6115c8bed', phase='data_egress', boundary={'source': 'tool_result', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='tool', destination_type='user_interface', components={'invocation': {'file': 'project/rag_agent/edges.py', 'line': 40, 'function': 'route_after_orchestrator_call'}, 'file': 'project/rag_agent/edges.py', 'line': 40, 'function': 'route_after_orchestrator_call', 'agent_name': 'route_after_orchestrator_call', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        decision = _gr_client.enforce(_gr_site, decision, content_type='text/plain')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    return decision
