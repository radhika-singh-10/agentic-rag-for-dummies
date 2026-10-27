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
import shutil
import config
import pymupdf.layout
import pymupdf4llm
from pathlib import Path
import glob
import tiktoken
from functools import lru_cache


def clear_directory_contents(directory: Path) -> None:
    """Delete everything under directory but not the directory itself (safe for Docker volume / bind mount roots)."""
    directory = Path(directory)
    if not directory.is_dir():
        return
    for child in directory.iterdir():
        if child.is_dir():
            # LINEAJE: runtime guardrail checks `child` as it flows from the agent to system, at a security decision (in clear_directory_contents).
            #   Detected: this statement moves data from the agent to system with no runtime policy check (detection confidence: medium).
            #   Decision: the Guardrail evaluates AI_DAT_SEC_029; sensitive values in `child` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
            #   Do not remove without review. site_id='site:sha256:2affd3f662f2403a0f340af92d356ed204762ca3381571fd35a20b73cf18609f'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:2affd3f662f2403a0f340af92d356ed204762ca3381571fd35a20b73cf18609f', phase='security_decision', boundary={'source': 'agent_message', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='agent', destination_type='system', components={'invocation': {'file': 'project/utils.py', 'line': 19, 'function': 'clear_directory_contents'}, 'file': 'project/utils.py', 'line': 19, 'function': 'clear_directory_contents', 'agent_name': 'clear_directory_contents', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
            try:
                child = _gr_client.enforce(_gr_site, child, content_type='application/json', variable_name='child', source_file=__file__, before_line=19)
            except _gr_client.GuardrailUnavailableError:
                pass
            shutil.rmtree(child)
        else:
            child.unlink()


os.environ["TOKENIZERS_PARALLELISM"] = "false"

def pdf_to_markdown(pdf_path, output_dir):
    doc = pymupdf.open(pdf_path)
    md = pymupdf4llm.to_markdown(doc, header=False, footer=False, page_separators=True, ignore_images=True, write_images=False, image_path=None)
    md_cleaned = md.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='ignore')
    output_path = Path(output_dir) / Path(doc.name).name
    Path(output_path).with_suffix(".md").write_bytes(md_cleaned.encode('utf-8'))

def pdfs_to_markdowns(path_pattern, overwrite: bool = False):
    output_dir = Path(config.MARKDOWN_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in map(Path, glob.glob(path_pattern)):
        md_path = (output_dir / pdf_path.name).with_suffix(".md")
        if overwrite or not md_path.exists():
            pdf_to_markdown(pdf_path, output_dir)

@lru_cache(maxsize=1)
def _get_token_encoding():
    try:
        return tiktoken.encoding_for_model("gpt-4")
    except Exception:
        try:
            return tiktoken.get_encoding("cl100k_base")
        except Exception:
            return None


def estimate_context_tokens(messages: list) -> int:
    contents = [
        str(msg.content)
        for msg in messages
        if hasattr(msg, "content") and msg.content
    ]
    encoding = _get_token_encoding()
    if encoding is None:
        return sum(max(1, len(content) // 4) for content in contents)
    return sum(len(encoding.encode(content)) for content in contents)
