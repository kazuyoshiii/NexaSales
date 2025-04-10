"""
顧客セグメント抽出エージェント

このモジュールでは、公開市場調査データ、業界レポート、専門家インタビューに基づいて
「価値創出ポテンシャル」と「実現容易性」の2軸で顧客をセグメント化するエージェントを定義します。
"""

from typing import Dict, Any, List
# OpenAI Agents SDK
from agents import Agent, function_tool
from models.models import CustomerSegment, ValuePotential, ImplementationEase
from tools.common_tools import websearch_tool, extract_market_data, segment_customers





@function_tool
async def analyze_segment_characteristics(segment: CustomerSegment) -> str:
    """セグメントの特性を詳細に分析します。

    Args:
        segment: 顧客セグメント

    Returns:
        セグメントの特性分析結果
    """
    # セグメント情報から特性を詳細に分析する
    
    # セグメント情報を分析して特性を抓出
    segment_id = segment.segment_id
    segment_name = segment.name
    value_potential = segment.value_potential
    implementation_ease = segment.implementation_ease
    
    # 特性分析の実装が必要
    result = {
        "segment_id": segment_id,
        "name": segment_name,
        "value_potential": value_potential,
        "implementation_ease": implementation_ease,
        "analysis": {
            # 分析結果を加える
        }
    }
    return str(result)


# 実際の実装（デコレータなし）
async def _enhance_segment_data_impl(segments: List[CustomerSegment], market_data: str) -> List[CustomerSegment]:
    """セグメントデータを市場データで強化します - 実装部分"""
    enhanced_segments = []
    
    # サービス情報オブジェクトをJSON文字列化
    service_info_str = '{"name": "NexaSales"}'
    
    for segment in segments:
        # 業界カテゴリと企業例の取得
        import json
        import ast
        
        # 市場規模と獲得確率のデフォルト値設定
        market_size = 0
        acquisition_prob = 0.0
        
        # 業界カテゴリの特定
        industry_categories = await identify_industry_categories(segment.segment_id, service_info_str)
        
        # 企業例の生成
        example_companies = await generate_example_companies(segment.segment_id, industry_categories)
        
        # BANT情報の生成
        bant_info = await generate_bant_analysis(segment.segment_id, service_info_str, market_data)
        
        # BANT情報オブジェクトの作成
        from models.models import BANTBudget, BANTAuthority, BANTTimeline, BANTInformation
        
        bant_budget = BANTBudget(
            range=bant_info.get("budget", {}).get("range"),
            cycle=bant_info.get("budget", {}).get("cycle"),
            decision_maker=bant_info.get("budget", {}).get("decision_maker")
        )
        
        bant_authority = BANTAuthority(
            final_decision_maker=bant_info.get("authority", {}).get("final_decision_maker"),
            champion=bant_info.get("authority", {}).get("champion"),
            process=bant_info.get("authority", {}).get("process")
        )
        
        bant_timeline = BANTTimeline(
            consideration_period=bant_info.get("timeline", {}).get("consideration_period"),
            cycle=bant_info.get("timeline", {}).get("cycle"),
            urgency=bant_info.get("timeline", {}).get("urgency")
        )
        
        bant_information = BANTInformation(
            budget=bant_budget,
            authority=bant_authority,
            need=bant_info.get("need", []),
            timeline=bant_timeline
        )
        
        # セグメントタイプの判定
        from models.models import SegmentType
        segment_type = None
        if segment.value_potential == "high" and segment.implementation_ease == "high":
            segment_type = SegmentType.HIGH_VALUE_LOW_BARRIER
        elif segment.value_potential == "high" and segment.implementation_ease == "low":
            segment_type = SegmentType.HIGH_VALUE_HIGH_BARRIER
        elif segment.value_potential == "low" and segment.implementation_ease == "high":
            segment_type = SegmentType.LOW_VALUE_LOW_BARRIER
        elif segment.value_potential == "low" and segment.implementation_ease == "low":
            segment_type = SegmentType.LOW_VALUE_HIGH_BARRIER
        
        # セグメント名の生成 - 常に価値と実装障壁に基づいた命名を使用
        if segment_type == SegmentType.HIGH_VALUE_LOW_BARRIER:
            segment_name = "高価値・低障壁"
        elif segment_type == SegmentType.HIGH_VALUE_HIGH_BARRIER:
            segment_name = "高価値・高障壁"
        elif segment_type == SegmentType.LOW_VALUE_LOW_BARRIER:
            segment_name = "低価値・低障壁"
        elif segment_type == SegmentType.LOW_VALUE_HIGH_BARRIER:
            segment_name = "低価値・高障壁"
        else:
            segment_name = segment.name or "未分類セグメント"
        
        # セグメントの強化
        enhanced_segment = CustomerSegment(
            segment_id=segment.segment_id,
            name=segment_name,
            value_potential=segment.value_potential,
            implementation_ease=segment.implementation_ease,
            segment_type=segment_type,
            description=segment.description,
            characteristics=segment.characteristics,
            industry_categories=industry_categories,
            example_companies=example_companies,
            bant_information=bant_information,
            market_size=market_size,
            acquisition_probability=acquisition_prob
        )
        
        enhanced_segments.append(enhanced_segment)
    
    return enhanced_segments


# 外部から呼び出せる非デコレータ関数
async def enhance_segment_data(segments: List[CustomerSegment], market_data: str) -> List[CustomerSegment]:
    """セグメントデータを市場データで強化します（外部から呼び出し可能）

    Args:
        segments: 顧客セグメントのリスト
        market_data: 市場データ

    Returns:
        強化された顧客セグメントのリスト
    """
    return await _enhance_segment_data_impl(segments, market_data)


# エージェント用のツール関数 - 非同期処理の修正版
def _enhance_segment_data_tool_wrapper(segments: List[CustomerSegment], market_data: str) -> List[CustomerSegment]:
    """セグメントデータを市場データで強化します。

    Args:
        segments: 顧客セグメントのリスト
        market_data: 市場データ

    Returns:
        強化された顧客セグメントのリスト
    """
    import asyncio
    try:
        # 現在のイベントループを取得
        loop = asyncio.get_event_loop()
        # 非同期関数を同期的に実行
        return loop.run_until_complete(_enhance_segment_data_impl(segments, market_data))
    except RuntimeError as e:
        # 現在のループが閉じられている場合は新しいループを作成
        if "There is no current event loop in thread" in str(e):
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(_enhance_segment_data_impl(segments, market_data))
            finally:
                new_loop.close()
        # 実行中のループ内からの呼び出しの場合は、セグメントをそのまま返す
        # これはエラーを返すよりも、処理を継続させるためのフォールバック
        import logging
        logging.warning(f"セグメント強化処理中に非同期エラーが発生しました: {e}")
        return segments

# function_toolの設定
enhance_segment_data_tool = function_tool(_enhance_segment_data_tool_wrapper)


@function_tool
async def generate_bant_analysis(segment_id: str, service_info: str, market_data: str) -> Dict[str, Any]:
    """セグメントのBANT情報を生成します。

    Args:
        segment_id: セグメントID
        service_info: サービス情報
        market_data: 市場データ

    Returns:
        BANTフレームワークに基づく分析情報
    """

    # OpenAIへのリクエストでそのセグメントのBANT情報を生成
    # サービス情報とセグメントIDに基づいて生成
    
    # 空のBANT情報を返す
    bant_info = {
        "budget": {
            "range": "",
            "cycle": "",
            "decision_maker": ""
        },
        "authority": {
            "final_decision_maker": "",
            "champion": "",
            "process": ""
        },
        "need": [],
        "timeline": {
            "consideration_period": "",
            "cycle": "",
            "urgency": ""
        }
    }
    
    return bant_info


@function_tool
async def identify_industry_categories(segment_id: str, service_info: str) -> List[str]:
    """セグメントの業界カテゴリを特定します。

    Args:
        segment_id: セグメントID
        service_info: サービス情報

    Returns:
        業界カテゴリのリスト
    """
    # OpenAIへのリクエストでそのセグメントに関連する業界カテゴリを生成
    
    # 空のリストを返す
    return []


@function_tool
async def generate_example_companies(segment_id: str, industry_categories: List[str]) -> List[str]:
    """セグメントの具体的な企業例を生成します。

    Args:
        segment_id: セグメントID
        industry_categories: 業界カテゴリのリスト

    Returns:
        具体的な企業例のリスト
    """
    # OpenAIへのリクエストで業界カテゴリに基づいて具体的な企業例を生成
    
    # 空のリストを返す
    return []


# プロンプトの定義
INSTRUCTIONS = """# システムコンテキスト
あなたは顧客セグメンテーションと市場優先度評価フレームワークの一部として、
価値創出ポテンシャルと実現容易性の2軸で顧客をセグメント化し、各セグメントのBANT情報を提供するエージェントです。

# 入力
- サービス説明: 分析対象のサービスの詳細情報
- 市場データ: 業界レポート、市場調査データ

# 実行タスク
1. 「価値創出ポテンシャル」(高/低)と「実現容易性」(高/低)の2軸で4つの基本セグメントを特定してください。
2. 各セグメントに以下の詳細を付与してください：
   a. セグメントID(s1, s2, s3, s4)
   b. 具体的な業界軸と企業例（最低3社）
   c. 完全なBANT情報（Budget, Authority, Need, Timeline）
3. セグメント情報は、営業活動に直接活用できる具体性を持たせてください。

# 重要: セグメント命名規則
各セグメントには必ず以下の命名規則に従った名前を付けてください：
- 高価値・低障壁：価値創出ポテンシャルが高く、実現容易性が高いセグメント
- 高価値・高障壁：価値創出ポテンシャルが高く、実現容易性が低いセグメント
- 低価値・低障壁：価値創出ポテンシャルが低く、実現容易性が高いセグメント
- 低価値・高障壁：価値創出ポテンシャルが低く、実現容易性が低いセグメント

会社規模（大企業・中小企業など）ではなく、必ず上記の命名規則を使用してください。

# 出力形式
レスポンスは以下の構造で返してください：

## セグメント: [セグメント名]
- セグメントID: s1（必ず「s」+数字の形式。例: s1, s2, s3...）
- 価値創出ポテンシャル: high/low（英語表記に統一）
- 実現容易性: high/low（英語表記に統一）
- 説明: [セグメントの簡潔な説明]
- 業界カテゴリ:
  - [業界1]
  - [業界2]
  - [業界3]
- 企業例:
  - [企業1]
  - [企業2]
  - [企業3]
- BANT情報:
  - Budget（予算）:
    - 予算範囲: [予算範囲]
    - 予算サイクル: [予算サイクル]
    - 予算決定者: [予算決定者]
  - Authority（権限）:
    - 最終決定者: [最終決定者の役職]
    - 推進者: [推進者の役職]
    - 意思決定プロセス: [プロセスの説明]
  - Need（ニーズ）:
    - [ニーズ1]
    - [ニーズ2]
    - [ニーズ3]
  - Timeline（タイムライン）:
    - 検討期間: [検討にかかる期間]
    - 導入サイクル: [導入判断のサイクル]
    - 緊急度: [緊急度の高低]
- 特性:
  - [特性1]
  - [特性2]
  - [特性3]
※ 価値創出ポテンシャルと実現容易性は、高(high)/低(low)の2段階で評価してください
※ 特性や具体例は、そのサービスに合わせた現実的で具体的な内容にしてください
"""

# エージェントの定義
customer_segment_agent = Agent(
    name="CustomerSegmentExtractionAgent",
    instructions=INSTRUCTIONS,
    tools=[
        websearch_tool,
        extract_market_data,
        segment_customers,
        analyze_segment_characteristics,
        enhance_segment_data_tool,  # 新しいツール関数名に変更
        generate_bant_analysis,
        identify_industry_categories,
        generate_example_companies
    ],
)

# エージェントを取得する関数
def get_customer_segment_agent() -> Agent:
    """顧客セグメント抽出エージェントを取得します。

    Returns:
        設定済みの顧客セグメント抽出エージェント
    """
    return customer_segment_agent
