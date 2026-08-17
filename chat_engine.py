# chat_engine.py
# v2.1 — warmer persona, robust confidence handling, improved follow-up tone, and safe score parsing

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import re
import textwrap


@dataclass
class ChatResponse:
    answer: str
    confidence: float
    sources_used: List[str]
    meta: Dict[str, Any]


class ChatEngine:
    """
    ChatEngine formats user questions, pulls the most relevant SOP chunks from a knowledge base,
    and crafts a friendly, structured response with a short checklist and one optional follow-up.
    """

    def __init__(self, kb_provider, llm_client, *, max_context_chars: int = 12000):
        self.kb = kb_provider
        self.llm = llm_client
        self.max_context_chars = max_context_chars

    # -----------------------------
    # Public API
    # -----------------------------
    def answer(self, user_question: str) -> ChatResponse:
        hits = self.kb.search(user_question, top_k=12)
        context_text, sources = self._stitch_context(hits, limit=self.max_context_chars)

        prompt = self._build_prompt(user_question=user_question, context=context_text)
        raw = self._safe_generate(prompt).strip()

        cleaned = self._enforce_structure(raw)
        confidence = self._heuristic_confidence(user_question, context_text, hits)
        followup = self._auto_follow_up(user_question)

        answer = cleaned
        if followup:
            answer = f"{cleaned}\n\n—\n{followup}"

        return ChatResponse(
            answer=answer,
            confidence=round(confidence, 2),
            sources_used=sources,
            meta={
                "chunks_considered": len(hits),
                "context_chars": len(context_text),
                "max_context_chars": self.max_context_chars,
            },
        )

    # -----------------------------
    # Helpers
    # -----------------------------
    def _safe_generate(self, prompt: str) -> str:
        try:
            result = self.llm.generate(prompt)
            if isinstance(result, str):
                return result
            return getattr(result, "text", str(result))
        except Exception as e:
            return f"(⚠️ Generation error: {e})"

    def _stitch_context(self, hits: List[Dict[str, Any]], limit: int) -> Tuple[str, List[str]]:
        pieces = []
        used_sources = []
        total = 0
        for h in hits:
            snippet = h.get("text", "")
            sid = h.get("source_id", "sop")
            if not snippet:
                continue
            if total + len(snippet) > limit and total > 0:
                break
            pieces.append(f"[{sid}] {snippet}")
            total += len(snippet)
            used_sources.append(sid)

        used_sources = list(dict.fromkeys(used_sources))
        return "\n---\n".join(pieces), used_sources

    def _heuristic_confidence(self, question: str, context: str, hits: List[Dict[str, Any]]) -> float:
        q_terms = [t for t in re.findall(r"[a-z0-9]+", question.lower()) if len(t) > 2]
        ctx_lower = context.lower()
        overlap = sum(1 for t in set(q_terms) if t in ctx_lower)
        overlap_score = min(100, overlap * 6)

        top = 0
        if hits and isinstance(hits[0], dict):
            try:
                top = float(hits[0].get("score", 0))
            except (ValueError, TypeError):
                top = 0
        top_score = max(0, min(100, (top or 0) * 100))

        size_penalty = 0
        if len(context) < 800:
            size_penalty = 12
        elif len(context) < 2200:
            size_penalty = 6

        raw = 0.55 * overlap_score + 0.35 * top_score + 0.10 * (100 - size_penalty)
        return max(0, min(100, raw))

    def _build_prompt(self, user_question: str, context: str) -> str:
        wants_steps = bool(re.search(r"\bhow\b|\bprocedure\b|\bsteps?\b|\bworkflow\b", user_question, re.I))
        style_hint = "Focus on a short checklist with clear steps." if wants_steps else \
                     "Start with a concise answer, then give a brief checklist for next actions."

        return textwrap.dedent(f"""
        You are SOPIA, a friendly on-duty assistant for the ACE 5 HIV Care SOP.
        Your tone is professional-warm, concise, and helpful. Use simple words.
        Use ONE emoji only if it truly helps clarity (otherwise none).

        Ground rules:
        - Only use the SOP CONTEXT below. If the answer is not in the context, say:
          "not in the SOP excerpt i have. generally:" and then provide safe, generic guidance.
        - Prefer short sentences. Keep first answer 2–5 lines before any bullets.
        - When you mention a form, threshold, or timing, be precise.
        - If you must use jargon, define it briefly in [brackets].
        - Finish with a short “do this next” checklist.
        - Ask at most ONE helpful follow-up question if relevant.

        {style_hint}

        SOP CONTEXT (snippets may be from multiple sections):
        ---
        {context}
        ---

        USER:
        {user_question}

        FORMAT EXACTLY:
        1) brief answer (2–5 lines)
        2) steps / checklist (• bullets, 3–6 items max)
        3) forms/docs to fill (if any)
        4) one follow-up question (optional)
        """).strip()

    def _enforce_structure(self, text: str) -> str:
        wanted = ["1)", "2)", "3)", "4)"]
        if any(x in text for x in wanted):
            return text
        prefix = "1) Summary\n2) Steps\n3) Forms\n4) Follow-up"
        return f"{prefix}\n\n{text}"

    def _auto_follow_up(self, user_question: str) -> Optional[str]:
        if re.search(r"\btest|result|report\b", user_question, re.I):
            return "Would you like me to show how to record the result in the patient file?"
        if re.search(r"\breferral|clinic\b", user_question, re.I):
            return "Do you want the referral process or contact list?"
        if re.search(r"\bdrug|dose|medication\b", user_question, re.I):
            return "Should I include the dosage table?"
        return None
