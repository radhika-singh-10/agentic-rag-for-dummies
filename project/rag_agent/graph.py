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

from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode
from functools import partial

from .graph_state import State, AgentState
from core.execution_logger import logged_node
from .nodes import (
    aggregate_answers,
    collect_answer,
    compress_context,
    fallback_response,
    orchestrator,
    request_clarification,
    rewrite_query,
    should_compress_context,
    summarize_history,
)
from .edges import route_after_orchestrator_call, route_after_rewrite

def create_agent_graph(llm, tools_list):
    # LINEAJE: runtime guardrail checks `tools_list` as it flows from the agent to the LLM, before it is sent to the model (in create_agent_graph).
    #   Detected: this statement moves data from the agent to the LLM with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_AGENT_ACTIVITY_LOG, AI_APP_SEC_006, AI_APP_SEC_028, AI_APP_SEC_070 (+2 more); sensitive values in `tools_list` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:79b02e8283961461bba04c0539e44cdf1d3dbd08564c391cf9c44ddcaf21391f'
    _gr_client = _lineaje_load_gr_client()
    _lineaje_interaction_id = _gr_client.new_interaction_id()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:79b02e8283961461bba04c0539e44cdf1d3dbd08564c391cf9c44ddcaf21391f', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', components={'source': {'entity_type': 'agent', 'file_path': 'project/rag_agent/graph.py', 'line': 21, 'name': 'create_agent_graph', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY'}, 'invocation': {'file': 'project/rag_agent/graph.py', 'function': 'create_agent_graph', 'line': 22}, 'destination': {'entity_type': 'llm', 'name': 'granite4.1:8b', 'provider': '', 'version': ''}, 'file': 'project/rag_agent/graph.py', 'line': 22, 'function': 'create_agent_graph', 'agent_name': 'create_agent_graph', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:dbbed356696ceb10'}, interaction_id=_lineaje_interaction_id)
    try:
        tools_list = _gr_client.enforce(_gr_site, tools_list, content_type='application/json', variable_name='tools_list', source_file=__file__, before_line=22)
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        raise
    llm_with_tools = llm.bind_tools(tools_list)
    # LINEAJE: runtime guardrail checks `llm_with_tools` as it flows from the LLM to the agent, after the model replies (in create_agent_graph).
    #   Detected: this statement moves data from the LLM to the agent with no runtime policy check (detection confidence: medium).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_011, AI_DAT_SEC_025, AI_DAT_SEC_027, AI_DAT_SEC_029; sensitive values in `llm_with_tools` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:c790093a8804801b71cb24a12965d2b245989a4e518811f20cf40521aa5659b5'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:c790093a8804801b71cb24a12965d2b245989a4e518811f20cf40521aa5659b5', phase='post_model', boundary={'source': 'model', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='llm', destination_type='agent', components={'source': {'entity_type': 'agent', 'file_path': 'project/rag_agent/graph.py', 'line': 21, 'name': 'create_agent_graph', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY'}, 'invocation': {'file': 'project/rag_agent/graph.py', 'function': 'create_agent_graph', 'line': 22}, 'destination': {'entity_type': 'llm', 'name': 'granite4.1:8b', 'provider': '', 'version': ''}, 'file': 'project/rag_agent/graph.py', 'line': 22, 'function': 'create_agent_graph', 'agent_name': 'create_agent_graph', 'agent_name_source': 'inferred_from_function', 'boundary_id': 'bnd:dbbed356696ceb10'}, interaction_id=locals().get('_lineaje_interaction_id'))
    try:
        llm_with_tools = _gr_client.enforce(_gr_site, llm_with_tools, content_type='application/json', variable_name='llm_with_tools', source_file=__file__, before_line=22)
    except _gr_client.GuardrailUnavailableError:
        pass
    tool_node = ToolNode(tools_list)

    checkpointer = InMemorySaver()

    _lineaje_payload = "Compiling agent graph..."
    # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the application log, before it is written to the log (in create_agent_graph).
    #   Detected: this statement moves data from the agent to the application log with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_010; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:77b1c0780bf36d75b457f17d1d227f07edc4b3717f2086614ac5bb92efa3901c'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:77b1c0780bf36d75b457f17d1d227f07edc4b3717f2086614ac5bb92efa3901c', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/graph.py', 'line': 21, 'name': 'create_agent_graph'}, 'invocation': {'file': 'project/rag_agent/graph.py', 'line': 27, 'function': 'create_agent_graph'}, 'file': 'project/rag_agent/graph.py', 'line': 27, 'function': 'create_agent_graph', 'agent_name': 'create_agent_graph', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    print(_lineaje_payload)
    agent_builder = StateGraph(AgentState)
    agent_builder.add_node("orchestrator", logged_node("agent.orchestrator", partial(orchestrator, llm_with_tools=llm_with_tools)))
    agent_builder.add_node("tools", tool_node)
    agent_builder.add_node("compress_context", logged_node("agent.compress_context", partial(compress_context, llm=llm)))
    agent_builder.add_node("fallback_response", logged_node("agent.fallback_response", partial(fallback_response, llm=llm)))
    agent_builder.add_node("should_compress_context", logged_node("agent.should_compress_context", should_compress_context))
    agent_builder.add_node("collect_answer", logged_node("agent.collect_answer", collect_answer))

    agent_builder.add_edge(START, "orchestrator")
    agent_builder.add_conditional_edges("orchestrator", route_after_orchestrator_call, {"tools": "tools", "fallback_response": "fallback_response", "collect_answer": "collect_answer"})
    agent_builder.add_edge("tools", "should_compress_context")
    agent_builder.add_edge("compress_context", "orchestrator")
    agent_builder.add_edge("fallback_response", "collect_answer")
    agent_builder.add_edge("collect_answer", END)

    agent_subgraph = agent_builder.compile()

    graph_builder = StateGraph(State)
    graph_builder.add_node("summarize_history", logged_node("main.summarize_history", partial(summarize_history, llm=llm)))
    graph_builder.add_node("rewrite_query", logged_node("main.rewrite_query", partial(rewrite_query, llm=llm)))
    graph_builder.add_node("request_clarification", logged_node("main.request_clarification", request_clarification))
    graph_builder.add_node("agent", agent_subgraph)
    graph_builder.add_node("aggregate_answers", logged_node("main.aggregate_answers", partial(aggregate_answers, llm=llm)))

    graph_builder.add_edge(START, "summarize_history")
    graph_builder.add_edge("summarize_history", "rewrite_query")
    graph_builder.add_conditional_edges("rewrite_query", route_after_rewrite)
    graph_builder.add_edge("request_clarification", "rewrite_query")
    graph_builder.add_edge(["agent"], "aggregate_answers")
    graph_builder.add_edge("aggregate_answers", END)

    agent_graph = graph_builder.compile(checkpointer=checkpointer, interrupt_before=["request_clarification"])

    _lineaje_payload = "✓ Agent graph compiled successfully."
    # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the application log, before it is written to the log (in create_agent_graph).
    #   Detected: this statement moves data from the agent to the application log with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_010; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:f7ec054d22e79c18babe2aee517e289ce07b982585e692aea7ad0e21ff1c9c4d'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:f7ec054d22e79c18babe2aee517e289ce07b982585e692aea7ad0e21ff1c9c4d', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/graph.py', 'line': 21, 'name': 'create_agent_graph'}, 'invocation': {'file': 'project/rag_agent/graph.py', 'line': 61, 'function': 'create_agent_graph'}, 'file': 'project/rag_agent/graph.py', 'line': 61, 'function': 'create_agent_graph', 'agent_name': 'create_agent_graph', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    print(_lineaje_payload)
    # LINEAJE: runtime guardrail checks `agent_graph` as it flows from the agent to the user interface, before it leaves the application (in create_agent_graph).
    #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `agent_graph` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:92c66ffd4da2f7b31ab603d606090912590267da803c6a1f40a521f742255a6f'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:92c66ffd4da2f7b31ab603d606090912590267da803c6a1f40a521f742255a6f', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/rag_agent/graph.py', 'line': 21, 'name': 'create_agent_graph'}, 'invocation': {'file': 'project/rag_agent/graph.py', 'line': 62, 'function': 'create_agent_graph'}, 'file': 'project/rag_agent/graph.py', 'line': 62, 'function': 'create_agent_graph', 'agent_name': 'create_agent_graph', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        agent_graph = _gr_client.enforce(_gr_site, agent_graph, content_type='text/plain')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    return agent_graph
