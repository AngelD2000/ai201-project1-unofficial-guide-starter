"""
app.py
------
Gradio chat interface for the unofficial CU Boulder CS guide.

Multi-turn memory: prior turns are kept in a LangChain
`InMemoryChatMessageHistory`, which is the source of truth handed to the LLM
on every call. The Gradio chatbot widget mirrors that history for display.
The Sources block is appended at display time but NOT stored in history, so
the model isn't conditioned to imitate citation formatting from prior turns.
"""

import gradio as gr
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage

from generate import generate_answer, format_full_answer

# Single-user demo: one shared in-memory history across calls in this process.
history = InMemoryChatMessageHistory()


def _history_as_openai_messages():
    out = []
    for m in history.messages:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        out.append({"role": role, "content": m.content})
    return out


def respond(user_message, _chat_display):
    prior = _history_as_openai_messages()
    bare_answer, sources_block, _hits = generate_answer(
        user_message, chat_history=prior
    )
    # Store the BARE answer (no source block) so future turns don't see
    # citation styling that we want to keep system-controlled.
    history.add_message(HumanMessage(content=user_message))
    history.add_message(AIMessage(content=bare_answer))
    return format_full_answer(bare_answer, sources_block)


def reset_history():
    history.clear()


with gr.Blocks(title="CU Boulder CS — Unofficial Guide") as demo:
    gr.Markdown(
        "# CU Boulder CS — Unofficial Guide\n"
        "Ask about professors, courses, dorms, costs, or grad admissions. "
        "Answers come strictly from retrieved student-sourced content; sources "
        "are listed under each reply."
    )
    # Gradio 6.x: ChatInterface uses the OpenAI 'messages' format by default;
    # the legacy `type=` parameter was removed.
    chat = gr.ChatInterface(fn=respond)
    gr.Button("Reset conversation").click(fn=reset_history)


if __name__ == "__main__":
    demo.launch()
