"""통합 모델 추론 서비스.

환경변수 INFERENCE_BACKEND로 백엔드를 선택합니다:
- "claude"    → Anthropic Claude (기본, API 키 필요)
- "finetuned" → HF Fine-tuned LLaMA 3 (로컬 GPU 또는 HF Hub)

회고 초안 생성 노드에서 직접 LLM을 호출하는 대신 이 서비스를 사용합니다.
"""

import asyncio
import logging
from functools import lru_cache

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


class ClaudeBackend:
    """Anthropic Claude 기반 추론 백엔드"""

    def __init__(self) -> None:
        self._llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=settings.ANTHROPIC_API_KEY,
            max_tokens=4096,
        )

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self._llm.ainvoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        )
        return response.content


class FinetunedBackend:
    """HuggingFace Fine-tuned LLaMA 3 기반 추론 백엔드.

    transformers는 선택적 의존성이므로 임포트 실패 시 명확한 오류를 냅니다.
    """

    def __init__(self) -> None:
        self._pipe = None

    def _load(self) -> None:
        """지연 로딩 — 첫 추론 요청 시 모델을 로드합니다."""
        if self._pipe is not None:
            return

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        except ImportError as e:
            raise ImportError(
                "transformers / torch 패키지가 필요합니다. "
                "pip install transformers torch accelerate 를 실행하세요."
            ) from e

        logger.info("Fine-tuned 모델 로드 중: %s", settings.HF_MODEL_ID)
        tokenizer = AutoTokenizer.from_pretrained(
            settings.HF_MODEL_ID,
            token=settings.HF_TOKEN or None,
        )
        model = AutoModelForCausalLM.from_pretrained(
            settings.HF_MODEL_ID,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            token=settings.HF_TOKEN or None,
        )
        self._pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device_map="auto",
        )
        logger.info("Fine-tuned 모델 로드 완료")

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        self._load()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        # transformers pipeline은 동기 → asyncio executor로 실행
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(
            None,
            lambda: self._pipe(
                messages,
                max_new_tokens=1024,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
            ),
        )
        return output[0]["generated_text"][-1]["content"]


class ModelService:
    """INFERENCE_BACKEND 설정에 따라 백엔드를 선택하는 통합 추론 서비스"""

    def __init__(self) -> None:
        backend = settings.INFERENCE_BACKEND.lower()
        if backend == "finetuned":
            self._backend = FinetunedBackend()
            logger.info("추론 백엔드: Fine-tuned LLaMA 3 (%s)", settings.HF_MODEL_ID)
        else:
            self._backend = ClaudeBackend()
            logger.info("추론 백엔드: Claude (claude-sonnet-4-6)")

    async def generate_retrospective_draft(
        self,
        logs_text: str,
        period_from: str,
        period_to: str,
        rag_context: str = "",
    ) -> str:
        """주간 회고 초안 생성.

        Returns:
            마크다운 형식의 회고 초안 전문
        """
        system_prompt = (
            "당신은 개발자의 성장을 돕는 AI 코치입니다.\n"
            "주어진 작업 로그와 과거 패턴을 바탕으로 진솔하고 통찰력 있는 주간 회고를 작성해주세요.\n"
            "회고는 한국어로 작성하며 마크다운 형식을 사용합니다."
        )
        user_prompt = (
            f"## 이번 주 작업 로그 ({period_from} ~ {period_to})\n\n"
            f"{logs_text}\n\n"
            f"{f'## 과거 유사 패턴{chr(10)}{rag_context}{chr(10)}{chr(10)}' if rag_context else ''}"
            "위 내용을 바탕으로 주간 회고를 작성해주세요.\n"
            "형식:\n"
            "- 제목: 한 줄 요약 (## 제목 형식)\n"
            "- 이번 주 한 일\n"
            "- 잘한 점\n"
            "- 아쉬운 점 & 개선 방향\n"
            "- 배운 것"
        )
        return await self._backend.generate(system_prompt, user_prompt)

    @property
    def backend_name(self) -> str:
        return "finetuned" if isinstance(self._backend, FinetunedBackend) else "claude"


@lru_cache(maxsize=1)
def get_model_service() -> ModelService:
    """싱글턴 ModelService 반환"""
    return ModelService()
