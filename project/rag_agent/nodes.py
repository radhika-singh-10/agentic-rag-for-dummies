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

from typing import Literal, Set
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage, AIMessage, ToolMessage
from langgraph.types import Command
from .graph_state import State, AgentState
from .schemas import QueryAnalysis
from .prompts import *
from utils import estimate_context_tokens
from config import BASE_TOKEN_THRESHOLD, CHILD_CHUNK_SEPARATOR, MAIN_HISTORY_MESSAGES_TO_KEEP, TOKEN_GROWTH_FACTOR

if MAIN_HISTORY_MESSAGES_TO_KEEP < 2:
    raise ValueError("MAIN_HISTORY_MESSAGES_TO_KEEP must be at least 2.")

PRE_ANSWER_HISTORY_MESSAGES_TO_KEEP = max(MAIN_HISTORY_MESSAGES_TO_KEEP - 1, 0)

def _is_plain_conversation_message(msg) -> bool:
    return (
        isinstance(msg, (HumanMessage, AIMessage))
        and not getattr(msg, "tool_calls", None)
        and not getattr(msg, "name", None)
    )

def _name_internal_message(message, name):
    """Tag a subgraph-only message so it is not treated as chat history."""
    return message.model_copy(update={"name": name})

def _retrieval_contexts(messages) -> list[str]:
    contexts = []
    ignored_prefixes = (
        "NO_RELEVANT_CHUNKS",
        "NO_PARENT_DOCUMENT",
        "RETRIEVAL_ERROR:",
        "PARENT_RETRIEVAL_ERROR:",
    )
    for message in messages:
        if not isinstance(message, ToolMessage):
            continue
        content = str(message.content).strip()
        if content and not content.startswith(ignored_prefixes):
            parts = content.split(CHILD_CHUNK_SEPARATOR) if message.name == "search_child_chunks" else [content]
            contexts.extend(part for part in parts if part)
    return list(dict.fromkeys(contexts))

def _format_conversation(messages) -> str:
    lines = []
    for msg in messages:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)

def _remove_messages_not_in(messages, keep_ids):
    removals = []
    for msg in messages:
        msg_id = getattr(msg, "id", None)
        if isinstance(msg, SystemMessage) or not msg_id:
            continue
        if msg_id not in keep_ids:
            removals.append(RemoveMessage(id=msg_id))
    # LINEAJE: runtime guardrail checks `removals` as it flows from the agent to the user interface, before it leaves the application (in _remove_messages_not_in).
    #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `removals` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:38f99a062edb18ef00e66dcd4dc063c183d1a7ee8120b933d94d5b20ffc66500'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:38f99a062edb18ef00e66dcd4dc063c183d1a7ee8120b933d94d5b20ffc66500', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'line': 58, 'function': '_remove_messages_not_in'}, 'file': 'project/rag_agent/nodes.py', 'line': 58, 'function': '_remove_messages_not_in', 'agent_name': '_remove_messages_not_in', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        removals = _gr_client.enforce(_gr_site, removals, content_type='text/plain')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    return removals

def _recent_conversation(messages, pending_query="") -> list:
    """Return recent context before the current user message.

    During clarification, exclude the unresolved query and the assistant's
    clarification request because they are represented explicitly.
    """
    plain_messages = [msg for msg in messages if _is_plain_conversation_message(msg)]
    recent_messages = plain_messages[:-1]

    if pending_query:
        for index in range(len(recent_messages) - 1, -1, -1):
            msg = recent_messages[index]
            if isinstance(msg, HumanMessage) and str(msg.content).strip() == pending_query:
                return recent_messages[:index]

    # LINEAJE: runtime guardrail checks `recent_messages` as it flows from the agent to the user interface, before it leaves the application (in _recent_conversation).
    #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `recent_messages` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:9778705e134273b1dd1caee89c5ed857aa639a9f43775d68b3dfba83a718e2be'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:9778705e134273b1dd1caee89c5ed857aa639a9f43775d68b3dfba83a718e2be', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'line': 75, 'function': '_recent_conversation'}, 'file': 'project/rag_agent/nodes.py', 'line': 75, 'function': '_recent_conversation', 'agent_name': '_recent_conversation', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        recent_messages = _gr_client.enforce(_gr_site, recent_messages, content_type='text/plain')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    return recent_messages

def summarize_history(state: State, llm):
    messages = state.get("messages", [])
    updates = {"agent_answers": [{"__reset__": True}]}

    if not messages:
        # LINEAJE: runtime guardrail checks `updates` as it flows from the agent to the user interface, before it leaves the application (in summarize_history).
        #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `updates` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:b858029dd320de591b6fb1fd436a1f55404873fe277538854cdb841620e22c65'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:b858029dd320de591b6fb1fd436a1f55404873fe277538854cdb841620e22c65', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'line': 82, 'function': 'summarize_history'}, 'file': 'project/rag_agent/nodes.py', 'line': 82, 'function': 'summarize_history', 'agent_name': 'summarize_history', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
        try:
            updates = _gr_client.enforce(_gr_site, updates, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return updates

    plain_messages = [msg for msg in messages if _is_plain_conversation_message(msg)]
    keep_count = PRE_ANSWER_HISTORY_MESSAGES_TO_KEEP
    messages_to_summarize = plain_messages[:-keep_count] if len(plain_messages) > keep_count else []
    keep_ids = {getattr(msg, "id", None) for msg in plain_messages[-keep_count:]}
    keep_ids.discard(None)

    removals = _remove_messages_not_in(messages, keep_ids)
    if removals:
        updates["messages"] = removals

    if not messages_to_summarize:
        # LINEAJE: runtime guardrail checks `updates` as it flows from the agent to the user interface, before it leaves the application (in summarize_history).
        #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `updates` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:6d0c141cc6098781d44902a75b16c801ddc1dec5674e2903852fd9479be7d2a1'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:6d0c141cc6098781d44902a75b16c801ddc1dec5674e2903852fd9479be7d2a1', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'line': 95, 'function': 'summarize_history'}, 'file': 'project/rag_agent/nodes.py', 'line': 95, 'function': 'summarize_history', 'agent_name': 'summarize_history', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
        try:
            updates = _gr_client.enforce(_gr_site, updates, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return updates

    existing_summary = state.get("conversation_summary", "").strip()
    conversation = "Existing summary:\n"
    conversation += f"{existing_summary or '(none)'}\n\n"
    conversation += "New messages to merge into the summary:\n"
    conversation += _format_conversation(messages_to_summarize)

    _lineaje_arg = ([
        SystemMessage(content=get_conversation_summary_prompt()),
        HumanMessage(content=conversation),
    ])
    # LINEAJE: runtime guardrail checks `_lineaje_arg` as it flows from the agent to the LLM, before it is sent to the model (in summarize_history).
    #   Detected: this statement moves data from the agent to the LLM with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_AGENT_ACTIVITY_LOG, AI_APP_SEC_006, AI_APP_SEC_028, AI_APP_SEC_070 (+2 more); sensitive values in `_lineaje_arg` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:4a3eae013935f2126b095aab57e814dea317f26c402f4ac5f31506d1503ca646'
    _lineaje__lineaje_arg_evidence = {'_lineaje_arg': _lineaje_arg, **(getattr(_lineaje_load_gr_client(), 'receiver_model', None) or (lambda o, p, f, s: {'model': f, 'model_source': s}))(llm, (), getattr(_lineaje_load_gr_client(), 'current_model', lambda _f: '')(__file__), 'guess')}
    _gr_client = _lineaje_load_gr_client()
    _lineaje_interaction_id = _gr_client.new_interaction_id()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:4a3eae013935f2126b095aab57e814dea317f26c402f4ac5f31506d1503ca646', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'function': 'summarize_history', 'line': 103}, 'file': 'project/rag_agent/nodes.py', 'line': 103, 'function': 'summarize_history', 'agent_name': 'summarize_history', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:aeb48dc9fb7327ac'}, interaction_id=_lineaje_interaction_id)
    try:
        _lineaje__lineaje_arg_evidence = _gr_client.enforce(_gr_site, _lineaje__lineaje_arg_evidence, content_type='application/json')
        _lineaje_arg = _lineaje__lineaje_arg_evidence.get('_lineaje_arg', _lineaje_arg) if isinstance(_lineaje__lineaje_arg_evidence, dict) else _lineaje_arg
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        raise
    summary_response = llm.invoke(_lineaje_arg)
    # LINEAJE: runtime guardrail checks `summary_response` as it flows from the LLM to the agent, after the model replies (in summarize_history).
    #   Detected: this statement moves data from the LLM to the agent with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_011, AI_DAT_SEC_025, AI_DAT_SEC_027, AI_DAT_SEC_029; sensitive values in `summary_response` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:f54e54341dc6413512b77ac5e6cea50f90bba69238124a22be9203774ebab26e'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:f54e54341dc6413512b77ac5e6cea50f90bba69238124a22be9203774ebab26e', phase='post_model', boundary={'source': 'model', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='llm', destination_type='agent', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'function': 'summarize_history', 'line': 103}, 'file': 'project/rag_agent/nodes.py', 'line': 103, 'function': 'summarize_history', 'agent_name': 'summarize_history', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:aeb48dc9fb7327ac'}, interaction_id=locals().get('_lineaje_interaction_id'))
    try:
        if not hasattr(_gr_client, 'enforce_reply'):
            __import__("logging").getLogger("lineaje.gr_client").error("gr_stub_client.py predates enforce_reply (STUB_API 2): this site is NOT enforced; replace gr_stub_client.py with the current companion")
            raise _gr_client.GuardrailUnavailableError("stale gr_stub_client.py: no enforce_reply")
        summary_response = _gr_client.enforce_reply(_gr_site, summary_response, content_type='application/json')
    except _gr_client.GuardrailUnavailableError:
        pass
    updates["conversation_summary"] = summary_response.content.strip()
    # LINEAJE: runtime guardrail checks `updates` as it flows from the agent to the user interface, before it leaves the application (in summarize_history).
    #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `updates` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:99287516c076751793402bdda888219adbcc361bd362060b0c19c3786d91ad24'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:99287516c076751793402bdda888219adbcc361bd362060b0c19c3786d91ad24', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'line': 108, 'function': 'summarize_history'}, 'file': 'project/rag_agent/nodes.py', 'line': 108, 'function': 'summarize_history', 'agent_name': 'summarize_history', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        updates = _gr_client.enforce(_gr_site, updates, content_type='text/plain')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    return updates

def rewrite_query(state: State, llm):
    last_message = state["messages"][-1]
    current_query = str(last_message.content).strip()
    conversation_summary = state.get("conversation_summary", "").strip()
    pending_query = state.get("pendingQuery", "").strip()
    pending_clarifications = state.get("pendingClarifications", [])
    recent_messages = _recent_conversation(state["messages"], pending_query)

    context_parts = []
    if conversation_summary:
        context_parts.append(f"Conversation Summary:\n{conversation_summary}")
    if recent_messages:
        context_parts.append(f"Recent Conversation:\n{_format_conversation(recent_messages)}")

    if pending_query:
        clarifications = [*pending_clarifications, current_query]
        clarification_text = "\n".join(
            f"{index}. {value}" for index, value in enumerate(clarifications, start=1)
        )
        context_parts.append(
            f"Unresolved User Query:\n{pending_query}\n\n"
            f"User Clarifications:\n{clarification_text}"
        )
        original_query = f"{pending_query}\nClarifications:\n{clarification_text}"
    else:
        clarifications = []
        context_parts.append(f"User Query:\n{current_query}")
        original_query = current_query

    context_section = "\n\n".join(context_parts)
    try:
        _lineaje_obs = _lineaje_load_gr_client()
        _lineaje_obs_site = _lineaje_obs.SiteDescriptor(site_id='site:sha256:b255a2c4dfa42b1bdd303da7778b1697ee56931aa200f67af121ef4e13e894a4', phase='', boundary={}, fail_mode='ALLOW', source_type='agent', destination_type='llm', components={'file': 'project/rag_agent/nodes.py', 'line': 140, 'function': 'rewrite_query', 'agent_name': 'rewrite_query', 'agent_name_source': 'inferred_from_function', 'call_target': 'llm.with_structured_output', 'source': {'entity_type': 'agent', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'function': 'rewrite_query', 'line': 140}, 'destination': {'entity_type': 'llm', 'name': 'granite4.1:8b', 'provider': '', 'version': ''}, 'boundary_id': 'bnd:b817346cfbce785f'}, observe_only=True)
        _lineaje_obs.enforce(_lineaje_obs_site, {'activity': 'agent_to_llm'}, content_type='application/json')
    except Exception:
        pass
    llm_with_structure = llm.with_structured_output(QueryAnalysis)
    _lineaje_arg = [SystemMessage(content=get_rewrite_query_prompt()), HumanMessage(content=context_section)]
    # LINEAJE: runtime guardrail checks `_lineaje_arg` as it flows from the agent to the LLM, before it is sent to the model (in rewrite_query).
    #   Detected: this statement moves data from the agent to the LLM with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_AGENT_ACTIVITY_LOG, AI_APP_SEC_006, AI_APP_SEC_028, AI_APP_SEC_070 (+2 more); sensitive values in `_lineaje_arg` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:21ceedd81971f91a26478779035fa7de60fe77096d5c1ed67ea424dda817b8bd'
    _lineaje__lineaje_arg_evidence = {'_lineaje_arg': _lineaje_arg, **(getattr(_lineaje_load_gr_client(), 'receiver_model', None) or (lambda o, p, f, s: {'model': f, 'model_source': s}))(llm_with_structure, (), getattr(_lineaje_load_gr_client(), 'current_model', lambda _f: '')(__file__), 'guess')}
    _gr_client = _lineaje_load_gr_client()
    _lineaje_interaction_id = _gr_client.new_interaction_id()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:21ceedd81971f91a26478779035fa7de60fe77096d5c1ed67ea424dda817b8bd', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'function': 'rewrite_query', 'line': 141}, 'file': 'project/rag_agent/nodes.py', 'line': 141, 'function': 'rewrite_query', 'agent_name': 'rewrite_query', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:b28c6c9104b3f138'}, interaction_id=_lineaje_interaction_id)
    try:
        _lineaje__lineaje_arg_evidence = _gr_client.enforce(_gr_site, _lineaje__lineaje_arg_evidence, content_type='application/json')
        _lineaje_arg = _lineaje__lineaje_arg_evidence.get('_lineaje_arg', _lineaje_arg) if isinstance(_lineaje__lineaje_arg_evidence, dict) else _lineaje_arg
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        raise
    response = llm_with_structure.invoke(_lineaje_arg)
    # LINEAJE: runtime guardrail checks `response` as it flows from the LLM to the agent, after the model replies (in rewrite_query).
    #   Detected: this statement moves data from the LLM to the agent with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_011, AI_DAT_SEC_025, AI_DAT_SEC_027, AI_DAT_SEC_029; sensitive values in `response` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:6841b6039faa68f15a88c92c17ff8f09a71437fa983356ea52643857f895762c'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:6841b6039faa68f15a88c92c17ff8f09a71437fa983356ea52643857f895762c', phase='post_model', boundary={'source': 'model', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='llm', destination_type='agent', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'function': 'rewrite_query', 'line': 141}, 'file': 'project/rag_agent/nodes.py', 'line': 141, 'function': 'rewrite_query', 'agent_name': 'rewrite_query', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:b28c6c9104b3f138'}, interaction_id=locals().get('_lineaje_interaction_id'))
    try:
        if not hasattr(_gr_client, 'enforce_reply'):
            __import__("logging").getLogger("lineaje.gr_client").error("gr_stub_client.py predates enforce_reply (STUB_API 2): this site is NOT enforced; replace gr_stub_client.py with the current companion")
            raise _gr_client.GuardrailUnavailableError("stale gr_stub_client.py: no enforce_reply")
        response = _gr_client.enforce_reply(_gr_site, response, content_type='application/json')
    except _gr_client.GuardrailUnavailableError:
        pass
    clarification_message_update = (
        [_name_internal_message(last_message, "clarification_response")]
        if pending_query else []
    )

    if response.questions and response.is_clear:
        return {
            "questionIsClear": True,
            "originalQuery": original_query,
            "pendingQuery": "",
            "pendingClarifications": [],
            "rewrittenQuestions": response.questions,
            "messages": clarification_message_update,
        }

    clarification = response.clarification_needed if response.clarification_needed and len(response.clarification_needed.strip()) > 10 else "I need more information to understand your question."
    return {
        "questionIsClear": False,
        "originalQuery": "",
        "pendingQuery": pending_query or current_query,
        "pendingClarifications": clarifications,
        "rewrittenQuestions": [],
        "messages": clarification_message_update + [
            AIMessage(content=clarification, name="clarification")
        ],
    }

def request_clarification(state: State):
    return {}

# --- Agent Nodes ---
def orchestrator(state: AgentState, llm_with_tools):
    context_summary = state.get("context_summary", "").strip()
    sys_msg = SystemMessage(content=get_orchestrator_prompt())
    summary_injection = (
        [HumanMessage(content=f"[COMPRESSED CONTEXT FROM PRIOR RESEARCH]\n\n{context_summary}")]
        if context_summary else []
    )
    if not state.get("messages"):
        human_msg = HumanMessage(content=state["question"], name="agent_question")
        force_search = HumanMessage(content="YOU MUST CALL 'search_child_chunks' AS THE FIRST STEP TO ANSWER THIS QUESTION.")
        _lineaje_payload = [sys_msg] + summary_injection + [human_msg, force_search]
        # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the LLM, before it is sent to the model (in orchestrator).
        #   Detected: this statement moves data from the agent to the LLM with no runtime policy check (detection confidence: medium).
        #   Decision: the Guardrail evaluates AI_AGENT_ACTIVITY_LOG, AI_APP_SEC_006, AI_APP_SEC_028, AI_APP_SEC_070 (+2 more); sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:77be5d6b2e8b1b0be8225cba90d0be265402d47169e8958c05f6d8ff62ed062d'
        _lineaje__lineaje_payload_evidence = {'_lineaje_payload': _lineaje_payload, 'model': getattr(_lineaje_load_gr_client(), 'current_model', lambda _f: '')(__file__)}
        _gr_client = _lineaje_load_gr_client()
        _lineaje_interaction_id = _gr_client.new_interaction_id()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:77be5d6b2e8b1b0be8225cba90d0be265402d47169e8958c05f6d8ff62ed062d', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'line': 183, 'function': 'orchestrator'}, 'file': 'project/rag_agent/nodes.py', 'line': 183, 'function': 'orchestrator', 'agent_name': 'orchestrator', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True}, interaction_id=_lineaje_interaction_id)
        try:
            _lineaje__lineaje_payload_evidence = _gr_client.enforce(_gr_site, _lineaje__lineaje_payload_evidence, content_type='application/json')
            _lineaje_payload = _lineaje__lineaje_payload_evidence.get('_lineaje_payload', _lineaje_payload) if isinstance(_lineaje__lineaje_payload_evidence, dict) else _lineaje_payload
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            raise
        response = llm_with_tools.invoke(_lineaje_payload)
        # LINEAJE: runtime guardrail checks `response` as it flows from the LLM to the agent, after the model replies (in orchestrator).
        #   Detected: this statement moves data from the LLM to the agent with no runtime policy check (detection confidence: medium).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_011, AI_DAT_SEC_025, AI_DAT_SEC_027, AI_DAT_SEC_029; sensitive values in `response` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:3e4845a9938d24a68f36073b617e684f2c110fbb383ef9d52893815395b8c9ae'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:3e4845a9938d24a68f36073b617e684f2c110fbb383ef9d52893815395b8c9ae', phase='post_model', boundary={'source': 'model', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='llm', destination_type='agent', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'line': 183, 'function': 'orchestrator'}, 'file': 'project/rag_agent/nodes.py', 'line': 183, 'function': 'orchestrator', 'agent_name': 'orchestrator', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True}, interaction_id=locals().get('_lineaje_interaction_id'))
        try:
            response = _gr_client.enforce(_gr_site, response, content_type='application/json', variable_name='response', source_file=__file__, before_line=183)
        except _gr_client.GuardrailUnavailableError:
            pass
        response = _name_internal_message(response, "agent_response")
        return {"messages": [human_msg, response], "tool_call_count": len(response.tool_calls or []), "iteration_count": 1}

    _lineaje_payload = [sys_msg] + summary_injection + state["messages"]
    # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the LLM, before it is sent to the model (in orchestrator).
    #   Detected: this statement moves data from the agent to the LLM with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_AGENT_ACTIVITY_LOG, AI_APP_SEC_006, AI_APP_SEC_028, AI_APP_SEC_070 (+2 more); sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:880b411dfbc3a1badfb1157e0ede4d655ffe6895d65b1eda69583a2516615879'
    _lineaje__lineaje_payload_evidence = {'_lineaje_payload': _lineaje_payload, 'model': getattr(_lineaje_load_gr_client(), 'current_model', lambda _f: '')(__file__)}
    _gr_client = _lineaje_load_gr_client()
    _lineaje_interaction_id = _gr_client.new_interaction_id()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:880b411dfbc3a1badfb1157e0ede4d655ffe6895d65b1eda69583a2516615879', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'line': 187, 'function': 'orchestrator'}, 'file': 'project/rag_agent/nodes.py', 'line': 187, 'function': 'orchestrator', 'agent_name': 'orchestrator', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True}, interaction_id=_lineaje_interaction_id)
    try:
        _lineaje__lineaje_payload_evidence = _gr_client.enforce(_gr_site, _lineaje__lineaje_payload_evidence, content_type='application/json')
        _lineaje_payload = _lineaje__lineaje_payload_evidence.get('_lineaje_payload', _lineaje_payload) if isinstance(_lineaje__lineaje_payload_evidence, dict) else _lineaje_payload
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        raise
    response = llm_with_tools.invoke(_lineaje_payload)
    # LINEAJE: runtime guardrail checks `response` as it flows from the LLM to the agent, after the model replies (in orchestrator).
    #   Detected: this statement moves data from the LLM to the agent with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_011, AI_DAT_SEC_025, AI_DAT_SEC_027, AI_DAT_SEC_029; sensitive values in `response` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:ea85422e06c131c29da814865f8e12f72dff0be27a25cd5a08fad40ccb6d4ec4'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:ea85422e06c131c29da814865f8e12f72dff0be27a25cd5a08fad40ccb6d4ec4', phase='post_model', boundary={'source': 'model', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='llm', destination_type='agent', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'line': 187, 'function': 'orchestrator'}, 'file': 'project/rag_agent/nodes.py', 'line': 187, 'function': 'orchestrator', 'agent_name': 'orchestrator', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True}, interaction_id=locals().get('_lineaje_interaction_id'))
    try:
        response = _gr_client.enforce(_gr_site, response, content_type='application/json', variable_name='response', source_file=__file__, before_line=187)
    except _gr_client.GuardrailUnavailableError:
        pass
    response = _name_internal_message(response, "agent_response")
    tool_calls = response.tool_calls if hasattr(response, "tool_calls") else []
    return {"messages": [response], "tool_call_count": len(tool_calls) if tool_calls else 0, "iteration_count": 1}

def fallback_response(state: AgentState, llm):
    seen = set()
    unique_contents = []
    for m in state["messages"]:
        if isinstance(m, ToolMessage) and m.content not in seen:
            unique_contents.append(m.content)
            seen.add(m.content)

    context_summary = state.get("context_summary", "").strip()

    context_parts = []
    if context_summary:
        context_parts.append(f"## Compressed Research Context (from prior iterations)\n\n{context_summary}")
    if unique_contents:
        context_parts.append(
            "## Retrieved Data (current iteration)\n\n" +
            "\n\n".join(f"--- DATA SOURCE {i} ---\n{content}" for i, content in enumerate(unique_contents, 1))
        )

    context_text = "\n\n".join(context_parts) if context_parts else "No data was retrieved from the documents."

    prompt_content = (
        f"USER QUERY: {state.get('question')}\n\n"
        f"{context_text}\n\n"
        f"INSTRUCTION:\nProvide the best possible answer using only the data above."
    )
    _lineaje_arg = [SystemMessage(content=get_fallback_response_prompt()), HumanMessage(content=prompt_content)]
    # LINEAJE: runtime guardrail checks `_lineaje_arg` as it flows from the agent to the LLM, before it is sent to the model (in fallback_response).
    #   Detected: this statement moves data from the agent to the LLM with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_AGENT_ACTIVITY_LOG, AI_APP_SEC_006, AI_APP_SEC_028, AI_APP_SEC_070 (+2 more); sensitive values in `_lineaje_arg` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:6ca9a1178ae091d97e55a5a6bf28c97fd4743b527aca9beafa4af98cc38bd03d'
    _lineaje__lineaje_arg_evidence = {'_lineaje_arg': _lineaje_arg, **(getattr(_lineaje_load_gr_client(), 'receiver_model', None) or (lambda o, p, f, s: {'model': f, 'model_source': s}))(llm, (), getattr(_lineaje_load_gr_client(), 'current_model', lambda _f: '')(__file__), 'guess')}
    _gr_client = _lineaje_load_gr_client()
    _lineaje_interaction_id = _gr_client.new_interaction_id()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:6ca9a1178ae091d97e55a5a6bf28c97fd4743b527aca9beafa4af98cc38bd03d', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'function': 'fallback_response', 'line': 218}, 'file': 'project/rag_agent/nodes.py', 'line': 218, 'function': 'fallback_response', 'agent_name': 'fallback_response', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:51d8bb524b745fe9'}, interaction_id=_lineaje_interaction_id)
    try:
        _lineaje__lineaje_arg_evidence = _gr_client.enforce(_gr_site, _lineaje__lineaje_arg_evidence, content_type='application/json')
        _lineaje_arg = _lineaje__lineaje_arg_evidence.get('_lineaje_arg', _lineaje_arg) if isinstance(_lineaje__lineaje_arg_evidence, dict) else _lineaje_arg
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        raise
    response = llm.invoke(_lineaje_arg)
    # LINEAJE: runtime guardrail checks `response` as it flows from the LLM to the agent, after the model replies (in fallback_response).
    #   Detected: this statement moves data from the LLM to the agent with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_011, AI_DAT_SEC_025, AI_DAT_SEC_027, AI_DAT_SEC_029; sensitive values in `response` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:588b9b84c0e4804226ff709fafc40a9b86e1c7a06395fb9e5dcc5549360a25ed'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:588b9b84c0e4804226ff709fafc40a9b86e1c7a06395fb9e5dcc5549360a25ed', phase='post_model', boundary={'source': 'model', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='llm', destination_type='agent', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'function': 'fallback_response', 'line': 218}, 'file': 'project/rag_agent/nodes.py', 'line': 218, 'function': 'fallback_response', 'agent_name': 'fallback_response', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:51d8bb524b745fe9'}, interaction_id=locals().get('_lineaje_interaction_id'))
    try:
        if not hasattr(_gr_client, 'enforce_reply'):
            __import__("logging").getLogger("lineaje.gr_client").error("gr_stub_client.py predates enforce_reply (STUB_API 2): this site is NOT enforced; replace gr_stub_client.py with the current companion")
            raise _gr_client.GuardrailUnavailableError("stale gr_stub_client.py: no enforce_reply")
        response = _gr_client.enforce_reply(_gr_site, response, content_type='application/json')
    except _gr_client.GuardrailUnavailableError:
        pass
    response = _name_internal_message(response, "agent_response")
    return {"messages": [response]}

def should_compress_context(state: AgentState) -> Command[Literal["compress_context", "orchestrator"]]:
    messages = state["messages"]

    new_ids: Set[str] = set()
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                if tc["name"] == "retrieve_parent_chunks":
                    raw = tc["args"].get("parent_id") or tc["args"].get("id") or tc["args"].get("ids") or []
                    if isinstance(raw, str):
                        new_ids.add(f"parent::{raw}")
                    else:
                        new_ids.update(f"parent::{r}" for r in raw)

                elif tc["name"] == "search_child_chunks":
                    query = tc["args"].get("query", "")
                    # LINEAJE: runtime guardrail checks `query` as it flows from an external API to the agent, after the tool returns (in should_compress_context).
                    #   Detected: this statement moves data from an external API to the agent with no runtime policy check (detection confidence: medium).
                    #   Decision: the Guardrail evaluates the policies enabled for this boundary; sensitive values in `query` are masked in place; a policy violation is logged and the call continues (fail_mode=ALLOW_WITH_AUDIT). If the Guardrail is unreachable, the call continues unchanged.
                    #   Do not remove without review. site_id='site:sha256:7c855a76a45d7cd6bfe7c7a3e5ec153d2f079cabd2fc6a21338652715d91cf6c'
                    _gr_client = _lineaje_load_gr_client()
                    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:7c855a76a45d7cd6bfe7c7a3e5ec153d2f079cabd2fc6a21338652715d91cf6c', phase='post_tool', boundary={'source': 'external_endpoint', 'sink': 'agent_message'}, fail_mode='ALLOW_WITH_AUDIT', source_type='api', destination_type='agent', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 110, 'name': 'rewrite_query'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'line': 237, 'function': 'should_compress_context'}, 'file': 'project/rag_agent/nodes.py', 'line': 237, 'function': 'should_compress_context', 'agent_name': 'should_compress_context', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
                    try:
                        query = _gr_client.enforce(_gr_site, query, content_type='application/json', variable_name='query', source_file=__file__, before_line=237)
                    except _gr_client.GuardrailUnavailableError:
                        pass
                    if query:
                        new_ids.add(f"search::{query}")
            break

    updated_ids = state.get("retrieval_keys", set()) | new_ids

    current_token_messages = estimate_context_tokens(messages)
    current_token_summary = estimate_context_tokens([HumanMessage(content=state.get("context_summary", ""))])
    current_tokens = current_token_messages + current_token_summary

    max_allowed = BASE_TOKEN_THRESHOLD + int(current_token_summary * TOKEN_GROWTH_FACTOR)

    goto = "compress_context" if current_tokens > max_allowed else "orchestrator"
    try:
        _lineaje_obs = _lineaje_load_gr_client()
        _lineaje_obs_site = _lineaje_obs.SiteDescriptor(site_id='site:sha256:1f97f5cebd14103663eee47ec23a1ce6a4afaa198de480b04b20014dd9c581a9', phase='', boundary={}, fail_mode='ALLOW', source_type='agent', destination_type='agent', components={'file': 'project/rag_agent/nodes.py', 'line': 251, 'function': 'should_compress_context', 'agent_name': 'should_compress_context', 'agent_name_source': 'inferred_from_function', 'call_target': 'Command', 'not_on_graph': True}, observe_only=True)
        _lineaje_obs.enforce(_lineaje_obs_site, {'activity': 'agent_to_agent'}, content_type='application/json')
    except Exception:
        pass
    return Command(
        update={
            "retrieval_keys": updated_ids,
            "retrieved_contexts": _retrieval_contexts(messages),
        },
        goto=goto,
    )

def compress_context(state: AgentState, llm):
    messages = state["messages"]
    existing_summary = state.get("context_summary", "").strip()

    if not messages:
        return {}

    conversation_text = f"USER QUESTION:\n{state.get('question')}\n\nConversation to compress:\n\n"
    if existing_summary:
        conversation_text += f"[PRIOR COMPRESSED CONTEXT]\n{existing_summary}\n\n"

    for msg in messages[1:]:
        if isinstance(msg, AIMessage):
            tool_calls_info = ""
            if getattr(msg, "tool_calls", None):
                calls = ", ".join(f"{tc['name']}({tc['args']})" for tc in msg.tool_calls)
                tool_calls_info = f" | Tool calls: {calls}"
            conversation_text += f"[ASSISTANT{tool_calls_info}]\n{msg.content or '(tool call only)'}\n\n"
        elif isinstance(msg, ToolMessage):
            tool_name = getattr(msg, "name", "tool")
            conversation_text += f"[TOOL RESULT — {tool_name}]\n{msg.content}\n\n"

    _lineaje_arg = [SystemMessage(content=get_context_compression_prompt()), HumanMessage(content=conversation_text)]
    # LINEAJE: runtime guardrail checks `_lineaje_arg` as it flows from the agent to the LLM, before it is sent to the model (in compress_context).
    #   Detected: this statement moves data from the agent to the LLM with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_AGENT_ACTIVITY_LOG, AI_APP_SEC_006, AI_APP_SEC_028, AI_APP_SEC_070 (+2 more); sensitive values in `_lineaje_arg` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:0fbae6232c865e0f2597b6569139bb0d7fdea7298de776bd66277bfddd358282'
    _lineaje__lineaje_arg_evidence = {'_lineaje_arg': _lineaje_arg, **(getattr(_lineaje_load_gr_client(), 'receiver_model', None) or (lambda o, p, f, s: {'model': f, 'model_source': s}))(llm, (), getattr(_lineaje_load_gr_client(), 'current_model', lambda _f: '')(__file__), 'guess')}
    _gr_client = _lineaje_load_gr_client()
    _lineaje_interaction_id = _gr_client.new_interaction_id()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:0fbae6232c865e0f2597b6569139bb0d7fdea7298de776bd66277bfddd358282', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 259, 'name': 'compress_context'}, 'destination': {'entity_type': 'llm', 'name': 'Qwen3-Embedding-0.6B', 'version': '', 'provider': 'qwen'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'function': 'compress_context', 'line': 281}, 'file': 'project/rag_agent/nodes.py', 'line': 281, 'function': 'compress_context', 'agent_name': 'compress_context', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:eaebdbfb040372fd'}, interaction_id=_lineaje_interaction_id)
    try:
        _lineaje__lineaje_arg_evidence = _gr_client.enforce(_gr_site, _lineaje__lineaje_arg_evidence, content_type='application/json')
        _lineaje_arg = _lineaje__lineaje_arg_evidence.get('_lineaje_arg', _lineaje_arg) if isinstance(_lineaje__lineaje_arg_evidence, dict) else _lineaje_arg
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        raise
    summary_response = llm.invoke(_lineaje_arg)
    new_summary = summary_response.content
    # LINEAJE: runtime guardrail checks `new_summary` as it flows from the LLM to the agent, after the model replies (in compress_context).
    #   Detected: this statement moves data from the LLM to the agent with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_011, AI_DAT_SEC_025, AI_DAT_SEC_027, AI_DAT_SEC_029; sensitive values in `new_summary` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:d80f5d4ed17fbb43a0fd088f3c271ef395b649f31d50e8e9eec5c838c842f055'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:d80f5d4ed17fbb43a0fd088f3c271ef395b649f31d50e8e9eec5c838c842f055', phase='post_model', boundary={'source': 'model', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='llm', destination_type='agent', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 259, 'name': 'compress_context'}, 'destination': {'entity_type': 'llm', 'name': 'Qwen3-Embedding-0.6B', 'version': '', 'provider': 'qwen'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'function': 'compress_context', 'line': 281}, 'file': 'project/rag_agent/nodes.py', 'line': 282, 'function': 'compress_context', 'agent_name': 'compress_context', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:eaebdbfb040372fd'}, interaction_id=locals().get('_lineaje_interaction_id'))
    try:
        new_summary = _gr_client.enforce(_gr_site, new_summary, content_type='application/json', variable_name='new_summary', source_file=__file__, before_line=282)
    except _gr_client.GuardrailUnavailableError:
        pass

    retrieved_ids: Set[str] = state.get("retrieval_keys", set())
    if retrieved_ids:
        parent_ids = sorted(r for r in retrieved_ids if r.startswith("parent::"))
        search_queries = sorted(r.replace("search::", "") for r in retrieved_ids if r.startswith("search::"))

        block = "\n\n---\n**Already executed (do NOT repeat):**\n"
        if parent_ids:
            block += "Parent chunks retrieved:\n" + "\n".join(f"- {p.replace('parent::', '')}" for p in parent_ids) + "\n"
        if search_queries:
            block += "Search queries already run:\n" + "\n".join(f"- {q}" for q in search_queries) + "\n"
        new_summary += block

    return {"context_summary": new_summary, "messages": [RemoveMessage(id=m.id) for m in messages[1:]]}

def collect_answer(state: AgentState):
    last_message = state["messages"][-1]
    is_valid = isinstance(last_message, AIMessage) and last_message.content and not last_message.tool_calls
    answer = last_message.content if is_valid else "Unable to generate an answer."
    return {
        "final_answer": answer,
        "agent_answers": [{
            "index": state["question_index"],
            "question": state["question"],
            "answer": answer,
            "contexts": state.get("retrieved_contexts", []),
        }]
    }
# --- End of Agent Nodes---

def aggregate_answers(state: State, llm):
    messages = state.get("messages", [])
    plain_messages = [msg for msg in messages if _is_plain_conversation_message(msg)]
    keep_ids = {getattr(msg, "id", None) for msg in plain_messages[-PRE_ANSWER_HISTORY_MESSAGES_TO_KEEP:]}
    keep_ids.discard(None)
    removals = _remove_messages_not_in(messages, keep_ids)

    if not state.get("agent_answers"):
        return {"messages": removals + [AIMessage(content="No answers were generated.")]}

    sorted_answers = sorted(state["agent_answers"], key=lambda x: x["index"])

    formatted_answers = ""
    for i, ans in enumerate(sorted_answers, start=1):
        formatted_answers += (f"\nRetrieved response {i}:\n"f"{ans['answer']}\n")

    user_message = HumanMessage(content=f"""Original user question: {state["originalQuery"]}\nRetrieved answers:{formatted_answers}""")
    _lineaje_arg = [SystemMessage(content=get_aggregation_prompt()), user_message]
    # LINEAJE: runtime guardrail checks `_lineaje_arg` as it flows from the agent to the LLM, before it is sent to the model (in aggregate_answers).
    #   Detected: this statement moves data from the agent to the LLM with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_AGENT_ACTIVITY_LOG, AI_APP_SEC_006, AI_APP_SEC_028, AI_APP_SEC_070 (+2 more); sensitive values in `_lineaje_arg` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:e7088ad5083771c453351585aa88c0a195c75cb969e878bd6f464f9fbc64ead8'
    _lineaje__lineaje_arg_evidence = {'_lineaje_arg': _lineaje_arg, **(getattr(_lineaje_load_gr_client(), 'receiver_model', None) or (lambda o, p, f, s: {'model': f, 'model_source': s}))(llm, (), getattr(_lineaje_load_gr_client(), 'current_model', lambda _f: '')(__file__), 'guess')}
    _gr_client = _lineaje_load_gr_client()
    _lineaje_interaction_id = _gr_client.new_interaction_id()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:e7088ad5083771c453351585aa88c0a195c75cb969e878bd6f464f9fbc64ead8', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 259, 'name': 'compress_context'}, 'destination': {'entity_type': 'llm', 'name': 'Qwen3-Embedding-0.6B', 'version': '', 'provider': 'qwen'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'function': 'aggregate_answers', 'line': 330}, 'file': 'project/rag_agent/nodes.py', 'line': 330, 'function': 'aggregate_answers', 'agent_name': 'aggregate_answers', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:ef4859f1432014db'}, interaction_id=_lineaje_interaction_id)
    try:
        _lineaje__lineaje_arg_evidence = _gr_client.enforce(_gr_site, _lineaje__lineaje_arg_evidence, content_type='application/json')
        _lineaje_arg = _lineaje__lineaje_arg_evidence.get('_lineaje_arg', _lineaje_arg) if isinstance(_lineaje__lineaje_arg_evidence, dict) else _lineaje_arg
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        raise
    synthesis_response = llm.invoke(_lineaje_arg)
    # LINEAJE: runtime guardrail checks `synthesis_response` as it flows from the LLM to the agent, after the model replies (in aggregate_answers).
    #   Detected: this statement moves data from the LLM to the agent with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_011, AI_DAT_SEC_025, AI_DAT_SEC_027, AI_DAT_SEC_029; sensitive values in `synthesis_response` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:c3c3f311ed483470f30a69c3200b4bb5afd75ee191dc0c51307d634cef96506c'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:c3c3f311ed483470f30a69c3200b4bb5afd75ee191dc0c51307d634cef96506c', phase='post_model', boundary={'source': 'model', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='llm', destination_type='agent', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/nodes.py', 'line': 259, 'name': 'compress_context'}, 'destination': {'entity_type': 'llm', 'name': 'Qwen3-Embedding-0.6B', 'version': '', 'provider': 'qwen'}, 'invocation': {'file': 'project/rag_agent/nodes.py', 'function': 'aggregate_answers', 'line': 330}, 'file': 'project/rag_agent/nodes.py', 'line': 330, 'function': 'aggregate_answers', 'agent_name': 'aggregate_answers', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:ef4859f1432014db'}, interaction_id=locals().get('_lineaje_interaction_id'))
    try:
        if not hasattr(_gr_client, 'enforce_reply'):
            __import__("logging").getLogger("lineaje.gr_client").error("gr_stub_client.py predates enforce_reply (STUB_API 2): this site is NOT enforced; replace gr_stub_client.py with the current companion")
            raise _gr_client.GuardrailUnavailableError("stale gr_stub_client.py: no enforce_reply")
        synthesis_response = _gr_client.enforce_reply(_gr_site, synthesis_response, content_type='application/json')
    except _gr_client.GuardrailUnavailableError:
        pass
    return {"messages": removals + [AIMessage(content=synthesis_response.content)]}
