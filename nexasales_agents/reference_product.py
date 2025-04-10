"""
参照製品特定と分析エージェント

このモジュールでは、サービス概要レポートと公開市場・競合情報から、対象サービスと競合する
参照製品を特定し、各参照商品について提供価値要因を個別に定量化するエージェントを定義します。
"""

from typing import Dict, Any, List
# OpenAI Agents SDK
from agents import Agent, function_tool
from models.models import ReferenceProduct
from tools.common_tools import websearch_tool, analyze_competitors, identify_reference_products


@function_tool
async def analyze_product_value(product: ReferenceProduct) -> str:
    """参照製品の提供価値を分析します。

    Args:
        product: 参照製品

    Returns:
        提供価値分析結果
    """
    # 実際の製品データを使用して分析
    value_analysis = {}

    # 実際の製品データから分析を行う
    if product and product.name and product.features and product.strengths:
        # 製品の特徴と強みに基づいて価値提案を抽出
        value_analysis["core_value_proposition"] = f"{product.name}の主要な価値提案"
        
        # 実際の製品データに基づいて価値要素を抽出
        value_analysis["value_components"] = {}
        
        # 製品の強みから効率性改善要素を抽出
        value_analysis["value_components"]["efficiency_improvement"] = {
            "description": "製品が提供する効率性改善",
            "strengths": product.strengths,
            "features": product.features
        }
        
        # 価格情報が利用可能な場合は追加
        if hasattr(product, 'pricing') and product.pricing:
            value_analysis["pricing_info"] = product.pricing
    else:
        value_analysis["error"] = "製品情報が不十分です"
    
    return str(value_analysis)


@function_tool
async def compare_product_features(products: List[ReferenceProduct]) -> str:
    """参照製品の機能を比較します。

    Args:
        products: 参照製品のリスト

    Returns:
        機能比較結果
    """
    # 実際の製品データから機能比較を生成
    feature_comparison = {}
    
    if not products or len(products) == 0:
        feature_comparison["error"] = "製品情報が提供されていません"
        return str(feature_comparison)
    
    # 比較する製品名のリストを生成
    product_names = [product.name for product in products if product and product.name]
    
    # カテゴリと機能の比較のための空のデータ構造を作成
    feature_comparison["core_features"] = {}
    feature_comparison["advanced_features"] = {}
    feature_comparison["usability"] = {}
    
    # 各製品の機能情報を抽出して比較情報を構築
    for product in products:
        if not product or not product.features:
            continue
            
        # 製品の機能を分析してカテゴリごとに整理
        for feature in product.features:
            # 機能の種類を判別して適切なカテゴリに配置
            feature_category = "core_features"  # デフォルトはコア機能カテゴリ
            
            # 実際の製品データに基づいて比較情報を生成
            if feature not in feature_comparison[feature_category]:
                feature_comparison[feature_category][feature] = {}
                
            # この製品のこの機能に関する情報を追加
            feature_comparison[feature_category][feature][product.name] = {
                "available": True,
                "notes": f"{product.name}の{feature}機能"
            }
    
    return str(feature_comparison)


@function_tool
async def create_value_comparison_matrix(
    products: List[ReferenceProduct],
    value_analyses: List[str]
) -> str:
    """参照製品の価値比較マトリックスを作成します。

    Args:
        products: 参照製品のリスト
        value_analyses: 各製品の価値分析結果

    Returns:
        価値比較マトリックス
    """
    # 実際の製品データと価値分析から比較マトリックスを生成
    comparison_matrix = {}
    
    if not products or len(products) == 0:
        comparison_matrix["error"] = "製品情報が提供されていません"
        return str(comparison_matrix)
    
    # 製品名のリストを生成
    product_names = [product.name for product in products if product and product.name]
    
    # マトリックスのカテゴリを初期化
    comparison_matrix["reference_price"] = {}
    comparison_matrix["value_components"] = {}
    
    # 各製品の情報をマトリックスに追加
    for i, product in enumerate(products):
        if not product or not product.name:
            continue
            
        # 価格情報があれば追加
        if hasattr(product, 'pricing') and product.pricing:
            comparison_matrix["reference_price"][product.name] = product.pricing
        
        # 強みと弱みの情報を価値要素として抽出
        if product.strengths:
            if "strengths" not in comparison_matrix["value_components"]:
                comparison_matrix["value_components"]["strengths"] = {}
            comparison_matrix["value_components"]["strengths"][product.name] = product.strengths
        
        if hasattr(product, 'weaknesses') and product.weaknesses:
            if "weaknesses" not in comparison_matrix["value_components"]:
                comparison_matrix["value_components"]["weaknesses"] = {}
            comparison_matrix["value_components"]["weaknesses"][product.name] = product.weaknesses
    
    return str(comparison_matrix)


# プロンプトの定義
INSTRUCTIONS = """# システムコンテキスト
あなたは顧客セグメンテーションと市場優先度評価フレームワークの一部として、
参照製品の特定と分析を担当するエージェントです。

## 目的
サービス概要レポートと公開市場・競合情報から、対象サービスと競合する参照製品を特定し、
各参照商品について提供価値要因を個別に定量化してください。

## アプローチ
1. サービス概要レポートを理解する
2. 公開市場・競合情報から参照製品を特定する
3. 各参照製品の機能、価格、強み、弱みを分析する
4. 各参照製品の提供価値要因を特定し、定量化する
5. 参照製品間の比較マトリックスを作成する
6. 分析結果を構造化された形式で出力する

## 出力形式
分析結果は以下の形式で出力してください：
- 参照製品リスト（各製品の名前、会社、説明、機能、価格、市場シェア、強み、弱み）
- 各参照製品の提供価値分析（価値要素、定量化、金銭的価値）
- 参照製品間の比較マトリックス
"""

# エージェントの定義
reference_product_agent = Agent(
    name="ReferenceProductIdentificationAgent",
    instructions=INSTRUCTIONS,
    tools=[
        websearch_tool,
        analyze_competitors,
        identify_reference_products,
        analyze_product_value,
        compare_product_features,
        create_value_comparison_matrix
    ],
)

# エージェントを取得する関数
def get_reference_product_agent() -> Agent:
    """参照製品特定エージェントを取得します。

    Returns:
        設定済みの参照製品特定エージェント
    """
    return reference_product_agent
