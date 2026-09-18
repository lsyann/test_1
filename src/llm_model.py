from typing import Tuple
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizer, PreTrainedModel, logging
from huggingface_hub import hf_hub_download
from .retrieval import get_sources, get_text


class Small_LLM_Model:
    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-0.6B",
        *,
        device: str | None = None,
        dtype: torch.dtype | None = None,
        trust_remote_code: bool = True,
    ) -> None:
        self._model_name = model_name

        # Auto-select device with priority: mps > cuda > cpu
        if device is None:
            if torch.backends.mps.is_available():
                device = "mps"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
        self._device = device

        if dtype is None:
            dtype = torch.float16 if self._device in ["cuda", "mps"] else torch.float32
        self._dtype = dtype

        # --- load tokenizer & model -------------------------------------------------
        self._tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=trust_remote_code
        )
        if self._tokenizer.pad_token_id is None:
            # ensure we have a pad token to keep batch helpers happy
            self._tokenizer.pad_token_id = self._tokenizer.eos_token_id

        self._model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=self._dtype,
            device_map="auto" if self._device == "cuda" else None,
            trust_remote_code=trust_remote_code,
        )
        self._model.to(self._device)
        self._model.eval()

        # switch to inference-only mode
        for p in self._model.parameters():
            p.requires_grad = False


    def encode(self, text: str) -> torch.Tensor:
        """Tokenise *text* and return a 2-D ``input_ids`` tensor on the target device."""
        return self._tokenizer.encode(text, add_special_tokens=False)


    def decode(self, ids: torch.Tensor | list[int]) -> str:
        if isinstance(ids, torch.Tensor):
            ids = ids.tolist()
        return self._tokenizer.decode(ids, skip_special_tokens=True)


    def get_logits_from_input_ids(self, input_ids: list[int]) -> list[float]:
        input_tensor = torch.tensor([input_ids], device=self._device, dtype=torch.long)
        with torch.no_grad():
            out = self._model(input_ids=input_tensor)
        logits = out.logits[0, -1].tolist()
        return [float(x) for x in logits]

def get_answer(llm: Small_LLM_Model, prompt: str, k: int, new_sources: str = "") -> str:
    if not new_sources:
        sources = get_sources(prompt, k)

    torch.cuda.memory.empth_cache()

    context = '"""use the following context to answer the question:\n'
    if not new_sources:
        for source in sources:
            context += "\n" + get_text(source) + "\n\n"
    else:
        context += "\n" + new_sources + "\n\n"
    context += '"""\n\nQuestion: "' + prompt + '"\n\nAnswer: "'

    tokens = llm.encode(context)
    answer = []
    max_tokens = 0
    while True:
        logits = llm.get_logits_from_input_ids(tokens)
        index = logits.index(max(logits))
        tokens.append(index)
        answer.append(index)
        max_tokens += 1
        if max_tokens > 100 or '"' in llm.decode(answer):
            return llm.decode(answer)[:-3]
    return llm.decode(answer)
