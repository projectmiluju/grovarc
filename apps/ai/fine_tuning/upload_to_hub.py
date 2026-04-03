"""Fine-tuned 모델을 Hugging Face Hub에 업로드.

Colab에서 학습 완료 후 또는 로컬에서 실행합니다.

사용법:
    # 병합 모델 업로드
    python -m fine_tuning.upload_to_hub \
        --model-dir /path/to/merged-model \
        --repo-id projectmiluju/grovarc-llama3-8b \
        --private

    # LoRA 어댑터만 업로드
    python -m fine_tuning.upload_to_hub \
        --model-dir /path/to/lora-adapter \
        --repo-id projectmiluju/grovarc-llama3-8b-adapter \
        --adapter-only --private
"""

import argparse
import json
import logging
from pathlib import Path

from huggingface_hub import HfApi, login

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MODEL_CARD_TEMPLATE = """---
language:
- ko
license: llama3
base_model: meta-llama/Meta-Llama-3-8B-Instruct
tags:
- text-generation
- llama
- lora
- qlora
- peft
- grovarc
- retrospective
datasets:
- custom
pipeline_tag: text-generation
---

# grovarc-llama3-8b

개발자 주간 회고 초안 생성에 특화된 LLaMA 3 8B 파인튜닝 모델.

[Grovarc](https://github.com/projectmiluju/grovarc) 서비스의 AI 코어 모델입니다.

## 모델 설명

- **Base model**: `meta-llama/Meta-Llama-3-8B-Instruct`
- **Fine-tuning 방식**: QLoRA (4-bit NF4 + Double Quantization)
- **LoRA 설정**: r=16, alpha=32, 7개 레이어 (attention + FFN)
- **학습 데이터**: 실제 WorkLog + 회고 페어 + Claude Haiku 합성 데이터
- **학습 환경**: Google Colab T4 GPU

## 사용법

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "projectmiluju/grovarc-llama3-8b"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

messages = [
    {
        "role": "system",
        "content": "당신은 개발자의 성장을 돕는 AI 코치입니다. 주어진 작업 로그를 바탕으로 진솔하고 통찰력 있는 주간 회고를 작성해주세요. 회고는 한국어로 작성하며 마크다운 형식을 사용합니다.",
    },
    {
        "role": "user",
        "content": "## 이번 주 작업 로그 (2026-03-28 ~ 2026-04-03)\\n\\n[2026-03-28] ...",
    },
]

input_ids = tokenizer.apply_chat_template(
    messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
).to(model.device)

output = model.generate(input_ids, max_new_tokens=512, do_sample=True, temperature=0.7)
print(tokenizer.decode(output[0][input_ids.shape[-1]:], skip_special_tokens=True))
```

## 학습 하이퍼파라미터

| 파라미터 | 값 |
|---------|-----|
| epochs | 3 |
| batch size (유효) | 8 |
| learning rate | 2e-4 |
| lr scheduler | cosine |
| max_seq_length | 2048 |
| LoRA r | 16 |
| LoRA alpha | 32 |
| 학습 가능 파라미터 | ~20M (전체의 0.24%) |

## 한계

- 학습 데이터가 개발자 도메인에 특화되어 일반 대화 성능은 base model 대비 낮을 수 있음
- 합성 데이터 비중이 높아 실제 회고 스타일과 차이가 있을 수 있음
"""


def create_model_card(output_path: Path, extra_info: dict | None = None) -> None:
    """모델 카드 README.md 생성"""
    content = MODEL_CARD_TEMPLATE
    if extra_info:
        content += f"\n## 추가 정보\n\n```json\n{json.dumps(extra_info, ensure_ascii=False, indent=2)}\n```\n"
    output_path.write_text(content, encoding="utf-8")
    logger.info("모델 카드 생성: %s", output_path)


def upload_model(
    model_dir: Path,
    repo_id: str,
    hf_token: str,
    private: bool = True,
    adapter_only: bool = False,
) -> str:
    """모델 디렉토리를 HF Hub에 업로드.

    Returns:
        업로드된 리포지토리 URL
    """
    api = HfApi(token=hf_token)

    # 리포지토리 생성 (이미 존재하면 무시)
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="model",
            private=private,
            exist_ok=True,
        )
        logger.info("리포지토리 준비 완료: %s (private=%s)", repo_id, private)
    except Exception as e:
        logger.error("리포지토리 생성 실패: %s", e)
        raise

    # 모델 카드 생성 후 디렉토리에 포함
    readme_path = model_dir / "README.md"
    if not readme_path.exists():
        create_model_card(readme_path)

    # 업로드
    logger.info("업로드 시작 (이 작업은 모델 크기에 따라 수 분~수십 분 걸립니다)...")
    api.upload_folder(
        folder_path=str(model_dir),
        repo_id=repo_id,
        repo_type="model",
        commit_message="Upload fine-tuned model" if not adapter_only else "Upload LoRA adapter",
    )

    repo_url = f"https://huggingface.co/{repo_id}"
    logger.info("업로드 완료: %s", repo_url)
    return repo_url


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tuned 모델 HF Hub 업로드")
    parser.add_argument(
        "--model-dir",
        type=Path,
        required=True,
        help="업로드할 모델 디렉토리 경로",
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        default="projectmiluju/grovarc-llama3-8b",
        help="HF Hub 리포지토리 ID (기본: projectmiluju/grovarc-llama3-8b)",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="HF API 토큰 (없으면 환경변수 HF_TOKEN 사용)",
    )
    parser.add_argument("--private", action="store_true", default=True, help="비공개 리포로 설정")
    parser.add_argument("--public", dest="private", action="store_false", help="공개 리포로 설정")
    parser.add_argument("--adapter-only", action="store_true", help="LoRA 어댑터만 업로드")
    args = parser.parse_args()

    import os
    hf_token = args.token or os.environ.get("HF_TOKEN", "")
    if not hf_token:
        raise ValueError("HF_TOKEN이 필요합니다. --token 또는 환경변수 HF_TOKEN을 설정하세요.")

    login(token=hf_token)

    if not args.model_dir.exists():
        raise FileNotFoundError(f"모델 디렉토리가 없습니다: {args.model_dir}")

    url = upload_model(
        model_dir=args.model_dir,
        repo_id=args.repo_id,
        hf_token=hf_token,
        private=args.private,
        adapter_only=args.adapter_only,
    )
    print(f"\n업로드 완료: {url}")


if __name__ == "__main__":
    main()
