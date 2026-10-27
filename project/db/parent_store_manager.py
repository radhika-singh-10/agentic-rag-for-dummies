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

import re
import json
import config
from utils import clear_directory_contents
from pathlib import Path
from typing import List, Dict

class ParentStoreManager:
    __store_path: Path

    def __init__(self, store_path=config.PARENT_STORE_PATH):
        self.__store_path = Path(store_path) 
        self.__store_path.mkdir(parents=True, exist_ok=True)

    def save(self, parent_id: str, content: str, metadata: Dict) -> None:
        file_path = self.__store_path / f"{parent_id}.json"
        _lineaje_payload = json.dumps({"page_content": content,"metadata": metadata}, ensure_ascii=False, indent=2)
        # LINEAJE: runtime guardrail checks `_lineaje_payload` as it flows from the agent to a file, before it is written to disk (in ParentStoreManager.save).
        #   Detected: this statement moves data from the agent to a file with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates AI_DAT_SEC_025; sensitive values in `_lineaje_payload` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:8a0adfb6538134bc3df352dbc4f2cc9b36a99ab4a2036b10b31b010c9566247e'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:8a0adfb6538134bc3df352dbc4f2cc9b36a99ab4a2036b10b31b010c9566247e', phase='file_write', boundary={'source': 'agent_message', 'sink': 'file_content'}, fail_mode='BLOCK', source_type='agent', destination_type='file', components={'invocation': {'file': 'project/db/parent_store_manager.py', 'line': 17, 'function': 'ParentStoreManager.save'}, 'file': 'project/db/parent_store_manager.py', 'line': 17, 'function': 'save', 'agent_name': 'ParentStoreManager', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
        try:
            _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json', variable_name='_lineaje_payload', source_file=__file__, before_line=17)
        except _gr_client.GuardrailUnavailableError:
            pass
        file_path.write_text(
            _lineaje_payload,
            encoding="utf-8"
        )
    
    def save_many(self, parents: List) -> None:
        for parent_id, doc in parents:
            self.save(parent_id, doc.page_content, doc.metadata)

    def delete_many(self, parent_ids: List[str]) -> None:
        for parent_id in parent_ids:
            file_path = self.__store_path / f"{parent_id}.json"
            if file_path.exists():
                file_path.unlink()

    def load(self, parent_id: str) -> Dict:
        file_path = self.__store_path / (
            parent_id if parent_id.lower().endswith(".json") else f"{parent_id}.json"
        )
        return json.loads(file_path.read_text(encoding="utf-8"))
    
    def load_content(self, parent_id: str) -> Dict:
        data = self.load(parent_id)
        return {
                "content": data["page_content"],
                "parent_id": parent_id,
                "metadata": data["metadata"]
            }

    @staticmethod
    def _get_sort_key(id_str):
        match = re.search(r'_(?:parent_|p)(\d+)$', id_str)
        return int(match.group(1)) if match else 0

    def load_content_many(self, parent_ids: List[str]) -> List[Dict]:
        unique_ids = set(parent_ids)
        return [self.load_content(pid) for pid in sorted(unique_ids, key=self._get_sort_key)]

    def list_sources(self) -> List[str]:
        sources = set()
        for file_path in self.__store_path.glob("*.json"):
            try:
                source = json.loads(file_path.read_text(encoding="utf-8")).get("metadata", {}).get("source")
                if source:
                    sources.add(source)
            except (OSError, json.JSONDecodeError):
                continue
        return sorted(sources)
    
    def clear_store(self) -> None:
        self.__store_path.mkdir(parents=True, exist_ok=True)
        clear_directory_contents(self.__store_path)
