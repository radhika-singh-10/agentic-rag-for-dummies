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

import gradio as gr
from core.chat_interface import ChatInterface
from core.document_manager import DocumentManager
from core.rag_system import RAGSystem
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

def create_gradio_ui():
    rag_system = RAGSystem()
    rag_system.initialize()
    
    doc_manager = DocumentManager(rag_system)
    chat_interface = ChatInterface(rag_system)
    
    def format_file_list():
        files = doc_manager.get_markdown_files()
        if not files:
            return "📭 No documents available in the knowledge base"
        return "\n".join([f"{f}" for f in files])
    
    def upload_handler(files, progress=gr.Progress()):
        if not files:
            return None, format_file_list()
            
        # LINEAJE: runtime guardrail checks `files` as it flows from the RAG pipeline to a vector store, before the tool runs (in upload_handler).
        #   Detected: this statement moves data from the RAG pipeline to a vector store with no runtime policy check (detection confidence: high).
        #   Decision: the Guardrail evaluates the policies enabled for this boundary; sensitive values in `files` are masked in place; a policy violation is logged and the call continues (fail_mode=ALLOW_WITH_AUDIT). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:8637896ba0a509844cb76b8ade65ecf5cd4a2f31ac80bad44ff637ef1c4c7522'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:8637896ba0a509844cb76b8ade65ecf5cd4a2f31ac80bad44ff637ef1c4c7522', phase='pre_tool', boundary={'source': 'rag_pipeline', 'sink': 'vector_store'}, fail_mode='ALLOW_WITH_AUDIT', source_type='rag_pipeline', destination_type='vector_store', components={'invocation': {'file': 'project/ui/gradio_app.py', 'line': 26, 'function': 'create_gradio_ui.upload_handler'}, 'file': 'project/ui/gradio_app.py', 'line': 26, 'function': 'upload_handler', 'agent_name': 'upload_handler', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
        try:
            files = _gr_client.enforce(_gr_site, files, content_type='application/json', variable_name='files', source_file=__file__, before_line=26)
        except _gr_client.GuardrailUnavailableError:
            pass
        added, skipped = doc_manager.add_documents(
            files, 
            progress_callback=lambda p, desc: progress(p, desc=desc)
        )
        
        gr.Info(f"✅ Added: {added} | Skipped: {skipped}")
        return None, format_file_list()
    
    def clear_handler():
        try:
            doc_manager.clear_all()
            gr.Info("🗑️ Removed all documents")
        except Exception as exc:
            gr.Error(f"Unable to clear documents: {exc}")
        return format_file_list()
    
    def chat_handler(msg, hist):
        # LINEAJE: runtime guardrail checks `msg` as it flows from the agent to the LLM, before it is sent to the model (in chat_handler).
        #   Detected: this statement moves data from the agent to the LLM with no runtime policy check (detection confidence: medium).
        #   Decision: the Guardrail evaluates AI_AGENT_ACTIVITY_LOG, AI_APP_SEC_006, AI_APP_SEC_028, AI_APP_SEC_070 (+2 more); sensitive values in `msg` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
        #   Do not remove without review. site_id='site:sha256:d3401dcc0143555bf87dcc4bd81c71c1ec42ae677db12f931be7578e9ddf1fab'
        _lineaje_msg_evidence = {'msg': msg, 'model': getattr(_lineaje_load_gr_client(), 'current_model', lambda _f: '')(__file__)}
        _gr_client = _lineaje_load_gr_client()
        _lineaje_interaction_id = _gr_client.new_interaction_id()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:d3401dcc0143555bf87dcc4bd81c71c1ec42ae677db12f931be7578e9ddf1fab', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', components={'invocation': {'file': 'project/ui/gradio_app.py', 'line': 43, 'function': 'create_gradio_ui.chat_handler'}, 'file': 'project/ui/gradio_app.py', 'line': 43, 'function': 'chat_handler', 'agent_name': 'chat_handler', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True}, interaction_id=_lineaje_interaction_id)
        try:
            _lineaje_msg_evidence = _gr_client.enforce(_gr_site, _lineaje_msg_evidence, content_type='application/json')
            msg = _lineaje_msg_evidence.get('msg', msg) if isinstance(_lineaje_msg_evidence, dict) else msg
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            raise
        for chunk in chat_interface.chat(msg, hist):
            yield chunk
        try:
            _lineaje_obs = _lineaje_load_gr_client()
            _lineaje_obs_site = _lineaje_obs.SiteDescriptor(site_id='site:sha256:ffefd5acab9115e5f61ebd441f5ef10e6df73297e53c3771f20f173e74a2bf24', phase='', boundary={}, fail_mode='ALLOW', source_type='llm', destination_type='agent', components={'file': 'project/ui/gradio_app.py', 'line': 43, 'function': 'chat_handler', 'agent_name': 'chat_handler', 'agent_name_source': 'inferred_from_function', 'call_target': 'chat_interface.chat', 'not_on_graph': True}, observe_only=True, interaction_id=locals().get('_lineaje_interaction_id'))
            _lineaje_obs.enforce(_lineaje_obs_site, {'activity': 'llm_to_agent'}, content_type='application/json')
        except Exception:
            pass
    
    def clear_chat_handler():
        chat_interface.clear_session()
    
    with gr.Blocks(title="Agentic RAG") as demo:
        
        with gr.Tab("Documents", elem_id="doc-management-tab"):
            gr.Markdown("## Add New Documents")
            gr.Markdown("Upload PDF or Markdown files. Existing documents are skipped; use Clear All before re-indexing.")
            
            files_input = gr.File(
                label="Drop PDF or Markdown files here",
                file_count="multiple",
                type="filepath",
                height=200,
                show_label=False
            )
            
            add_btn = gr.Button("Add Documents", variant="primary", size="md")
            
            gr.Markdown("## Current Documents in the Knowledge Base")
            file_list = gr.Textbox(
                value=format_file_list(),
                interactive=False,
                lines = 7,
                max_lines=10,
                elem_id="file-list-box",
                show_label=False
            )
            
            with gr.Row():
                refresh_btn = gr.Button("Refresh", size="md")
                clear_btn = gr.Button("Clear All", variant="stop", size="md")
            
            add_btn.click(upload_handler, [files_input], [files_input, file_list], show_progress="corner")
            refresh_btn.click(format_file_list, None, file_list)
            clear_btn.click(clear_handler, None, file_list)
        
        with gr.Tab("Chat"):
            chatbot = gr.Chatbot(
                height=720, 
                placeholder="<strong>Ask me anything!</strong><br><em>I'll search, reason, and act to give you the best answer :)</em>",
                show_label=False,
                avatar_images=(None, os.path.join(ASSETS_DIR, "chatbot_avatar.png")),
                layout="bubble"
            )
            chatbot.clear(clear_chat_handler)
            
            gr.ChatInterface(fn=chat_handler, chatbot=chatbot)
    
    # LINEAJE: runtime guardrail checks `demo` as it flows from the agent to the user interface, before it leaves the application (in create_gradio_ui).
    #   Detected: this statement moves data from the agent to the user interface with no runtime policy check (detection confidence: high).
    #   Decision: the Guardrail evaluates AI_DAT_SEC_012; sensitive values in `demo` are masked in place; a policy violation stops the call (fail_mode=BLOCK). If the Guardrail is unreachable, the call continues unchanged.
    #   Do not remove without review. site_id='site:sha256:2b06942faa4908d44362bafc14cf78de0763fec4f93c0dc8a18a88047e1b2ce3'
    _gr_client = _lineaje_load_gr_client()
    _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:2b06942faa4908d44362bafc14cf78de0763fec4f93c0dc8a18a88047e1b2ce3', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', components={'invocation': {'file': 'project/ui/gradio_app.py', 'line': 95, 'function': 'create_gradio_ui'}, 'file': 'project/ui/gradio_app.py', 'line': 95, 'function': 'create_gradio_ui', 'agent_name': 'create_gradio_ui', 'agent_name_source': 'inferred_from_function', 'not_on_graph': True})
    try:
        demo = _gr_client.enforce(_gr_site, demo, content_type='text/plain')
    except _gr_client.GuardrailUnavailableError:
        pass
    except PermissionError:
        pass
    return demo
