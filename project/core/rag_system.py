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

import uuid
from langchain_ollama import ChatOllama
import config
from db.vector_db_manager import VectorDbManager
from db.parent_store_manager import ParentStoreManager
from document_chunker import DocumentChunker
from rag_agent.tools import ToolFactory
from rag_agent.graph import create_agent_graph
from core.observability import Observability

class RAGSystem:

    def __init__(self, collection_name=config.CHILD_COLLECTION):
        self.collection_name = collection_name
        self.vector_db = VectorDbManager()
        self.parent_store = ParentStoreManager()
        self.chunker = DocumentChunker()
        self.observability = Observability()
        self.agent_graph = None
        self.thread_id = str(uuid.uuid4())
        self.recursion_limit = config.GRAPH_RECURSION_LIMIT

    def initialize(self):
        self.vector_db.create_collection(self.collection_name)
        collection = self.vector_db.get_collection(self.collection_name)

        # LINEAJE: runtime guardrail checks the model this client is built with as it flows from the agent to the LLM, before it is sent to the model (in RAGSystem.initialize).
        #   Detected: this statement moves data from the agent to the LLM with no runtime policy check (detection confidence: medium).
        #   Decision: the Guardrail evaluates AI_AGENT_ACTIVITY_LOG, AI_APP_SEC_006, AI_APP_SEC_028, AI_APP_SEC_070 (+1 more); a model that is not approved is refused before the client is built (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:f1b6fa7bacd41d0343dfb8bb488aa9c42db76105e519b8a5b66431f24b7f5725'
        _lineaje_model_evidence = {'model': config.LLM_MODEL, 'client': 'ChatOllama', 'provider': 'langchain_ollama', 'model_source': 'call_kwarg', 'project': 'tree'}
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:f1b6fa7bacd41d0343dfb8bb488aa9c42db76105e519b8a5b66431f24b7f5725', phase='pre_model', boundary={'source': 'agent_config', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/core/rag_system.py', 'line': 11, 'name': 'RAGSystem'}, 'invocation': {'file': 'project/core/rag_system.py', 'function': 'RAGSystem.initialize', 'line': 27}, 'destination': {'entity_type': 'llm', 'name': 'granite4.1:8b', 'provider': '', 'version': ''}, 'file': 'project/core/rag_system.py', 'line': 27, 'function': 'initialize', 'agent_name': 'RAGSystem', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:a0a84b60e3efaf64'})
        try:
            _lineaje_model_evidence = _gr_client.enforce(_gr_site, _lineaje_model_evidence, content_type='application/json')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            raise
        llm = ChatOllama(
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            seed=config.LLM_SEED,
        )
        tools = ToolFactory(collection).create_tools()
        # LINEAJE: runtime guardrail checks `llm` as it flows from the agent to the agent, before the agent sends it (in RAGSystem.initialize).
        #   Detected: this statement moves data from the agent to the agent with no runtime policy check (detection confidence: medium).
        #   Decision: the Guardrail evaluates the policies enabled for this boundary; sensitive values in `llm` are masked in place; a policy violation is logged and the call continues (fail_mode=ALLOW_WITH_AUDIT). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:d1febb40b198adf7b5d60da9708401201020366d44ad41641935596cfd0d25ca'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:d1febb40b198adf7b5d60da9708401201020366d44ad41641935596cfd0d25ca', phase='pre_agent_send', boundary={'source': 'agent_message', 'sink': 'agent_message'}, fail_mode='ALLOW_WITH_AUDIT', source_type='agent', destination_type='agent', components={'source': {'entity_type': 'agent', 'file_path': 'project/core/rag_system.py', 'line': 11, 'name': 'RAGSystem', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY'}, 'invocation': {'file': 'project/core/rag_system.py', 'function': 'RAGSystem.initialize', 'line': 33}, 'destination': {'entity_type': 'agent', 'file_path': 'project/rag_agent/graph.py', 'line': 21, 'name': 'create_agent_graph', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY'}, 'file': 'project/core/rag_system.py', 'line': 33, 'function': 'initialize', 'agent_name': 'RAGSystem', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:cd5f62188495438f'})
        try:
            llm = _gr_client.enforce(_gr_site, llm, content_type='application/json', variable_name='llm', source_file=__file__, before_line=33)
        except _gr_client.GuardrailUnavailableError:
            pass
        self.agent_graph = create_agent_graph(llm, tools)
        # LINEAJE: runtime guardrail checks `self.agent_graph` as it flows from the LLM to the agent, after the model replies (in RAGSystem.initialize).
        #   Detected: this statement moves data from the LLM to the agent with no runtime policy check (detection confidence: medium).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_011, AI_DAT_SEC_025, AI_DAT_SEC_027, AI_DAT_SEC_029; sensitive values in `self.agent_graph` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:4b16adf6e9bef6e7cdf704f3e59e270ee1aaf63db95119fb1d60ba1eb523e4e2'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:4b16adf6e9bef6e7cdf704f3e59e270ee1aaf63db95119fb1d60ba1eb523e4e2', phase='post_model', boundary={'source': 'model', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='llm', destination_type='agent', components={'source': {'entity_type': 'agent', 'file_path': 'project/core/rag_system.py', 'line': 11, 'name': 'RAGSystem', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY'}, 'invocation': {'file': 'project/core/rag_system.py', 'function': 'RAGSystem.initialize', 'line': 33}, 'destination': {'entity_type': 'llm', 'name': 'granite4.1:8b', 'provider': '', 'version': ''}, 'file': 'project/core/rag_system.py', 'line': 33, 'function': 'initialize', 'agent_name': 'RAGSystem', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:30f18bcabc9cbbe3'}, interaction_id=locals().get('_lineaje_interaction_id'))
        try:
            self.agent_graph = _gr_client.enforce(_gr_site, self.agent_graph, content_type='application/json', variable_name='self.agent_graph', source_file=__file__, before_line=33)
        except _gr_client.GuardrailUnavailableError:
            pass

    def get_config(self):
        cfg = {"configurable": {"thread_id": self.thread_id}, "recursion_limit": self.recursion_limit}
        handler = self.observability.get_handler()
        if handler:
            cfg["callbacks"] = [handler]
        # LINEAJE: runtime guardrail checks `cfg` as it flows from the agent to the user interface, before it leaves the application (in RAGSystem.get_config).
        #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `cfg` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:be14d1e014f36ecfd106bb22e660801188ce7e56c82c71b92af6ee9238564e87'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:be14d1e014f36ecfd106bb22e660801188ce7e56c82c71b92af6ee9238564e87', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/core/rag_system.py', 'line': 11, 'name': 'RAGSystem'}, 'invocation': {'file': 'project/core/rag_system.py', 'line': 40, 'function': 'RAGSystem.get_config'}, 'file': 'project/core/rag_system.py', 'line': 40, 'function': 'get_config', 'agent_name': 'RAGSystem', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
        try:
            cfg = _gr_client.enforce(_gr_site, cfg, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return cfg

    def reset_thread(self):
        try:
            self.agent_graph.checkpointer.delete_thread(self.thread_id)
        except Exception as e:
            _lineaje_payload = f"Warning: Could not delete thread {self.thread_id}: {e}"
            # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the application log, before it is written to the log (in RAGSystem.reset_thread).
            #   Detected: this statement moves data from the agent to the application log with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates AI_DAT_SEC_010; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:cdd7c11ea978e80f60fcda10b7f91d12ec999865401be0eb3081766892aa0d2a'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:cdd7c11ea978e80f60fcda10b7f91d12ec999865401be0eb3081766892aa0d2a', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'file_path': 'project/core/rag_system.py', 'line': 11, 'name': 'RAGSystem'}, 'invocation': {'file': 'project/core/rag_system.py', 'line': 46, 'function': 'RAGSystem.reset_thread'}, 'file': 'project/core/rag_system.py', 'line': 46, 'function': 'reset_thread', 'agent_name': 'RAGSystem', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            print(_lineaje_payload)
        self.thread_id = str(uuid.uuid4())
