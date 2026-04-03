"""Fine-tuning 데이터셋 스키마 정의.

LLaMA 3 ChatML 형식 (messages format)을 사용합니다.
"""

from dataclasses import dataclass, field

SYSTEM_PROMPT = """당신은 개발자의 성장을 돕는 AI 코치입니다.
주어진 작업 로그와 과거 패턴을 바탕으로 진솔하고 통찰력 있는 주간 회고를 작성해주세요.
회고는 한국어로 작성하며 마크다운 형식을 사용합니다."""


@dataclass
class Message:
    role: str   # "system" | "user" | "assistant"
    content: str


@dataclass
class TrainingSample:
    """학습 샘플 하나 (ChatML messages 형식)"""
    messages: list[Message]
    source: str = ""  # "real" | "synthetic"

    def to_dict(self) -> dict:
        return {
            "messages": [{"role": m.role, "content": m.content} for m in self.messages],
            "source": self.source,
        }


def build_sample(logs_text: str, period_from: str, period_to: str, retrospective: str, source: str = "real") -> TrainingSample:
    """WorkLog 텍스트 + 회고 텍스트로 학습 샘플 생성"""
    user_content = f"""## 이번 주 작업 로그 ({period_from} ~ {period_to})

{logs_text}

위 내용을 바탕으로 주간 회고를 작성해주세요.
형식:
- 제목: 한 줄 요약 (## 제목 형식)
- 이번 주 한 일
- 잘한 점
- 아쉬운 점 & 개선 방향
- 배운 것"""

    return TrainingSample(
        messages=[
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=user_content),
            Message(role="assistant", content=retrospective),
        ],
        source=source,
    )
