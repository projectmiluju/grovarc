"""train_config 설정값 검증 테스트."""

from fine_tuning.train_config import (
    BitsAndBytesConfig,
    DataConfig,
    LoraConfig,
    TrainingArguments,
    bnb_config,
    data_config,
    lora_config,
    training_args,
)


def test_lora_config_defaults():
    cfg = LoraConfig()
    assert cfg.r == 16
    assert cfg.lora_alpha == 32
    assert cfg.lora_alpha / cfg.r == 2.0   # 권장 scaling 비율
    assert cfg.task_type == "CAUSAL_LM"
    assert "q_proj" in cfg.target_modules
    assert "down_proj" in cfg.target_modules
    assert len(cfg.target_modules) == 7    # LLaMA 3 attention + FFN


def test_bnb_config_defaults():
    cfg = BitsAndBytesConfig()
    assert cfg.load_in_4bit is True
    assert cfg.bnb_4bit_quant_type == "nf4"
    assert cfg.bnb_4bit_use_double_quant is True


def test_training_args_effective_batch_size():
    args = TrainingArguments()
    effective_batch = args.per_device_train_batch_size * args.gradient_accumulation_steps
    assert effective_batch == 8   # T4 VRAM에서 안정적인 유효 배치 크기


def test_training_args_bf16_not_fp16():
    """BF16과 FP16을 동시에 켜면 충돌 — BF16만 True여야 함"""
    args = TrainingArguments()
    assert args.bf16 is True
    assert args.fp16 is False


def test_data_config_model_id():
    cfg = DataConfig()
    assert "llama-3" in cfg.model_id.lower() or "Llama-3" in cfg.model_id
    assert cfg.max_seq_length == 2048


def test_singleton_instances_are_defaults():
    """기본 인스턴스가 정상 생성되는지 확인"""
    assert lora_config.r == 16
    assert bnb_config.load_in_4bit is True
    assert training_args.num_train_epochs == 3
    assert "train.jsonl" in data_config.train_file
