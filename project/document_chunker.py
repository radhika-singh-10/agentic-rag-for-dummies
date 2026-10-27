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

import os
import glob
import config
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

class DocumentChunker:
    def __init__(self):
        if config.MIN_PARENT_SIZE <= 0 or config.MAX_PARENT_SIZE < config.MIN_PARENT_SIZE:
            raise ValueError("Parent chunk sizes must be positive and MIN_PARENT_SIZE <= MAX_PARENT_SIZE.")
        if not 0 <= config.CHILD_CHUNK_OVERLAP < config.CHILD_CHUNK_SIZE:
            raise ValueError("CHILD_CHUNK_OVERLAP must be smaller than CHILD_CHUNK_SIZE.")
        if config.CHILD_CHUNK_OVERLAP >= config.MAX_PARENT_SIZE:
            raise ValueError("CHILD_CHUNK_OVERLAP must be smaller than MAX_PARENT_SIZE.")

        self.__parent_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=config.HEADERS_TO_SPLIT_ON, 
            strip_headers=False
        )
        self.__child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHILD_CHUNK_SIZE, 
            chunk_overlap=config.CHILD_CHUNK_OVERLAP
        )
        self.__min_parent_size = config.MIN_PARENT_SIZE
        self.__max_parent_size = config.MAX_PARENT_SIZE

    @staticmethod
    def __merge_metadata(target, source, prepend=False):
        for key, value in source.items():
            if key not in target:
                target[key] = value
            else:
                first, second = (value, target[key]) if prepend else (target[key], value)
                values = [
                    item.strip()
                    for raw in (first, second)
                    for item in str(raw).split(" -> ")
                    if item.strip()
                ]
                target[key] = " -> ".join(dict.fromkeys(values))

    def create_chunks(self, path_dir=config.MARKDOWN_DIR):
        all_parent_chunks, all_child_chunks = [], []

        for doc_path_str in sorted(glob.glob(os.path.join(path_dir, "*.md"))):
            doc_path = Path(doc_path_str)
            parent_chunks, child_chunks = self.create_chunks_single(doc_path)
            all_parent_chunks.extend(parent_chunks)
            all_child_chunks.extend(child_chunks)
        
        return all_parent_chunks, all_child_chunks

    def create_chunks_single(self, md_path, source_name=None):
        doc_path = Path(md_path)
        source_name = source_name or f"{doc_path.stem}.pdf"
        
        with open(doc_path, "r", encoding="utf-8") as f:
            # LINEAJE: runtime guardrail checks `f` as it flows from file storage to the agent (in DocumentChunker.create_chunks_single).
            #   Detected: this statement moves data from file storage to the agent with no runtime policy check (detection confidence: medium).
            #   Decision: the Guardrail evaluates AI_APP_SEC_070, AI_DAT_SEC_023, AI_DAT_SEC_024; sensitive values in `f` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:22ccf174b4439843c34410689582bb0ad4f665c559ac691582033a818f686fc4'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:22ccf174b4439843c34410689582bb0ad4f665c559ac691582033a818f686fc4', phase='file_upload', boundary={'source': 'file_upload', 'sink': 'agent_context'}, fail_mode='BLOCK', source_type='file_storage', destination_type='agent', components={'invocation': {'file': 'project/document_chunker.py', 'line': 58, 'function': 'DocumentChunker.create_chunks_single'}, 'file': 'project/document_chunker.py', 'line': 58, 'function': 'create_chunks_single', 'agent_name': 'DocumentChunker', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                f = _gr_client.enforce(_gr_site, f, content_type='application/json')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                raise
            _lineaje_payload = f.read()
            # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from rag source to the RAG pipeline, before the tool runs (in DocumentChunker.create_chunks_single).
            #   Detected: this statement moves data from rag source to the RAG pipeline with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates the policies enabled for this boundary; sensitive values in `_lineaje_payload` are masked in place; a policy violation is logged and the call continues (fail_mode=ALLOW_WITH_AUDIT). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:0c9e5e43913faa308b80743c45cecfb66d1156c323c02480baad70553a199a6a'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:0c9e5e43913faa308b80743c45cecfb66d1156c323c02480baad70553a199a6a', phase='pre_tool', boundary={'source': 'rag_source', 'sink': 'rag_pipeline'}, fail_mode='ALLOW_WITH_AUDIT', source_type='rag_source', destination_type='rag_pipeline', components={'invocation': {'file': 'project/document_chunker.py', 'line': 58, 'function': 'DocumentChunker.create_chunks_single'}, 'file': 'project/document_chunker.py', 'line': 58, 'function': 'create_chunks_single', 'agent_name': 'DocumentChunker', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json', variable_name='_lineaje_payload', source_file=__file__, before_line=58)
            except _gr_client.GuardrailUnavailableError:
                pass
            parent_chunks = self.__parent_splitter.split_text(_lineaje_payload)
        
        merged_parents = self.__merge_small_parents(parent_chunks)
        split_parents = self.__split_large_parents(merged_parents)
        cleaned_parents = self.__clean_small_chunks(split_parents)
        if any(len(chunk.page_content) > self.__max_parent_size for chunk in cleaned_parents):
            raise ValueError("Parent chunking produced a chunk larger than MAX_PARENT_SIZE.")
        
        all_parent_chunks, all_child_chunks = [], []
        self.__create_child_chunks(
            all_parent_chunks,
            all_child_chunks,
            cleaned_parents,
            doc_path,
            source_name,
        )
        return all_parent_chunks, all_child_chunks

    def __merge_small_parents(self, chunks):
        if not chunks:
            return []
        
        merged, current = [], None
        
        for chunk in chunks:
            if current is None:
                current = chunk
            else:
                current.page_content += "\n\n" + chunk.page_content
                self.__merge_metadata(current.metadata, chunk.metadata)

            if len(current.page_content) >= self.__min_parent_size:
                merged.append(current)
                current = None
        
        if current:
            if merged:
                merged[-1].page_content += "\n\n" + current.page_content
                self.__merge_metadata(merged[-1].metadata, current.metadata)
            else:
                merged.append(current)
        
        # LINEAJE: runtime guardrail checks `merged` as it flows from the agent to the user interface, before it leaves the application (in DocumentChunker.__merge_small_parents).
        #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `merged` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:c9f7ff207b44d58a603e0e93ac4a4a56f3fab279f6a86189b83cb2b70537f03e'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:c9f7ff207b44d58a603e0e93ac4a4a56f3fab279f6a86189b83cb2b70537f03e', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/document_chunker.py', 'line': 100, 'function': 'DocumentChunker.__merge_small_parents'}, 'file': 'project/document_chunker.py', 'line': 100, 'function': '__merge_small_parents', 'agent_name': 'DocumentChunker', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
        try:
            merged = _gr_client.enforce(_gr_site, merged, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return merged

    def __split_large_parents(self, chunks):
        split_chunks = []
        
        for chunk in chunks:
            if len(chunk.page_content) <= self.__max_parent_size:
                split_chunks.append(chunk)
            else:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.__max_parent_size,
                    chunk_overlap=config.CHILD_CHUNK_OVERLAP
                )
                _lineaje_payload = [chunk]
                # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from rag source to the RAG pipeline, before the tool runs (in DocumentChunker.__split_large_parents).
                #   Detected: this statement moves data from rag source to the RAG pipeline with no runtime policy check (detection confidence: high).
                #   Decision: the Guardrail evaluates the policies enabled for this boundary; sensitive values in `_lineaje_payload` are masked in place; a policy violation is logged and the call continues (fail_mode=ALLOW_WITH_AUDIT). If the Guardrail is unreachable, the call continues unchanged.
                #   Do not remove without review. site_id='site:sha256:6f809be834ab1cdf819df92303c790430fa1c7727f6261432b2cce0924c42a00'
                _gr_client = _lineaje_load_gr_client()
                _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:6f809be834ab1cdf819df92303c790430fa1c7727f6261432b2cce0924c42a00', phase='pre_tool', boundary={'source': 'rag_source', 'sink': 'rag_pipeline'}, fail_mode='ALLOW_WITH_AUDIT', source_type='rag_source', destination_type='rag_pipeline', components={'invocation': {'file': 'project/document_chunker.py', 'line': 113, 'function': 'DocumentChunker.__split_large_parents'}, 'file': 'project/document_chunker.py', 'line': 113, 'function': '__split_large_parents', 'agent_name': 'DocumentChunker', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
                try:
                    _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json', variable_name='_lineaje_payload', source_file=__file__, before_line=113)
                except _gr_client.GuardrailUnavailableError:
                    pass
                sub_chunks = splitter.split_documents(_lineaje_payload)
                split_chunks.extend(sub_chunks)
        
        # LINEAJE: runtime guardrail checks `split_chunks` as it flows from the agent to the user interface, before it leaves the application (in DocumentChunker.__split_large_parents).
        #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `split_chunks` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:aec2bee21ed475f71c25fe667dd87603273961c8e15c03374bb687cbd58029b6'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:aec2bee21ed475f71c25fe667dd87603273961c8e15c03374bb687cbd58029b6', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/document_chunker.py', 'line': 116, 'function': 'DocumentChunker.__split_large_parents'}, 'file': 'project/document_chunker.py', 'line': 116, 'function': '__split_large_parents', 'agent_name': 'DocumentChunker', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
        try:
            split_chunks = _gr_client.enforce(_gr_site, split_chunks, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return split_chunks

    def __rebalance_pair(self, first, second):
        combined = first.page_content.rstrip() + "\n\n" + second.page_content.lstrip()
        lower = max(1, len(combined) - self.__max_parent_size)
        upper = min(self.__max_parent_size, len(combined) - 1)
        if len(combined) >= 2 * self.__min_parent_size:
            lower = max(lower, self.__min_parent_size)
            upper = min(upper, len(combined) - self.__min_parent_size)
        preferred = min(max(len(combined) // 2, lower), upper)

        split_at = preferred
        for separator in ("\n\n", "\n", " "):
            before = combined.rfind(separator, lower, preferred + 1)
            after = combined.find(separator, preferred, upper + 1)
            if before >= lower:
                split_at = before
                break
            if after != -1:
                split_at = after
                break

        left_text = combined[:split_at].rstrip()
        right_text = combined[split_at:].lstrip()
        if len(combined) >= 2 * self.__min_parent_size and (
            len(left_text) < self.__min_parent_size
            or len(right_text) < self.__min_parent_size
        ):
            split_at = preferred
            left_text, right_text = combined[:split_at], combined[split_at:]
        if not left_text or not right_text:
            return first, second

        metadata = dict(first.metadata)
        self.__merge_metadata(metadata, second.metadata)
        first.page_content, first.metadata = left_text, dict(metadata)
        second.page_content, second.metadata = right_text, dict(metadata)
        return first, second

    def __clean_small_chunks(self, chunks):
        cleaned = []
        
        for i, chunk in enumerate(chunks):
            if len(chunk.page_content) < self.__min_parent_size:
                if cleaned and len(cleaned[-1].page_content) + 2 + len(chunk.page_content) <= self.__max_parent_size:
                    cleaned[-1].page_content += "\n\n" + chunk.page_content
                    self.__merge_metadata(cleaned[-1].metadata, chunk.metadata)
                elif (
                    i < len(chunks) - 1
                    and len(chunk.page_content) + 2 + len(chunks[i + 1].page_content) <= self.__max_parent_size
                ):
                    chunks[i + 1].page_content = chunk.page_content + "\n\n" + chunks[i + 1].page_content
                    self.__merge_metadata(chunks[i + 1].metadata, chunk.metadata, prepend=True)
                else:
                    cleaned.append(chunk)
            else:
                cleaned.append(chunk)

        for i, chunk in enumerate(cleaned):
            if len(chunk.page_content) >= self.__min_parent_size or len(cleaned) == 1:
                continue
            if i < len(cleaned) - 1:
                cleaned[i], cleaned[i + 1] = self.__rebalance_pair(chunk, cleaned[i + 1])
            else:
                cleaned[i - 1], cleaned[i] = self.__rebalance_pair(cleaned[i - 1], chunk)
        
        # LINEAJE: runtime guardrail checks `cleaned` as it flows from the agent to the user interface, before it leaves the application (in DocumentChunker.__clean_small_chunks).
        #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `cleaned` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:4f3a557dc8ac210b46da2d8c019b0a61039ba5db609ef0c83b467a2e6bcab14f'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:4f3a557dc8ac210b46da2d8c019b0a61039ba5db609ef0c83b467a2e6bcab14f', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/document_chunker.py', 'line': 182, 'function': 'DocumentChunker.__clean_small_chunks'}, 'file': 'project/document_chunker.py', 'line': 182, 'function': '__clean_small_chunks', 'agent_name': 'DocumentChunker', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
        try:
            cleaned = _gr_client.enforce(_gr_site, cleaned, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return cleaned

    def __create_child_chunks(self, all_parent_pairs, all_child_chunks, parent_chunks, doc_path, source_name):
        for i, p_chunk in enumerate(parent_chunks):
            parent_id = f"{doc_path.stem}_p{i}"
            p_chunk.metadata.update({"source": source_name, "parent_id": parent_id})
            
            all_parent_pairs.append((parent_id, p_chunk))
            _lineaje_payload = [p_chunk]
            # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from rag source to the RAG pipeline, before the tool runs (in DocumentChunker.__create_child_chunks).
            #   Detected: this statement moves data from rag source to the RAG pipeline with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates the policies enabled for this boundary; sensitive values in `_lineaje_payload` are masked in place; a policy violation is logged and the call continues (fail_mode=ALLOW_WITH_AUDIT). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:730578398a8111025d3ab7adf5e34e11d17cbfb59e2df6c5817e516f666d3bd9'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:730578398a8111025d3ab7adf5e34e11d17cbfb59e2df6c5817e516f666d3bd9', phase='pre_tool', boundary={'source': 'rag_source', 'sink': 'rag_pipeline'}, fail_mode='ALLOW_WITH_AUDIT', source_type='rag_source', destination_type='rag_pipeline', components={'invocation': {'file': 'project/document_chunker.py', 'line': 190, 'function': 'DocumentChunker.__create_child_chunks'}, 'file': 'project/document_chunker.py', 'line': 190, 'function': '__create_child_chunks', 'agent_name': 'DocumentChunker', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json', variable_name='_lineaje_payload', source_file=__file__, before_line=190)
            except _gr_client.GuardrailUnavailableError:
                pass
            all_child_chunks.extend(self.__child_splitter.split_documents(_lineaje_payload))
