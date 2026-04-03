"""Claude API로 합성 학습 데이터 생성.

실제 데이터가 부족할 때 Claude를 활용해 다양한 WorkLog + 회고 페어를 생성합니다.

사용법:
    python -m fine_tuning.generate_synthetic --count 100 --output fine_tuning/data/synthetic.jsonl
"""

import argparse
import asyncio
import json
import logging
import random
from pathlib import Path

import anthropic

from app.core.config import settings
from fine_tuning.schema import build_sample

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# 다양한 개발자 페르소나와 기술 스택 조합
_PERSONAS = [
    {"role": "백엔드 개발자", "stacks": ["Spring Boot", "Kotlin", "PostgreSQL", "Redis", "Kafka"]},
    {"role": "프론트엔드 개발자", "stacks": ["React", "TypeScript", "Next.js", "TailwindCSS", "Zustand"]},
    {"role": "풀스택 개발자", "stacks": ["FastAPI", "Python", "Vue.js", "Docker", "GitHub Actions"]},
    {"role": "AI/ML 엔지니어", "stacks": ["PyTorch", "LangChain", "HuggingFace", "RAG", "LangGraph"]},
    {"role": "DevOps 엔지니어", "stacks": ["Kubernetes", "Terraform", "AWS", "Prometheus", "Grafana"]},
]

_MOODS_WEIGHTS = {
    "GREAT": 0.2,
    "GOOD": 0.4,
    "NEUTRAL": 0.2,
    "BAD": 0.15,
    "TERRIBLE": 0.05,
}

_PERIOD_WEEKS = ["2026-01-06~2026-01-10", "2026-01-13~2026-01-17", "2026-01-20~2026-01-24",
                 "2026-02-03~2026-02-07", "2026-02-10~2026-02-14", "2026-03-03~2026-03-07"]


async def generate_one_sample(client: anthropic.AsyncAnthropic, persona: dict, period: str) -> dict | None:
    """Claude로 WorkLog 묶음 + 회고 한 쌍 생성"""
    period_from, period_to = period.split("~")
    stacks = random.sample(persona["stacks"], k=min(3, len(persona["stacks"])))
    mood = random.choices(list(_MOODS_WEIGHTS.keys()), weights=list(_MOODS_WEIGHTS.values()))[0]

    prompt = f"""당신은 {persona['role']}입니다. 아래 조건에 맞는 가상의 주간 작업 로그 4~6개와 해당 주간의 회고를 생성해주세요.

조건:
- 기간: {period_from} ~ {period_to}
- 기술 스택: {', '.join(stacks)}
- 전반적인 기분/컨디션: {mood}
- 로그는 실제 개발 업무처럼 구체적이고 자연스럽게

응답 형식 (JSON):
{{
  "logs": [
    {{"date": "YYYY-MM-DD", "title": "작업 제목", "content": "작업 내용 2~4문장"}},
    ...
  ],
  "retrospective": "마크다운 회고 전문 (제목 포함, 400자 이상)"
}}

JSON만 반환하세요."""

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()

        # JSON 코드블록 제거
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()

        data = json.loads(raw)
        logs = data.get("logs", [])
        retrospective = data.get("retrospective", "")

        if not logs or not retrospective or len(retrospective) < 200:
            return None

        logs_text = "\n\n".join(
            f"[{log['date']}] {log['title']}\n{log['content']}" for log in logs
        )
        sample = build_sample(
            logs_text=logs_text,
            period_from=period_from,
            period_to=period_to,
            retrospective=retrospective,
            source="synthetic",
        )
        return sample.to_dict()

    except Exception as e:
        logger.warning("샘플 생성 실패: %s", e)
        return None


async def generate_synthetic_dataset(output_path: Path, count: int, concurrency: int = 5) -> int:
    """합성 데이터 count개 생성 후 JSONL 저장.

    Returns:
        실제 저장된 샘플 수
    """
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    # 페르소나 × 기간 조합 생성
    combos = [
        (random.choice(_PERSONAS), random.choice(_PERIOD_WEEKS))
        for _ in range(count)
    ]

    semaphore = asyncio.Semaphore(concurrency)

    async def bounded(persona, period):
        async with semaphore:
            return await generate_one_sample(client, persona, period)

    tasks = [bounded(p, w) for p, w in combos]
    results = await asyncio.gather(*tasks)

    samples = [r for r in results if r is not None]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    logger.info("합성 데이터 %d/%d건 저장 → %s", len(samples), count, output_path)
    return len(samples)


def main() -> None:
    parser = argparse.ArgumentParser(description="Claude API로 합성 학습 데이터 생성")
    parser.add_argument("--count", type=int, default=100, help="생성할 샘플 수 (기본: 100)")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("fine_tuning/data/synthetic.jsonl"),
        help="출력 JSONL 파일 경로",
    )
    parser.add_argument("--concurrency", type=int, default=5, help="동시 요청 수 (기본: 5)")
    args = parser.parse_args()

    asyncio.run(generate_synthetic_dataset(args.output, args.count, args.concurrency))


if __name__ == "__main__":
    main()
