"""
市場ポテンシャル分析エージェント

このモジュールでは、各セグメントの市場規模を分析し、業界レポート、市場調査、専門家予測から
各セグメントの企業数を算出し、競合状況、市場動向、商品適合性からセグメント別の獲得確率を推定するエージェントを定義します。
"""

from typing import Dict, Any, List
# OpenAI Agents SDK
from agents import Agent, function_tool
from models.models import MarketPotential, CustomerSegment
from tools.common_tools import websearch_tool, extract_market_data


@function_tool
async def analyze_market_size(segment: CustomerSegment) -> str:
    """セグメントの市場規模を分析します。

    Args:
        segment: 顧客セグメント

    Returns:
        市場規模分析結果
    """
    # セグメント情報から市場規模を分析
    # OpenAIへのリクエストで市場規模情報を生成
    
    # 市場規模の基本構造を定義
    market_size_data = {
        "total_companies": 0,  # セグメント内の企業数
        "annual_growth_rate": 0.0,  # 年間成長率
        "total_market_value": 0,  # 市場規模金額
        "average_company_size": 0,  # 平均企業規模
        "data_sources": [],  # データソース
        "confidence_level": ""  # 信頼度
    }
    
    # 実際の市場調査データから情報を抽出し入力する
    
    return str(market_size_data)


@function_tool
async def analyze_competitive_landscape(segment_id: str) -> str:
    """セグメントの競合状況を分析します。

    Args:
        segment_id: セグメントID

    Returns:
        競合状況分析結果
    """
    # セグメントIDに基づいて競合状況を分析
    # OpenAIへのリクエストで競合状況情報を生成
    
    # 競合分析の基本構造を定義
    competitive_data = {
        "major_competitors": [],  # 主要競合他社
        "market_concentration": "",  # 市場集中度
        "entry_barriers": "",  # 参入障壁
        "competitive_intensity": "",  # 競争強度
        "key_success_factors": [],  # 成功要因
        "our_competitive_position": ""  # 自社の競争ポジション
    }
    
    # 実際の市場データから競合状況を分析し入力する
    
    return str(competitive_data)


@function_tool
async def estimate_acquisition_probability(
    segment_id: str,
    market_size_data: str,
    competitive_data: str
) -> str:
    """セグメントの獲得確率を推定します。

    Args:
        segment_id: セグメントID
        market_size_data: 市場規模データ
        competitive_data: 競合状況データ

    Returns:
        獲得確率推定結果
    """
    # 市場規模データと競合状況データから獲得確率を推定
    # OpenAIへのリクエストで獲得確率情報を生成
    
    # 文字列から辞書データに変換する処理を実装
    try:
        market_data = eval(market_size_data) if isinstance(market_size_data, str) else market_size_data
        competitive_info = eval(competitive_data) if isinstance(competitive_data, str) else competitive_data
    except Exception as e:
        # データ変換に失敗した場合は空の辞書を使用
        market_data = {}
        competitive_info = {}
    
    # 獲得確率の基本構造を定義
    acquisition_data = {
        "base_probability": 0.0,  # 基本獲得確率
        "factors": {
            "product_fit": {
                "weight": 0.3,
                "score": 0.0,
                "justification": ""
            },
            "competitive_position": {
                "weight": 0.3,
                "score": 0.0,
                "justification": ""
            },
            "market_trends": {
                "weight": 0.2,
                "score": 0.0,
                "justification": ""
            },
            "entry_barriers": {
                "weight": 0.2,
                "score": 0.0,
                "justification": ""
            }
        },
        "adjusted_probability": 0.0,
        "confidence_level": ""
    }
    
    # 実際の分析データから獲得確率を計算し入力する
    
    # 市場規模データ、競合状況データを使用して各要因の評価を行う
    # 実際の実装では、これらのデータに基づいて評価を行う
    
    # OpenAIを使用して計算を行う場合は、ここで適切な処理を実装
    
    # 各要因のスコアと重みから調整後の獲得確率を計算
    # 実装例：重み付けされたスコアの合計を計算
    weighted_score = 0.0
    for factor_name, factor in acquisition_data["factors"].items():
        # 各要因のスコアがあれば計算に使用
        if "score" in factor and "weight" in factor:
            weighted_score += factor["score"] * factor["weight"]
    
    # 基本確率と加重スコアから最終獲得確率を計算
    # 基本確率が設定されていない場合は0を使用
    acquisition_data["adjusted_probability"] = acquisition_data.get("base_probability", 0.0)
    
    return str(acquisition_data)


@function_tool
async def calculate_segment_potential(
    segment_id: str,
    evc_result: str,  # evc_calculation.pyから得られたEVC結果
    segment_info: str  # セグメント情報（必須）
) -> str:
    """セグメントの市場ポテンシャルをAIによる推計で算出します。
    
    Args:
        segment_id: セグメントID
        evc_result: EVCの計算結果（JSON文字列形式）
        segment_info: セグメント情報
        
    Returns:
        市場ポテンシャル計算結果
    """
    # セグメント情報とEVC結果を解析
    import json
    
    try:
        segment_data = json.loads(segment_info)
        evc_data = json.loads(evc_result)
    except Exception as e:
        return str({
            "error": "データ形式が不正です",
            "message": str(e)
        })
    
    # セグメント情報とEVC値を確認
    if not evc_data.get("evc_value"):
        return str({
            "error": "EVC値が見つかりません",
            "message": "有効なEVC計算結果が必要です"
        })
    
    # EVCの値を取得
    evc_value = evc_data.get("evc_value")
    
    # AIによる企業数の推計
    company_estimate = await estimate_companies_with_ai(segment_id, segment_data)
    
    # AIによる獲得率の推計
    acquisition_rate = await estimate_acquisition_rate_with_ai(segment_id, segment_data)
    
    # ポテンシャル計算
    min_potential = company_estimate["min"] * acquisition_rate["min"] * evc_value
    expected_potential = company_estimate["expected"] * acquisition_rate["expected"] * evc_value
    max_potential = company_estimate["max"] * acquisition_rate["max"] * evc_value
    
    # 結果を構造化
    result = {
        "segment_id": segment_id,
        "companies": company_estimate,
        "acquisition_rate": acquisition_rate,
        "evc_value": evc_value,
        "potential_value": {
            "min": min_potential,
            "expected": expected_potential,
            "max": max_potential
        },
        "calculation_formula": "ポテンシャル = 企業数 × 獲得率 × EVC"
    }
    
    return str(result)


async def estimate_companies_with_ai(segment_id: str, segment_data: dict) -> dict:
    """セグメントの企業数をAIで推計します。
    
    Args:
        segment_id: セグメントID
        segment_data: セグメント情報
        
    Returns:
        企業数の推計結果（最小値、期待値、最大値）
    """
    from openai import OpenAI
    import json
    
    client = OpenAI()
    
    # AIへのプロンプト作成
    prompt = f"""
    以下のセグメント情報に基づいて、日本市場における企業数を推計してください。
    最小値、期待値、最大値を推計し、推計ロジックも説明してください。
    
    セグメントID: {segment_id}
    セグメント情報: {json.dumps(segment_data, ensure_ascii=False)}
    
    レスポンスは以下のJSON形式で返してください:
    {{
      "min": 最小企業数（整数）,
      "expected": 期待企業数（整数）,
      "max": 最大企業数（整数）,
      "logic": "推計ロジックの説明"
    }}
    """
    
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたは市場分析の専門家です。"},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    # レスポンスからJSONを抽出
    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return {
            "min": 100,
            "expected": 500,
            "max": 1000,
            "logic": "AIレスポンスの解析に失敗したため、デフォルト値を設定しました。"
        }


async def estimate_acquisition_rate_with_ai(segment_id: str, segment_data: dict) -> dict:
    """セグメントの獲得率をAIで推計します。
    
    Args:
        segment_id: セグメントID
        segment_data: セグメント情報
        
    Returns:
        獲得率の推計結果（最小値、期待値、最大値）
    """
    from openai import OpenAI
    import json
    
    client = OpenAI()
    
    # AIへのプロンプト作成
    prompt = f"""
    以下のセグメント情報に基づいて、獲得可能性（獲得率）を推計してください。
    最小値、期待値、最大値を推計し、推計ロジックも説明してください。
    ※参入障壁が高いほど獲得率は低く、参入障壁が低いほど獲得率は高くなります。
    
    セグメントID: {segment_id}
    セグメント情報: {json.dumps(segment_data, ensure_ascii=False)}
    
    レスポンスは以下のJSON形式で返してください:
    {{
      "min": 最小獲得率（0.0～1.0の小数）,
      "expected": 期待獲得率（0.0～1.0の小数）,
      "max": 最大獲得率（0.0～1.0の小数）,
      "logic": "推計ロジックの説明"
    }}
    """
    
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたは市場分析の専門家です。"},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    # レスポンスからJSONを抽出
    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return {
            "min": 0.05,
            "expected": 0.15,
            "max": 0.30,
            "logic": "AIレスポンスの解析に失敗したため、デフォルト値を設定しました。"
        }


@function_tool
async def calculate_total_potential(
    segment_id: str,
    market_size: int,
    acquisition_probability: float
) -> str:
    """セグメントの総市場ポテンシャルを計算します。

    Args:
        segment_id: セグメントID
        market_size: 市場規模（企業数）
        acquisition_probability: 獲得確率

    Returns:
        総市場ポテンシャル計算結果
    """
    # 市場ポテンシャル計算の基本構造を定義
    calculation_result = {
        "segment_id": segment_id,
        "segment_name": "",  # セグメントの特性から生成される
        "total_companies": market_size,
        "acquisition_probability": acquisition_probability,
        "acquirable_companies": 0,  # 市場規模と獲得確率から計算
        "average_evc_per_company": 0,  # セグメントの特性から算出
        "total_potential_value": 0,  # 獲得可能企業数×平均EVC値
        "calculation_formula": "総市場ポテンシャル = 企業数 × 獲得確率 × 平均EVC値",
        "calculation_details": ""
    }
    
    # 約定可能な企業数の計算
    acquirable_companies = int(market_size * acquisition_probability)
    calculation_result["acquirable_companies"] = acquirable_companies
    
    # 実際のセグメント分析から平均EVC値を計算し、総ポテンシャルを算出する
    # ここではOpenAIを使用して計算を行う場合、適切な処理を実装する
    
    return str(calculation_result)


@function_tool
async def create_market_potential_report(
    segments: List[CustomerSegment],
    market_analyses: List[str],
    competitive_analyses: List[str],
    acquisition_probabilities: List[str],
    total_potentials: List[str]
) -> str:
    """市場ポテンシャル分析レポートを作成します。

    Args:
        segments: 顧客セグメントのリスト
        market_analyses: 市場規模分析結果のリスト
        competitive_analyses: 競合状況分析結果のリスト
        acquisition_probabilities: 獲得確率推定結果のリスト
        total_potentials: 総市場ポテンシャル計算結果のリスト

    Returns:
        市場ポテンシャル分析レポート
    """
    # 各分析結果を統合してレポートを作成
    
    # セグメント別の市場ポテンシャルモデルを作成
    market_potentials = []
    
    for i, segment in enumerate(segments):
        segment_id = segment.segment_id
        
        # 対応する分析結果を取得
        try:
            market_analysis = eval(market_analyses[i]) if i < len(market_analyses) else {}
            competitive_analysis = eval(competitive_analyses[i]) if i < len(competitive_analyses) else {}
            acquisition_probability = eval(acquisition_probabilities[i]) if i < len(acquisition_probabilities) else {}
            total_potential = eval(total_potentials[i]) if i < len(total_potentials) else {}
        except Exception as e:
            # データ変換に失敗した場合は空の辞書を使用
            market_analysis = {}
            competitive_analysis = {}
            acquisition_probability = {}
            total_potential = {}
        
        # セグメントの市場ポテンシャルモデルを作成
        potential = MarketPotential(
            segment_id=segment_id,
            segment_name=segment.name,
            total_companies=market_analysis.get("total_companies", 0),
            annual_growth_rate=market_analysis.get("annual_growth_rate", 0.0),
            market_concentration=competitive_analysis.get("market_concentration", ""),
            competitive_intensity=competitive_analysis.get("competitive_intensity", ""),
            entry_barriers=competitive_analysis.get("entry_barriers", ""),
            acquisition_probability=acquisition_probability.get("adjusted_probability", 0.0),
            acquirable_companies=total_potential.get("acquirable_companies", 0),
            total_potential_value=total_potential.get("total_potential_value", 0),
            major_competitors=competitive_analysis.get("major_competitors", [])
        )
        
        market_potentials.append(potential)
    
    # 全体レポートの生成
    from datetime import datetime
    
    report = {
        "report_title": "市場ポテンシャル分析レポート",
        "creation_date": datetime.now().strftime("%Y-%m-%d"),
        "segments": [p.dict() for p in market_potentials],
        "total_market_value": sum(p.total_potential_value for p in market_potentials),
        "total_acquirable_companies": sum(p.acquirable_companies for p in market_potentials),
        "insights": [],
        "recommendations": []
    }
    
    
    return str(report)


# プロンプトの定義
INSTRUCTIONS = """# システムコンテキスト
あなたは顧客セグメンテーションと市場優先度評価フレームワークの一部として、
市場ポテンシャル分析を担当するエージェントです。

## 目的
各セグメントの市場規模を分析し、業界レポート、市場調査、専門家予測から各セグメントの企業数を算出し、
競合状況、市場動向、商品適合性からセグメント別の獲得確率を推定してください。

## アプローチ
1. 各セグメントの市場規模を分析する
2. 各セグメントの競合状況を分析する
3. セグメント別の獲得確率を推定する
4. 総市場ポテンシャルを計算する
5. 市場ポテンシャル分析レポートを作成する
6. 分析結果を構造化された形式で出力する

## 出力形式
分析結果は以下の形式で出力してください：
- セグメント別の市場規模（企業数）
- セグメント別の獲得確率
- セグメント別の総市場ポテンシャル
- 市場ポテンシャル分析レポート
"""

# エージェントの定義
market_potential_agent = Agent(
    name="MarketPotentialAnalysisAgent",
    instructions=INSTRUCTIONS,
    tools=[
        websearch_tool,
        extract_market_data,
        analyze_market_size,
        analyze_competitive_landscape,
        estimate_acquisition_probability,
        calculate_segment_potential,
        create_market_potential_report
    ],
)

# エージェントを取得する関数
def get_market_potential_agent() -> Agent:
    """市場ポテンシャル分析エージェントを取得します。

    Returns:
        設定済みの市場ポテンシャル分析エージェント
    """
    return market_potential_agent
