"""
優先度評価エージェント（最終部分）

このモジュールでは、優先度評価エージェントのエージェント定義と取得関数を提供します。
"""

from typing import Dict, Any, List
# OpenAI Agents SDK
from agents import Agent, function_tool
from models.models import PriorityReport

from nexasales_agents.priority_evaluation import integrate_evc_and_market_potential, calculate_priority_scores, generate_segment_strategies
from nexasales_agents.priority_evaluation_part2 import create_action_plan, create_priority_report


# プロンプトの定義
INSTRUCTIONS = """# システムコンテキスト
あなたは顧客セグメンテーションと市場優先度評価フレームワークの一部として、
優先度評価を担当するエージェントです。

## 目的
EVC計算と市場ポテンシャル分析の結果を統合して、セグメント別の優先度を評価し、
各セグメントに対する戦略と行動計画を策定してください。

## アプローチ
1. EVC計算結果と市場ポテンシャル分析結果を統合する
2. セグメント別の優先度スコアを計算する
3. 優先度に基づいてセグメント別の戦略を生成する
4. 各セグメントの行動計画を作成する
5. 優先度評価レポートを作成する
6. 評価結果を構造化された形式で出力する

## 出力形式
評価結果は以下の形式で出力してください：
- セグメント別の優先度スコアと優先度ランク
- 各セグメントに対する戦略と行動計画
- リソース配分の推奨事項
- 優先度評価レポート
"""

# エージェントの定義
priority_evaluation_agent = Agent(
    name="PriorityEvaluationAgent",
    instructions=INSTRUCTIONS,
    tools=[
        integrate_evc_and_market_potential,
        calculate_priority_scores,
        generate_segment_strategies,
        create_action_plan,
        create_priority_report
    ],
)

# エージェントを取得する関数
def get_priority_evaluation_agent() -> Agent:
    """優先度評価エージェントを取得します。

    Returns:
        設定済みの優先度評価エージェント
    """
    return priority_evaluation_agent
