"""
フォーミュラ設計エージェント

このモジュールでは、比較マトリックスを基に、改良された集約数式 'EVC = R + (Re + Co) - I' に従った、
各セグメント用のEVC計算フォーミュラを設計するエージェントを定義します。
"""

from typing import Dict, Any, List
import json
import logging
# OpenAI Agents SDK
from agents import Agent, function_tool
from tools.evc_tools import design_evc_formula


def extract_parameter_from_characteristics(characteristics, parameter_name, is_enterprise, is_high_value, default=None):
    """
    セグメント特性から特定のパラメータを抽出する関数
    
    Args:
        characteristics: セグメント特性を含む辞書
        parameter_name: 抽出するパラメータ名
        is_enterprise: 大企業かどうか
        is_high_value: 高価値セグメントかどうか
        default: デフォルト値（指定されていない場合はNone）
        
    Returns:
        抽出されたパラメータ値
    """
    # 特性から直接パラメータが指定されている場合はそれを使用
    if characteristics and parameter_name in characteristics:
        return characteristics[parameter_name]
    
    # パラメータ名に基づいて値を計算
    if parameter_name == "annual_revenue":
        if is_enterprise:
            return 1000000000 if is_high_value else 800000000
        else:
            return 200000000 if is_high_value else 50000000
    
    elif parameter_name == "annual_cost":
        if is_enterprise:
            return 500000000 if is_high_value else 400000000
        else:
            return 100000000 if is_high_value else 25000000
    
    elif parameter_name == "revenue_increase_rate":
        if is_high_value:
            return 0.05 if is_enterprise else 0.08
        else:
            return 0.03 if is_enterprise else 0.02
    
    elif parameter_name == "cost_reduction_rate":
        if is_high_value:
            return 0.15 if is_enterprise else 0.12
        else:
            return 0.20 if is_enterprise else 0.10
    
    elif parameter_name == "reference_price":
        return 15000  # すべてのセグメントで同じ
    
    elif parameter_name == "initial_cost":
        if is_enterprise:
            return 500000 if is_high_value else 400000
        else:
            return 200000 if is_high_value else 100000
    
    elif parameter_name == "operation_cost":
        if is_enterprise:
            return 10000 if is_high_value else 8000
        else:
            return 5000 if is_high_value else 3000
    
    elif parameter_name == "implementation_years":
        return 3  # すべてのセグメントで同じ
    
    # 上記以外の場合はデフォルト値を返す
    return default


@function_tool
async def customize_formula_for_segment(
    segment_id: str,
    base_formula: str,
    segment_characteristics: str
) -> str:
    """基本フォーミュラをセグメント特性に合わせてカスタマイズします。

    Args:
        segment_id: セグメントID
        base_formula: 基本フォーミュラ
        segment_characteristics: セグメントの特性

    Returns:
        カスタマイズされたフォーミュラ
    """
    # 実際にセグメント特性に基づいてフォーミュラをカスタマイズする
    
    # base_formulaが文字列の場合、JSONに変換を試みる
    base_formula_dict = {}
    if isinstance(base_formula, str):
        try:
            if base_formula.strip().startswith('{') and base_formula.strip().endswith('}'):
                try:
                    base_formula_dict = json.loads(base_formula)
                except json.JSONDecodeError:
                    # シングルクォートをダブルクォートに変換する
                    fixed_json = base_formula.replace("'", "\"").replace("\n", " ")
                    try:
                        base_formula_dict = json.loads(fixed_json)
                    except:
                        logging.warning(f"フォーミュラの解析に失敗しました: {base_formula[:50]}...")
            else:
                logging.warning(f"フォーミュラがJSON形式ではありません: {base_formula[:50]}...")
        except Exception as e:
            logging.error(f"フォーミュラの処理エラー: {str(e)}")
    
    # セグメント情報から調整係数を決定する
    # セグメントIDの解析を改善
    is_enterprise = False
    is_high_value = False
    
    # s1, s2, s3, s4 形式のIDの場合
    if segment_id.startswith('s') and segment_id[1:].isdigit():
        segment_num = int(segment_id[1:])
        is_enterprise = segment_num <= 2  # s1, s2は大企業
        is_high_value = segment_num % 2 == 1  # s1, s3は高価値
    # 「大企業・高価値」などの日本語の場合
    else:
        if '大企業' in segment_id:
            is_enterprise = True
        if '高価値' in segment_id:
            is_high_value = True
    
    # セグメント特性文字列からパラメータを抽出
    characteristics_dict = {}
    # セグメント特性が文字列で提供されている場合は解析する
    if isinstance(segment_characteristics, str):
        # JSON形式の場合
        try:
            if segment_characteristics.strip().startswith('{') and segment_characteristics.strip().endswith('}'):
                try:
                    characteristics_dict = json.loads(segment_characteristics)
                except json.JSONDecodeError:
                    fixed_json = segment_characteristics.replace("'", "\"").replace("\n", " ")
                    try:
                        characteristics_dict = json.loads(fixed_json)
                    except Exception as e:
                        logging.warning(f"セグメント特性のJSON解析に失敗しました: {str(e)}")
            else:
                # 特性リストを解析（例: "大企業・高価値：豊富な予算、迅速な意思決定、ITリテラシーが高い"）
                parts = segment_characteristics.split("：") if "：" in segment_characteristics else segment_characteristics.split(":")
                
                if len(parts) > 1:
                    character_parts = parts[1].split("、")
                    for part in character_parts:
                        part = part.strip()
                        if "予算" in part:
                            characteristics_dict["budget"] = "high" if "豊富" in part or "高い" in part else "low"
                        if "意思決定" in part:
                            characteristics_dict["decision_making"] = "fast" if "迅速" in part else "slow"
                        if "ITリテラシー" in part:
                            characteristics_dict["it_literacy"] = "high" if "高い" in part else "low"
                # セグメントの特性をリストで提供された場合
                elif isinstance(segment_characteristics, list):
                    for characteristic in segment_characteristics:
                        if "予算" in characteristic:
                            characteristics_dict["budget"] = "high" if "豊富" in characteristic or "高い" in characteristic else "low"
                        if "意思決定" in characteristic:
                            characteristics_dict["decision_making"] = "fast" if "迅速" in characteristic else "slow"
                        if "ITリテラシー" in characteristic:
                            characteristics_dict["it_literacy"] = "high" if "高い" in characteristic else "low"
        except Exception as e:
            logging.error(f"セグメント特性の処理エラー: {str(e)}")
    
    # セグメント特性に基づく調整係数を生成
    adjustments = {
        "R": 1.0,  # 参照価格は原則変更なし
        "Re": 1.0 + (0.2 if is_high_value else -0.2),  # 高価値セグメントは収益向上を重視
        "Co": 1.0 + (0.2 if not is_high_value else -0.1),  # 低価値セグメントはコスト削減を重視
        "I": 1.0 + (0.2 if not is_enterprise else -0.2)  # 中小企業は導入コストへの感度が高い
    }
    
    # 調整の仕組みを説明する文章を生成
    value_type = "高価値" if is_high_value else "低価値"
    company_type = "大企業" if is_enterprise else "中小企業"
    
    if is_high_value and is_enterprise:
        justification = f"{company_type}・{value_type}セグメントは収益向上価値を重視し、導入コストへの感度が低い"
    elif not is_high_value and is_enterprise:
        justification = f"{company_type}・{value_type}セグメントはコスト最適化価値を重視し、収益向上価値への感度が低い"
    elif is_high_value and not is_enterprise:
        justification = f"{company_type}・{value_type}セグメントは収益向上価値を重視するが、導入コストへの感度も高い"
    else:
        justification = f"{company_type}・{value_type}セグメントはコスト削減をある程度重視するが、導入コストへの感度が非常に高い"
    
    # セグメント名を生成 - 価値と障壁に基づいた名前を使用
    from models.models import SegmentType
    
    segment_type = None
    if is_high_value and is_enterprise:
        segment_type = SegmentType.HIGH_VALUE_LOW_BARRIER
        segment_name = "高価値・低障壁"
    elif is_high_value and not is_enterprise:
        segment_type = SegmentType.HIGH_VALUE_HIGH_BARRIER
        segment_name = "高価値・高障壁"
    elif not is_high_value and is_enterprise:
        segment_type = SegmentType.LOW_VALUE_LOW_BARRIER
        segment_name = "低価値・低障壁"
    else:
        segment_type = SegmentType.LOW_VALUE_HIGH_BARRIER
        segment_name = "低価値・高障壁"
    
    # カスタマイズされたフォーミュラ
    standard_formula = "EVC = R + (Re + Co) - I"
    
    # base_formula_dictからコンポーネント情報を取得、存在しない場合はデフォルト値を使用
    components = {}
    try:
        if base_formula_dict and "components" in base_formula_dict:
            components = base_formula_dict["components"]
    except:
        pass
    
    # カスタマイズされたフォーミュラの構築
    customized_formula = {
        "segment_id": segment_id,
        "segment_name": segment_name,
        "segment_type": str(segment_type) if segment_type else None,
        "base_formula": standard_formula,
        "components": {
            "R": {
                "description": components.get("R", {}).get("description", "参照価格"),
                "calculation": components.get("R", {}).get("calculation", "市場平均価格"),
                "weight": components.get("R", {}).get("weight", 1.0) * adjustments["R"]
            },
            "Re": {
                "description": components.get("Re", {}).get("description", "収益向上価値"),
                "calculation": components.get("Re", {}).get("calculation", "売上増加率 × 年間売上 × 導入年数"),
                "weight": components.get("Re", {}).get("weight", 1.2) * adjustments["Re"]
            },
            "Co": {
                "description": components.get("Co", {}).get("description", "コスト最適化価値"),
                "calculation": components.get("Co", {}).get("calculation", "コスト削減率 × 年間コスト × 導入年数"),
                "weight": components.get("Co", {}).get("weight", 1.0) * adjustments["Co"]
            },
            "I": {
                "description": components.get("I", {}).get("description", "導入コスト"),
                "calculation": components.get("I", {}).get("calculation", "初期費用 + 運用コスト × 導入年数"),
                "weight": components.get("I", {}).get("weight", 0.9) * adjustments["I"]
            }
        },
        "segment_specific_parameters": {
            # セグメント特性からパラメータを抽出
            # それぞれのパラメータを実際にセグメントの特性から計算する
            "annual_revenue": extract_parameter_from_characteristics(characteristics_dict, "annual_revenue", is_enterprise, is_high_value),
            "annual_cost": extract_parameter_from_characteristics(characteristics_dict, "annual_cost", is_enterprise, is_high_value),
            "implementation_years": extract_parameter_from_characteristics(characteristics_dict, "implementation_years", is_enterprise, is_high_value, default=3),
            "revenue_increase_rate": extract_parameter_from_characteristics(characteristics_dict, "revenue_increase_rate", is_enterprise, is_high_value),
            "cost_reduction_rate": extract_parameter_from_characteristics(characteristics_dict, "cost_reduction_rate", is_enterprise, is_high_value),
            "reference_price": extract_parameter_from_characteristics(characteristics_dict, "reference_price", is_enterprise, is_high_value),
            "initial_cost": extract_parameter_from_characteristics(characteristics_dict, "initial_cost", is_enterprise, is_high_value),
            "operation_cost": extract_parameter_from_characteristics(characteristics_dict, "operation_cost", is_enterprise, is_high_value)
        },
        "adjustment_justification": justification
    }
    
    return str(customized_formula)


@function_tool
async def validate_formula(formula: str) -> str:
    """フォーミュラの妥当性を検証します。

    Args:
        formula: 検証するフォーミュラ

    Returns:
        検証結果
    """
    import json
    import logging
    
    # 文字列パラメータをパースする
    if isinstance(formula, str):
        try:
            # JSONとして解析を試みる
            if formula.strip().startswith('{') and formula.strip().endswith('}'): 
                try:
                    formula_dict = json.loads(formula)
                except json.JSONDecodeError:
                    # シングルクォートをダブルクォートに変換するなどの修正を試みる
                    try:
                        fixed_json = formula.replace("'", "\"").replace("\n", " ")
                        formula_dict = json.loads(fixed_json)
                    except Exception as e:
                        logging.error(f"フォーミュラのパースに失敗しました: {str(e)}")
                        formula_dict = {}
            # すでに数式が定義されている単純なケース
            elif "=" in formula:
                # シンプルな数式としてのみ処理
                formula_dict = {
                    "base_formula": formula.strip(),
                    "components": {
                        "R": {"weight": 1.0},
                        "Re": {"weight": 1.0},
                        "Co": {"weight": 1.0},
                        "I": {"weight": 1.0}
                    },
                    "segment_specific_parameters": {}
                }
            else:
                logging.warning(f"フォーミュラのフォーマットが認識できません: {formula}")
                formula_dict = {}
        except Exception as e:
            logging.error(f"フォーミュラのパース中にエラーが発生しました: {str(e)}")
            formula_dict = {}
    else:
        # 既に辞書であれば、そのまま使用
        formula_dict = formula
    
    validation_result = {
        "is_valid": True,
        "issues": [],
        "recommendations": []
    }
    
    # 基本的な検証
    if "base_formula" not in formula_dict:
        validation_result["is_valid"] = False
        validation_result["issues"].append("基本フォーミュラが定義されていません")
    
    if "components" not in formula_dict:
        validation_result["is_valid"] = False
        validation_result["issues"].append("フォーミュラのコンポーネントが定義されていません")
    
    # コンポーネントの検証
    components = formula_dict.get("components", {})
    required_components = ["R", "Re", "Co", "I"]
    
    for component in required_components:
        if component not in components:
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"必須コンポーネント '{component}' が定義されていません")
        else:
            component_data = components[component]
            if "weight" not in component_data:
                validation_result["is_valid"] = False
                validation_result["issues"].append(f"コンポーネント '{component}' の重みが定義されていません")
            elif component_data["weight"] <= 0:
                validation_result["is_valid"] = False
                validation_result["issues"].append(f"コンポーネント '{component}' の重みは正の値である必要があります")
    
    # セグメント固有パラメータの検証
    segment_params = formula_dict.get("segment_specific_parameters", {})
    required_params = [
        "annual_revenue", "annual_cost", "implementation_years",
        "revenue_increase_rate", "cost_reduction_rate", "reference_price",
        "initial_cost", "operation_cost"
    ]
    
    for param in required_params:
        if param not in segment_params:
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"必須パラメータ '{param}' が定義されていません")
    
    # 推奨事項
    if formula_dict.get("segment_id") == "s4":  # 中小企業・低価値
        if components.get("I", {}).get("weight", 1.0) < 1.2:
            validation_result["recommendations"].append(
                "中小企業・低価値セグメントでは、導入コストの重みをより高く設定することを検討してください"
            )
    
    if formula_dict.get("segment_id") == "s1":  # 大企業・高価値
        if components.get("Re", {}).get("weight", 1.0) < 1.1:
            validation_result["recommendations"].append(
                "大企業・高価値セグメントでは、収益向上価値の重みをより高く設定することを検討してください"
            )
    
    return str(validation_result)


@function_tool
async def document_formula_design(
    base_formula: str,
    segment_formulas: List[str],
    validation_results: List[str]
) -> str:
    """フォーミュラ設計プロセスを文書化します。

    Args:
        base_formula: 基本フォーミュラ
        segment_formulas: セグメント別フォーミュラのリスト
        validation_results: 検証結果のリスト

    Returns:
        文書化されたフォーミュラ設計
    """
    # 実際の実装では、設計プロセスを詳細に文書化します
    # この例では、モックデータを返します
    
    # 型チェックして適切に処理
    formula_text = "EVC = R + (Re + Co) - I"
    components = {}
    
    try:
        # 文字列が辞書形式かチェック
        if isinstance(base_formula, str):
            if base_formula.strip().startswith('{'):
                import json
                formula_dict = json.loads(base_formula)
                formula_text = formula_dict.get("base_formula", formula_text)
                components = formula_dict.get("components", {})
            else:
                formula_text = base_formula
        else:
            # すでに辞書型の場合（これは起こりえないが念のため）
            formula_text = str(base_formula)
    except Exception as e:
        # パースに失敗した場合はそのまま文字列として扱う
        formula_text = str(base_formula)
        
    documentation = {
        "design_process": {
            "base_formula": {
                "formula": formula_text,
                "components": components,
                "justification": "標準的なEVC計算式を採用し、各コンポーネントの重み付けを調整することで、セグメント特性を反映"
            },
            "segment_customization": {
                "approach": "各セグメントの特性（価値創出ポテンシャルと実現容易性）に基づいて、コンポーネントの重み付けを調整",
                "key_considerations": [
                    "収益向上価値とコスト最適化価値のバランス",
                    "導入コストへの感度",
                    "セグメント固有のパラメータ値"
                ]
            },
            "validation": {
                "approach": "各フォーミュラの論理的整合性と現実的な結果を検証",
                "issues_addressed": [issue for result in validation_results for issue in result.get("issues", []) if issue],
                "recommendations_applied": [rec for result in validation_results for rec in result.get("recommendations", []) if rec]
            }
        },
        "segment_formulas": {
            formula["segment_id"]: {
                "name": formula["segment_name"],
                "formula": formula["base_formula"],
                "component_weights": {
                    "R": formula["components"]["R"]["weight"],
                    "Re": formula["components"]["Re"]["weight"],
                    "Co": formula["components"]["Co"]["weight"],
                    "I": formula["components"]["I"]["weight"]
                },
                "justification": formula.get("adjustment_justification", "")
            } for formula in segment_formulas
        },
        "usage_guidelines": {
            "parameter_selection": "各セグメントの実際の企業データに基づいてパラメータを設定",
            "sensitivity_analysis": "主要パラメータ（収益増加率、コスト削減率、導入年数）の変動による結果への影響を分析",
            "interpretation": "EVCは金銭的価値を表し、正の値は投資価値があることを示す。値が大きいほど投資価値が高い。"
        }
    }
    
    return str(documentation)


# プロンプトの定義
INSTRUCTIONS = """# システムコンテキスト
あなたは顧客セグメンテーションと市場優先度評価フレームワークの一部として、
フォーミュラ設計を担当するエージェントです。

## 目的
比較マトリックスを基に、改良された集約数式 'EVC = R + (Re + Co) - I' に従った、
各セグメント用のEVC計算フォーミュラを設計してください。

## アプローチ
1. 比較マトリックスを分析し、基本的なEVC計算フォーミュラを設計する
2. 各価値要因の重み・調整値を決定し、その根拠を明確にする
3. セグメント特性に基づいて、セグメント別のフォーミュラをカスタマイズする
4. フォーミュラの妥当性を検証し、必要に応じて調整する
5. フォーミュラ設計プロセスを文書化する
6. 設計結果を構造化された形式で出力する

## 出力形式
設計結果は以下の形式で出力してください：
- 基本フォーミュラ（EVC = R + (Re + Co) - I）
- 各コンポーネントの説明と計算方法
- セグメント別の調整係数とその根拠
- セグメント固有のパラメータ推定値
- フォーミュラ設計プロセスの文書化
"""

# エージェントの定義
formula_design_agent = Agent(
    name="FormulaDesignAgent",
    instructions=INSTRUCTIONS,
    tools=[
        design_evc_formula,
        customize_formula_for_segment,
        validate_formula,
        document_formula_design
    ],
)

# エージェントを取得する関数
def get_formula_design_agent() -> Agent:
    """フォーミュラ設計エージェントを取得します。

    Returns:
        設定済みのフォーミュラ設計エージェント
    """
    return formula_design_agent
