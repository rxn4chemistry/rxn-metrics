def convert_class_token_idx_for_tranlation_models(class_token_idx: int) -> str:
    return f"[{class_token_idx}]"
