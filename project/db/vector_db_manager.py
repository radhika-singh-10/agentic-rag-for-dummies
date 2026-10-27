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

import config
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

class VectorDbManager:
    __client: QdrantClient
    __dense_embeddings: HuggingFaceEmbeddings
    __sparse_embeddings: FastEmbedSparse
    def __init__(self):
        self.__client = QdrantClient(path=config.QDRANT_DB_PATH)
        # LINEAJE: runtime guardrail checks the model this client is built with as it flows from the agent to the LLM, before it is sent to the model (in VectorDbManager.__init__).
        #   Detected: this statement moves data from the agent to the LLM with no runtime policy check (detection confidence: medium).
        #   Decision: the Guardrail evaluates AI_AGENT_ACTIVITY_LOG, AI_APP_SEC_006, AI_APP_SEC_028, AI_APP_SEC_070 (+1 more); a model that is not approved is refused before the client is built (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:8b88e49e2d3d4d51ad0976711f1e6bb16238e65b33977e1f1a8e4465c67ba8ef'
        _lineaje_model_evidence = {'model': config.DENSE_MODEL, 'client': 'HuggingFaceEmbeddings', 'provider': 'langchain_huggingface', 'model_source': 'call_kwarg', 'project': 'tree'}
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:8b88e49e2d3d4d51ad0976711f1e6bb16238e65b33977e1f1a8e4465c67ba8ef', phase='pre_model', boundary={'source': 'agent_config', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', components={'invocation': {'file': 'project/db/vector_db_manager.py', 'function': 'VectorDbManager.__init__', 'line': 13}, 'file': 'project/db/vector_db_manager.py', 'line': 13, 'function': '__init__', 'agent_name': 'VectorDbManager', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:3090e26bcf352f27'})
        try:
            _lineaje_model_evidence = _gr_client.enforce(_gr_site, _lineaje_model_evidence, content_type='application/json')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            raise
        self.__dense_embeddings = HuggingFaceEmbeddings(model_name=config.DENSE_MODEL)
        self.__sparse_embeddings = FastEmbedSparse(model_name=config.SPARSE_MODEL)

    def _dense_vector_size(self):
        _lineaje_payload = "test"
        # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the RAG pipeline to embedding model, before it is sent to the model (in VectorDbManager._dense_vector_size).
        #   Detected: this statement moves data from the RAG pipeline to embedding model with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates the policies enabled for this boundary; sensitive values in `_lineaje_payload` are masked in place; a policy violation is logged and the call continues (fail_mode=ALLOW_WITH_AUDIT). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:dc0cb493f48dcb817323bfc271851dcde76b9449399db29e99b0d031a9adf582'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:dc0cb493f48dcb817323bfc271851dcde76b9449399db29e99b0d031a9adf582', phase='pre_model', boundary={'source': 'rag_pipeline', 'sink': 'embedding_model'}, fail_mode='ALLOW_WITH_AUDIT', source_type='rag_pipeline', destination_type='embedding_model', components={'invocation': {'file': 'project/db/vector_db_manager.py', 'line': 17, 'function': 'VectorDbManager._dense_vector_size'}, 'file': 'project/db/vector_db_manager.py', 'line': 17, 'function': '_dense_vector_size', 'agent_name': 'VectorDbManager', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
        try:
            _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json', variable_name='_lineaje_payload', source_file=__file__, before_line=17)
        except _gr_client.GuardrailUnavailableError:
            pass
        return len(self.__dense_embeddings.embed_query(_lineaje_payload))

    @staticmethod
    def _collection_vector_size(collection_info):
        vectors_config = collection_info.config.params.vectors
        if hasattr(vectors_config, "size"):
            return vectors_config.size
        if isinstance(vectors_config, dict) and vectors_config:
            first_vector = next(iter(vectors_config.values()))
            return getattr(first_vector, "size", None)
        return None

    def create_collection(self, collection_name):
        expected_size = self._dense_vector_size()
        if not self.__client.collection_exists(collection_name):
            _lineaje_payload = f"Creating collection: {collection_name}..."
            # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the application log, before it is written to the log (in VectorDbManager.create_collection).
            #   Detected: this statement moves data from the agent to the application log with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates AI_DAT_SEC_010; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:3d3cfa377b41c5e17952f70dea4a8391161e4d5cc7e6feb09773a0d18b9c6888'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:3d3cfa377b41c5e17952f70dea4a8391161e4d5cc7e6feb09773a0d18b9c6888', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', components={'invocation': {'file': 'project/db/vector_db_manager.py', 'line': 32, 'function': 'VectorDbManager.create_collection'}, 'file': 'project/db/vector_db_manager.py', 'line': 32, 'function': 'create_collection', 'agent_name': 'VectorDbManager', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            print(_lineaje_payload)
            self.__client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(size=expected_size, distance=qmodels.Distance.COSINE),
                sparse_vectors_config={config.SPARSE_VECTOR_NAME: qmodels.SparseVectorParams()},
            )
            _lineaje_payload = f"✓ Collection created: {collection_name}"
            # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the application log, before it is written to the log (in VectorDbManager.create_collection).
            #   Detected: this statement moves data from the agent to the application log with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates AI_DAT_SEC_010; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:8e6a19d82ce82574a51bc27977151c785afb8180ec798726dc4c11f1e00586ba'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:8e6a19d82ce82574a51bc27977151c785afb8180ec798726dc4c11f1e00586ba', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', components={'invocation': {'file': 'project/db/vector_db_manager.py', 'line': 38, 'function': 'VectorDbManager.create_collection'}, 'file': 'project/db/vector_db_manager.py', 'line': 38, 'function': 'create_collection', 'agent_name': 'VectorDbManager', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            print(_lineaje_payload)
        else:
            collection_info = self.__client.get_collection(collection_name)
            existing_size = self._collection_vector_size(collection_info)
            if existing_size and existing_size != expected_size:
                raise ValueError(
                    f"Qdrant collection '{collection_name}' has dense vector size "
                    f"{existing_size}, but '{config.DENSE_MODEL}' produces size "
                    f"{expected_size}. Clear and re-index the collection after "
                    "changing embedding models."
                )
            _lineaje_payload = f"✓ Collection already exists: {collection_name}"
            # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the application log, before it is written to the log (in VectorDbManager.create_collection).
            #   Detected: this statement moves data from the agent to the application log with no runtime policy check (detection confidence: high).
            #   Decision: the Guardrail evaluates AI_DAT_SEC_010; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:9c7e72370626bbb1acbb88d98a19410945fa397ba1afd7160f7caf7054e4a39d'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:9c7e72370626bbb1acbb88d98a19410945fa397ba1afd7160f7caf7054e4a39d', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', components={'invocation': {'file': 'project/db/vector_db_manager.py', 'line': 49, 'function': 'VectorDbManager.create_collection'}, 'file': 'project/db/vector_db_manager.py', 'line': 49, 'function': 'create_collection', 'agent_name': 'VectorDbManager', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            print(_lineaje_payload)

    def delete_collection(self, collection_name):
        try:
            if self.__client.collection_exists(collection_name):
                _lineaje_payload = f"Removing existing Qdrant collection: {collection_name}"
                # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to the application log, before it is written to the log (in VectorDbManager.delete_collection).
                #   Detected: this statement moves data from the agent to the application log with no runtime policy check (detection confidence: high).
                #   Decision: the Guardrail evaluates AI_DAT_SEC_010; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
                #   Do not remove without review. site_id='site:sha256:bfd1d8265163838ab5d7417a37268b6caa61eaf8f909032a8a3461d80c979503'
                _gr_client = _lineaje_load_gr_client()
                _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:bfd1d8265163838ab5d7417a37268b6caa61eaf8f909032a8a3461d80c979503', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', components={'invocation': {'file': 'project/db/vector_db_manager.py', 'line': 54, 'function': 'VectorDbManager.delete_collection'}, 'file': 'project/db/vector_db_manager.py', 'line': 54, 'function': 'delete_collection', 'agent_name': 'VectorDbManager', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
                try:
                    _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
                except _gr_client.GuardrailUnavailableError:
                    pass
                except PermissionError:
                    pass
                print(_lineaje_payload)
                self.__client.delete_collection(collection_name)
        except Exception as e:
            raise RuntimeError(f"Unable to delete Qdrant collection '{collection_name}'.") from e

    def get_collection(self, collection_name) -> QdrantVectorStore:
        try:
            try:
                _lineaje_obs = _lineaje_load_gr_client()
                _lineaje_obs_site = _lineaje_obs.SiteDescriptor(site_id='site:sha256:621b94f38aac78a516942c2ed831434049099e0c74ab1993b315c0d7dadff66f', phase='', boundary={}, fail_mode='ALLOW', source_type='rag_pipeline', destination_type='embedding_model', components={'file': 'project/db/vector_db_manager.py', 'line': 61, 'function': 'get_collection', 'agent_name': 'VectorDbManager', 'agent_name_source': 'inferred_from_class', 'call_target': 'QdrantVectorStore', 'invocation': {'file': 'project/db/vector_db_manager.py', 'function': 'VectorDbManager.get_collection', 'line': 61}, 'destination': {'entity_type': 'llm', 'name': 'Qwen3-Embedding-0.6B', 'provider': 'qwen', 'version': ''}, 'source': {'entity_type': 'rag', 'file_path': 'project/config.py', 'line': 11, 'name': 'document_child_chunks', 'repository_uri': 'https://github.com/radhika-singh-10/agentic-rag-for-dummies', 'unique_org_id': 'vdna_HSUl9QihFwySjoPY'}, 'boundary_id': 'bnd:8a358c32d2bcf123'}, observe_only=True)
                _lineaje_obs.enforce(_lineaje_obs_site, {'activity': 'embedding_call'}, content_type='application/json')
            except Exception:
                pass
            return QdrantVectorStore(
                    client=self.__client,
                    collection_name=collection_name,
                    embedding=self.__dense_embeddings,
                    sparse_embedding=self.__sparse_embeddings,
                    retrieval_mode=RetrievalMode.HYBRID,
                    sparse_vector_name=config.SPARSE_VECTOR_NAME
                )
        except Exception as e:
            raise RuntimeError(f"Unable to initialize Qdrant collection '{collection_name}'.") from e
