"""LLaMA 3 QLoRA Fine-tuning 하이퍼파라미터 설정."""

from dataclasses import dataclass, field


@dataclass
class LoraConfig:
    r: int = 16                  # LoRA rank
    lora_alpha: int = 32         # scaling factor (alpha/r = 2 권장)
    lora_dropout: float = 0.05
    bias: str = "none"
    task_type: str = "CAUSAL_LM"
    target_modules: list[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ])


@dataclass
class BitsAndBytesConfig:
    load_in_4bit: bool = True
    bnb_4bit_quant_type: str = "nf4"          # NormalFloat4 — QLoRA 논문 권장
    bnb_4bit_compute_dtype: str = "bfloat16"  # 학습 시 BF16으로 역전파
    bnb_4bit_use_double_quant: bool = True     # 이중 양자화로 추가 메모리 절약


@dataclass
class TrainingArguments:
    output_dir: str = "./outputs"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 2
    per_device_eval_batch_size: int = 2
    gradient_accumulation_steps: int = 4      # 유효 배치 = 2 * 4 = 8
    gradient_checkpointing: bool = True       # T4 16GB VRAM 절약
    learning_rate: float = 2e-4
    lr_scheduler_type: str = "cosine"
    warmup_ratio: float = 0.03
    weight_decay: float = 0.001
    fp16: bool = False
    bf16: bool = True
    max_grad_norm: float = 0.3
    logging_steps: int = 10
    eval_steps: int = 50
    save_steps: int = 100
    save_total_limit: int = 2
    evaluation_strategy: str = "steps"
    load_best_model_at_end: bool = True
    report_to: str = "none"                   # wandb 미사용 시 none


@dataclass
class DataConfig:
    model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    train_file: str = "fine_tuning/data/train.jsonl"
    val_file: str = "fine_tuning/data/val.jsonl"
    max_seq_length: int = 2048
    packing: bool = False                     # 짧은 샘플 패킹 (False = 안전)


# 기본 설정 인스턴스
lora_config = LoraConfig()
bnb_config = BitsAndBytesConfig()
training_args = TrainingArguments()
data_config = DataConfig()
