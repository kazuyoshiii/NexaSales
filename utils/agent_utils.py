"""
エージェントユーティリティ

このモジュールでは、エージェントの操作に関するユーティリティ関数を提供します。
公式ドキュメントに基づき、シンプルで分かりやすい実装を目指します。
"""

import logging
import traceback
from typing import Dict, Any, Optional
import os

# OpenAI Agents SDKのインポート
from agents import Runner, Agent, RunConfig, gen_trace_id

# ロガーの設定
logger = logging.getLogger(__name__)

def get_tracer():
    """トレーサーを取得します。
    
    OpenAI Agents SDKのTraceクラスは、Runner.run()メソッドが自動的に使用するため、
    別途グローバルオブジェクトとして保持する必要がありません。
    
    Returns:
        None - トレースは内部的に管理されます
    """
    return None

async def call_agent(agent: Any, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    エージェントを呼び出します。
    
    OpenAI Agents SDKの公式ドキュメントに基づくシンプルな実装です。
    contextにtracer_idが含まれる場合、それを使用して同一のトレースに記録します。
    
    Args:
        agent: 呼び出すエージェント
        message: エージェントに送信するメッセージ
        context: オプションのコンテキスト情報。trace_idを含めて渡すことで同一トレースを実現。
        
    Returns:
        エージェントからのレスポンスオブジェクト
    """
    # コンテキストの初期化
    if context is None:
        context = {}
    
    try:
        # ログ出力
        agent_name = getattr(agent, "name", agent.__class__.__name__)
        logger.info(f"エージェント {agent_name} を実行します")
        
        # OpenAI APIキーが設定されているか確認
        if not os.environ.get("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEYが環境変数に設定されていません")
            return {
                "error": "OPENAI_API_KEYが設定されていません",
                "result": "エージェントの実行にはOpenAI APIキーが必要です"
            }
        
        # 詳細なデバッグ情報を表示
        agent_info = {
            "name": agent_name,
            "message_length": len(message),
            "context_keys": list(context.keys()) if context else []
        }
        logger.debug(f"エージェント情報: {agent_info}")
        
        # OpenAI Agents SDK Runner APIを使用してエージェントを実行
        # max_turnsパラメータをエージェントに応じて調整
        # 市場ポテンシャル分析など、複雑なエージェントにはより大きな値を設定
        if 'MarketPotential' in agent_name:
            max_turns_value = 20  # 市場ポテンシャル分析は複雑なので多めに設定
        elif 'PriorityEvaluation' in agent_name:
            max_turns_value = 15  # 優先度評価も複雑なので多め
        else:
            max_turns_value = 12  # 標準値

        logger.info(f"エージェント {agent_name} のmax_turnsを {max_turns_value} に設定して実行します")
        
        # RunConfigを作成してトレースIDを設定
        run_config = None
        
        # コンテキストからtrace_idを取得（存在する場合）
        if context and "trace_id" in context:
            trace_id = context["trace_id"]
            workflow_name = context.get("workflow_name", "NexaSalesワークフロー")
            
            # RunConfigを作成してトレースIDを設定
            run_config = RunConfig(
                workflow_name=workflow_name,
                trace_id=trace_id,
                trace_metadata={"agent_name": agent_name}
            )
            logger.debug(f"共有トレースIDを使用: {trace_id}, ワークフロー: {workflow_name}")
        
        # Runner.runを実行
        result = await Runner.run(
            agent, 
            input=message,  # 公式ドキュメントではinputを使用
            context=context,
            max_turns=max_turns_value,  # エージェントに応じて調整されたmax_turns
            run_config=run_config  # トレースIDを含むRunConfigを渡す
        )
        
        # 成功時の詳細ログ
        response_length = len(result.final_output) if hasattr(result, "final_output") else 0
        turns_used = getattr(result, "turns_used", "N/A")
        logger.info(f"エージェント {agent_name} が正常に実行されました (ターン数: {turns_used}, 応答長: {response_length})")
        
        # ターン数が多い場合は警告表示
        if hasattr(result, "turns_used") and result.turns_used > max_turns_value * 0.8:
            logger.warning(f"エージェント {agent_name} のターン数が多いです ({result.turns_used}/{max_turns_value})")
        
        return {"result": result.final_output}
    except Exception as e:
        logger.error(f"エージェント呼び出し中にエラーが発生しました: {e}")
        traceback.print_exc()
        
        return {
            "error": str(e),
            "result": "エージェントの実行中にエラーが発生しました"
        }



