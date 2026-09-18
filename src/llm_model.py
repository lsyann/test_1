from typing import cast
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel
from .retrieval import get_sources, get_text

class Small_LLM_Model:
    def __init__(self):
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._tokenizer = (AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B"))
        self._model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B")
        self._model.to(self._device)


def get_answer(llm: Small_LLM_Model, prompt: str, k: int, new_sources: str = "") -> str:
    if not new_sources:
        sources = get_sources(prompt, k, False)
    context = '"""use the following context to answer the question:\n'
    if not new_sources:
        for source in sources:
            context += "\n" + get_text(source) + "\n\n"
    else:
        context += "\n" + new_sources + "\n\n"
    context += '"""\n\nQuestion: "' + prompt + '"\n\nAnswer: "'
    system_prompt: str = (
    "You answer questions about the vLLM codebase using only the numbered "
    "sources given to you. Ground every claim in those sources; do not rely "
    "on what you already know about similar projects or libraries, even when "
    "it looks relevant. If the sources do not contain the answer, say so "
    "plainly instead of guessing. Be concise: answer the question that was "
    "asked, in a few sentences, without adding setup steps or examples that "
    "are not in the sources.")
    message = [{"role": "system", "content": system_prompt}]
    message.append({"role": "user", "content": context})
    text = cast(str, llm._tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True, enable_thinking=False))
    inputs = llm._tokenizer(text, return_tensors="pt").to(llm._device)
    output = llm._model.generate(**inputs, max_new_tokens=100, do_sample=False)
    answer = output[0][inputs["input_ids"].shape[1]:]
    return cast(str, llm._tokenizer.decode(answer, skip_special_tokens=True))
