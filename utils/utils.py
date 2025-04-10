"""
NexaSales顧客セグメンテーションシステムのユーティリティ関数

このモジュールでは、システム全体で使用する共通のユーティリティ関数を定義します。
ロギング、設定管理、エラーハンドリングなどの機能を提供します。
"""

import logging
import os
import json
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv


# ロギング設定
def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """ロギングの設定を行います。

    Args:
        log_level: ロギングレベル（"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"）

    Returns:
        設定済みのロガーインスタンス
    """
    # HTTP通信関連のログを抑制
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("nexa_sales.log", encoding="utf-8")
        ]
    )
    return logging.getLogger("NexaSales")


# 環境変数の読み込み
def load_env_vars() -> Dict[str, str]:
    """環境変数を読み込みます。

    Returns:
        環境変数の辞書
    """
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY"]
    env_vars = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"環境変数 {var} が設定されていません。.envファイルを確認してください。")
        env_vars[var] = value
    
    # オプションの環境変数
    env_vars["MODEL_NAME"] = os.getenv("MODEL_NAME", "gpt-4o")
    
    return env_vars


# 結果の保存
def save_results(results: Dict[str, Any], filename: str = "results.json") -> None:
    """結果をJSONファイルに保存します。

    Args:
        results: 保存する結果データ
        filename: 保存先のファイル名
    """
    os.makedirs("results", exist_ok=True)
    filepath = os.path.join("results", filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


# エラーハンドリング
class NexaSalesError(Exception):
    """NexaSalesシステムの基本エラークラス"""
    pass


class APIError(NexaSalesError):
    """API関連のエラー"""
    pass


class DataValidationError(NexaSalesError):
    """データ検証エラー"""
    pass


class WorkflowError(NexaSalesError):
    """ワークフロー実行エラー"""
    pass


# エラーハンドリング関数
def handle_error(error: Exception, logger: logging.Logger) -> None:
    """エラーを適切に処理します。

    Args:
        error: 発生したエラー
        logger: ロガーインスタンス
    """
    if isinstance(error, NexaSalesError):
        logger.error(f"{error.__class__.__name__}: {str(error)}")
    else:
        logger.exception("予期しないエラーが発生しました")


# データ変換ユーティリティ
def convert_to_json_serializable(data: Any) -> Any:
    """データをJSON直列化可能な形式に変換します。

    Args:
        data: 変換するデータ

    Returns:
        JSON直列化可能な形式に変換されたデータ
    """
    if hasattr(data, "model_dump"):
        # Pydanticモデルの場合
        return data.model_dump()
    elif hasattr(data, "dict"):
        # 古いPydanticモデルの場合
        return data.dict()
    elif isinstance(data, dict):
        return {k: convert_to_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_json_serializable(item) for item in data]
    elif isinstance(data, (str, int, float, bool, type(None))):
        return data
    else:
        # その他のオブジェクトは文字列に変換
        return str(data)
