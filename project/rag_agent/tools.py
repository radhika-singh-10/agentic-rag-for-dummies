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

from langchain_core.tools import tool
import config
from db.parent_store_manager import ParentStoreManager
from core.execution_logger import log_error, log_tool_end, log_tool_start

class ToolFactory:
    
    def __init__(self, collection):
        self.collection = collection
        self.parent_store_manager = ParentStoreManager()
    
    def _search_child_chunks(self, query: str, limit: int = config.DEFAULT_RETRIEVAL_K) -> str:
        """Search document excerpts for evidence related to the user question.

        Use this as the first retrieval step. Results include parent IDs, file
        names, and short child-chunk excerpts. If excerpts are relevant but too
        fragmented to answer confidently, call retrieve_parent_chunks with the
        returned parent_id.
        
        Args:
            query: Focused search query with concrete keywords from the question.
            limit: Maximum number of child chunks to return.
        """
        log_tool_start("search_child_chunks", {"query": query, "limit": limit})
        try:
            results = self.collection.similarity_search(
                query,
                k=limit,
                score_threshold=config.RETRIEVAL_SCORE_THRESHOLD,
            )
            # LINEAJE: runtime guardrail checks `results` as it flows from a vector store to the agent, after the tool returns (in ToolFactory._search_child_chunks).
            #   Detected: this statement moves data from a vector store to the agent with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates the policies enabled for this boundary; sensitive values in `results` are masked in place; a policy violation is logged and the call continues (fail_mode=ALLOW_WITH_AUDIT). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:7e820bcba072b0a10359ce777d4c1536a86acf10bc642c0c67ee1c0a5095470f'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:7e820bcba072b0a10359ce777d4c1536a86acf10bc642c0c67ee1c0a5095470f', phase='post_tool', boundary={'source': 'vector_store', 'sink': 'agent_context'}, fail_mode='ALLOW_WITH_AUDIT', source_type='vector_store', destination_type='agent', components={'destination': {'entity_type': 'rag', 'file_path': 'project/config.py', 'line': 11, 'name': 'document_child_chunks', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY'}, 'invocation': {'file': 'project/rag_agent/tools.py', 'function': 'ToolFactory._search_child_chunks', 'line': 26}, 'source': {'entity_type': 'agent', 'file_path': 'project/rag_agent/graph.py', 'line': 21, 'name': 'create_agent_graph', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY'}, 'file': 'project/rag_agent/tools.py', 'line': 26, 'function': '_search_child_chunks', 'agent_name': 'ToolFactory', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:b1fcef92e0601bad'})
            try:
                results = _gr_client.enforce(_gr_site, results, content_type='application/json', variable_name='results', source_file=__file__, before_line=26)
            except _gr_client.GuardrailUnavailableError:
                pass
            if not results:
                output = "NO_RELEVANT_CHUNKS"
                log_tool_end("search_child_chunks", output)
                # LINEAJE: runtime guardrail checks `output` as it flows from the agent to the user interface, before it leaves the application (in ToolFactory._search_child_chunks).
                #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
                #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `output` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
                #   Do not remove without review. site_id='site:sha256:fadc6196c1c432b7dab6bf2ddec84b761cabcdddb7e1f4e6a7021edcfa878195'
                _gr_client = _lineaje_load_gr_client()
                _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:fadc6196c1c432b7dab6bf2ddec84b761cabcdddb7e1f4e6a7021edcfa878195', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/rag_agent/tools.py', 'line': 34, 'function': 'ToolFactory._search_child_chunks'}, 'file': 'project/rag_agent/tools.py', 'line': 34, 'function': '_search_child_chunks', 'agent_name': 'ToolFactory', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
                try:
                    output = _gr_client.enforce(_gr_site, output, content_type='text/plain')
                except _gr_client.GuardrailUnavailableError:
                    pass
                except PermissionError:
                    pass
                return output

            output = config.CHILD_CHUNK_SEPARATOR.join([
                f"Parent ID: {doc.metadata.get('parent_id', '')}\n"
                f"File Name: {doc.metadata.get('source', '')}\n"
                f"Content: {doc.page_content.strip()}"
                for doc in results
            ])
            log_tool_end("search_child_chunks", output)
            # LINEAJE: runtime guardrail checks `output` as it flows from the agent to the user interface, before it leaves the application (in ToolFactory._search_child_chunks).
            #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `output` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:d2733523b3f0af8d47e85451a62226954e95ab8020fb9c57c9206767128702ea'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:d2733523b3f0af8d47e85451a62226954e95ab8020fb9c57c9206767128702ea', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/rag_agent/tools.py', 'line': 43, 'function': 'ToolFactory._search_child_chunks'}, 'file': 'project/rag_agent/tools.py', 'line': 43, 'function': '_search_child_chunks', 'agent_name': 'ToolFactory', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                output = _gr_client.enforce(_gr_site, output, content_type='text/plain')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            return output

        except Exception as e:
            log_error("search_child_chunks", e)
            output = f"RETRIEVAL_ERROR: {str(e)}"
            log_tool_end("search_child_chunks", output)
            # LINEAJE: runtime guardrail checks `output` as it flows from the agent to the user interface, before it leaves the application (in ToolFactory._search_child_chunks).
            #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `output` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:c659f23b36ab240e322ade3747590042aa3e65b3115f27f6cb2c967ca8c449fe'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:c659f23b36ab240e322ade3747590042aa3e65b3115f27f6cb2c967ca8c449fe', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/rag_agent/tools.py', 'line': 49, 'function': 'ToolFactory._search_child_chunks'}, 'file': 'project/rag_agent/tools.py', 'line': 49, 'function': '_search_child_chunks', 'agent_name': 'ToolFactory', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                output = _gr_client.enforce(_gr_site, output, content_type='text/plain')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            return output
    
    def _retrieve_parent_chunks(self, parent_id: str) -> str:
        """Retrieve the full parent chunk for a relevant child search result.

        Use this only after search_child_chunks returns a relevant parent_id and
        the child excerpt needs more surrounding context. Do not call this for
        parent IDs already available in compressed context.
    
        Args:
            parent_id: Parent chunk ID returned by search_child_chunks.
        """
        log_tool_start("retrieve_parent_chunks", {"parent_id": parent_id})
        try:
            parent = self.parent_store_manager.load_content(parent_id)
            if not parent:
                output = "NO_PARENT_DOCUMENT"
                log_tool_end("retrieve_parent_chunks", output)
                # LINEAJE: runtime guardrail checks `output` as it flows from the agent to the user interface, before it leaves the application (in ToolFactory._retrieve_parent_chunks).
                #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
                #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `output` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
                #   Do not remove without review. site_id='site:sha256:dd71fc20bca2290e2a9730e60125c9b10a232ee5a29ef2e4c68b7e0b048d41e6'
                _gr_client = _lineaje_load_gr_client()
                _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:dd71fc20bca2290e2a9730e60125c9b10a232ee5a29ef2e4c68b7e0b048d41e6', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/rag_agent/tools.py', 'line': 67, 'function': 'ToolFactory._retrieve_parent_chunks'}, 'file': 'project/rag_agent/tools.py', 'line': 67, 'function': '_retrieve_parent_chunks', 'agent_name': 'ToolFactory', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
                try:
                    output = _gr_client.enforce(_gr_site, output, content_type='text/plain')
                except _gr_client.GuardrailUnavailableError:
                    pass
                except PermissionError:
                    pass
                return output

            output = (
                f"Parent ID: {parent.get('parent_id', 'n/a')}\n"
                f"File Name: {parent.get('metadata', {}).get('source', 'unknown')}\n"
                f"Content: {parent.get('content', '').strip()}"
            )
            log_tool_end("retrieve_parent_chunks", output)
            # LINEAJE: runtime guardrail checks `output` as it flows from the agent to the user interface, before it leaves the application (in ToolFactory._retrieve_parent_chunks).
            #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `output` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:0381246abe0c50bd1c993e179d798a3afd8b5c149fad66bb8d73943eb609e6a5'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:0381246abe0c50bd1c993e179d798a3afd8b5c149fad66bb8d73943eb609e6a5', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/rag_agent/tools.py', 'line': 75, 'function': 'ToolFactory._retrieve_parent_chunks'}, 'file': 'project/rag_agent/tools.py', 'line': 75, 'function': '_retrieve_parent_chunks', 'agent_name': 'ToolFactory', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                output = _gr_client.enforce(_gr_site, output, content_type='text/plain')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            return output

        except Exception as e:
            log_error("retrieve_parent_chunks", e)
            output = f"PARENT_RETRIEVAL_ERROR: {str(e)}"
            log_tool_end("retrieve_parent_chunks", output)
            # LINEAJE: runtime guardrail checks `output` as it flows from the agent to the user interface, before it leaves the application (in ToolFactory._retrieve_parent_chunks).
            #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `output` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:91079f74a7b3dccad81721182a67eb2d4daaeda5e801c9764f030293c9f434f9'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:91079f74a7b3dccad81721182a67eb2d4daaeda5e801c9764f030293c9f434f9', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/rag_agent/tools.py', 'line': 81, 'function': 'ToolFactory._retrieve_parent_chunks'}, 'file': 'project/rag_agent/tools.py', 'line': 81, 'function': '_retrieve_parent_chunks', 'agent_name': 'ToolFactory', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                output = _gr_client.enforce(_gr_site, output, content_type='text/plain')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            return output
    
    def create_tools(self) -> list:
        """Create and return the list of tools."""
        search_tool = tool("search_child_chunks")(self._search_child_chunks)
        retrieve_tool = tool("retrieve_parent_chunks")(self._retrieve_parent_chunks)
        
        return [search_tool, retrieve_tool]
