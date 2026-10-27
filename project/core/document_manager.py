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

from pathlib import Path
import shutil
import config
from utils import pdfs_to_markdowns, clear_directory_contents

class DocumentManager:

    def __init__(self, rag_system):
        self.rag_system = rag_system
        self.markdown_dir = Path(config.MARKDOWN_DIR)
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        
    def add_documents(self, document_paths, progress_callback=None):
        if not document_paths:
            return 0, 0
            
        document_paths = [document_paths] if isinstance(document_paths, str) else document_paths
        document_paths = [p for p in document_paths if p and Path(p).suffix.lower() in [".pdf", ".md"]]
        
        if not document_paths:
            return 0, 0
            
        added = 0
        skipped = 0
            
        for i, doc_path in enumerate(document_paths):
            if progress_callback:
                progress_callback((i + 1) / len(document_paths), f"Processing {Path(doc_path).name}")
                
            source_path = Path(doc_path)
            doc_name = source_path.stem
            md_path = self.markdown_dir / f"{doc_name}.md"
            
            if md_path.exists():
                skipped += 1
                continue
                
            parent_ids = []
            try:
                if source_path.suffix.lower() == ".md":
                    shutil.copy(source_path, md_path)
                else:
                    pdfs_to_markdowns(str(source_path), overwrite=False)
                parent_chunks, child_chunks = self.rag_system.chunker.create_chunks_single(
                    md_path,
                    source_name=source_path.name,
                )
                
                if not child_chunks:
                    raise ValueError("No child chunks were created.")
                
                parent_ids = [parent_id for parent_id, _ in parent_chunks]
                self.rag_system.parent_store.save_many(parent_chunks)
                collection = self.rag_system.vector_db.get_collection(self.rag_system.collection_name)
                # LINEAJE: runtime guardrail checks `child_chunks` as it flows from the RAG pipeline to a vector store, before the tool runs (in DocumentManager.add_documents).
                #   Detected: this statement moves data from the RAG pipeline to a vector store with no runtime policy check (detection confidence: high).
                #   Decision: the Guardrail evaluates the policies enabled for this boundary; sensitive values in `child_chunks` are masked in place; a policy violation is logged and the call continues (fail_mode=ALLOW_WITH_AUDIT). If the Guardrail is unreachable, the call continues unchanged.
                #   Do not remove without review. site_id='site:sha256:075dbe83bd6e9213f079e1d8e18a2bb0fedc5723f795b3b99289e3fd51463ef2'
                _gr_client = _lineaje_load_gr_client()
                _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:075dbe83bd6e9213f079e1d8e18a2bb0fedc5723f795b3b99289e3fd51463ef2', phase='pre_tool', boundary={'source': 'rag_pipeline', 'sink': 'vector_store'}, fail_mode='ALLOW_WITH_AUDIT', source_type='rag_pipeline', destination_type='vector_store', components={'invocation': {'file': 'project/core/document_manager.py', 'line': 55, 'function': 'DocumentManager.add_documents'}, 'file': 'project/core/document_manager.py', 'line': 55, 'function': 'add_documents', 'agent_name': 'DocumentManager', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
                try:
                    child_chunks = _gr_client.enforce(_gr_site, child_chunks, content_type='application/json', variable_name='child_chunks', source_file=__file__, before_line=55)
                except _gr_client.GuardrailUnavailableError:
                    pass
                collection.add_documents(child_chunks)
                
                added += 1
                
            except Exception as e:
                self.rag_system.parent_store.delete_many(parent_ids)
                if md_path.exists():
                    md_path.unlink()
                _lineaje_payload = f"Error processing {doc_path}: {e}"
                # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the application log, before it is written to the log (in DocumentManager.add_documents).
                #   Detected: this statement moves data from the agent to the application log with no runtime policy check (detection confidence: high).
                #   Decision: the Guardrail evaluates AI_DAT_SEC_010; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
                #   Do not remove without review. site_id='site:sha256:cca137a3cfae917d01cd8adf261c93b1f8af4bc0880cc00f2c20d2ad5a5003ef'
                _gr_client = _lineaje_load_gr_client()
                _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:cca137a3cfae917d01cd8adf261c93b1f8af4bc0880cc00f2c20d2ad5a5003ef', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', components={'invocation': {'file': 'project/core/document_manager.py', 'line': 63, 'function': 'DocumentManager.add_documents'}, 'file': 'project/core/document_manager.py', 'line': 63, 'function': 'add_documents', 'agent_name': 'DocumentManager', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
                try:
                    _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
                except _gr_client.GuardrailUnavailableError:
                    pass
                except PermissionError:
                    pass
                print(_lineaje_payload)
                skipped += 1
            
        return added, skipped
    
    def get_markdown_files(self):
        sources = self.rag_system.parent_store.list_sources()
        if sources:
            # LINEAJE: runtime guardrail checks `sources` as it flows from the agent to the user interface, before it leaves the application (in DocumentManager.get_markdown_files).
            #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `sources` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:9ac2a5a9efbe2d04dce2c34893331c49966346ec1477de9c953a416d4c249aa5'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:9ac2a5a9efbe2d04dce2c34893331c49966346ec1477de9c953a416d4c249aa5', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/core/document_manager.py', 'line': 71, 'function': 'DocumentManager.get_markdown_files'}, 'file': 'project/core/document_manager.py', 'line': 71, 'function': 'get_markdown_files', 'agent_name': 'DocumentManager', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                sources = _gr_client.enforce(_gr_site, sources, content_type='text/plain')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            return sources
        return sorted(p.name for p in self.markdown_dir.glob("*.md"))
    
    def clear_all(self):
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        self.rag_system.vector_db.delete_collection(self.rag_system.collection_name)

        clear_directory_contents(self.markdown_dir)
        self.rag_system.parent_store.clear_store()

        self.rag_system.vector_db.create_collection(self.rag_system.collection_name)
