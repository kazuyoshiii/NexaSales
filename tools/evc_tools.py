"""
NexaSales顧客セグメンテーションシステムのEVC計算ツール関数

このモジュールでは、EVC（経済的価値貢献）計算に関連するツール関数を定義します。
各種価値要素の計算、フォーミュラ設計、セグメント別の計算などの機能を提供します。
"""

from typing import Any, Dict, List, Optional
# OpenAI Agents SDK
from agents import function_tool
from models.models import EVCComponents, EVCResult, ValueComponent


@function_tool
async def design_evc_formula(comparison_matrix: str) -> str:
    """比較マトリックスに基づいてEVC計算フォーミュラを設計します。

    Args:
        comparison_matrix: 参照商品の比較マトリックス

    Returns:
        設計されたEVC計算フォーミュラ
    """
    # 実際の実装では、比較マトリックスを分析してフォーミュラを設計します
    # この例では、モックデータを返します
    return """{
        "base_formula": "EVC = R + (Re + Co) - I",
        "components": {
            "R": {
                "description": "参照価格",
                "calculation": "市場平均価格",
                "weight": 1.0
            },
            "Re": {
                "description": "収益向上価値",
                "calculation": "売上増加率 × 年間売上 × 導入年数",
                "weight": 1.2
            },
            "Co": {
                "description": "コスト最適化価値",
                "calculation": "コスト削減率 × 年間コスト × 導入年数",
                "weight": 1.0
            },
            "I": {
                "description": "導入コスト",
                "calculation": "初期費用 + 運用コスト × 導入年数",
                "weight": 0.9
            }
        },
        "segment_adjustments": {
            "s1": {"Re": 1.2, "Co": 1.0, "I": 0.8},
            "s2": {"Re": 0.8, "Co": 1.2, "I": 0.9},
            "s3": {"Re": 1.3, "Co": 0.9, "I": 1.2},
            "s4": {"Re": 0.7, "Co": 1.1, "I": 1.3}
        },
        "justification": "各セグメントの特性に基づいて重み付けを調整しました。高価値セグメントは収益向上価値を重視し、低価値セグメントはコスト最適化価値を重視します。"
    }"""


@function_tool
async def calculate_evc(segment_id: str, formula: str, parameters: str) -> EVCResult:
    """設計されたフォーミュラに基づいて特定セグメントのEVCを計算します。

    Args:
        segment_id: セグメントID
        formula: EVC計算フォーミュラ
        parameters: 計算に使用するパラメータ

    Returns:
        EVC計算結果
    """
    import logging
    import json
    import re
    
    # パラメータを辞書に変換する
    params_dict = {}
    if isinstance(parameters, dict):
        params_dict = parameters
    elif isinstance(parameters, str):
        try:
            # JSON形式の場合は解析
            if parameters.strip().startswith('{') and parameters.strip().endswith('}'):
                try:
                    params_dict = json.loads(parameters)
                except json.JSONDecodeError:
                    # シングルクォートをダブルクォートに変換するなどの修正を試みる
                    try:
                        fixed_json = parameters.replace("'", "\"").replace("\n", " ")
                        params_dict = json.loads(fixed_json)
                    except json.JSONDecodeError:
                        logging.warning(f"パラメータのJSON解析に失敗しました: {parameters[:50]}...")
            else:
                # キー値形式の場合は解析 (例: "売上増加率: 0.10, 年間売上: 100000000, ...")
                pairs = parameters.split(',')
                for pair in pairs:
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 値を適切な型に変換
                        try:
                            # 数値の場合
                            if re.match(r'^[\d.]+$', value):
                                if '.' in value:
                                    value = float(value)
                                else:
                                    value = int(value)
                        except ValueError:
                            pass  # 変換に失敗した場合は文字列のまま
                        
                        params_dict[key] = value
        except Exception as e:
            logging.error(f"パラメータの解析中にエラーが発生しました: {str(e)}")
    
    # セグメント特定のパラメータを設定
    # ここから下はパラメータが辞書型として処理される
    
    # 基本パラメータの動的取得
    # 参照価格はパラメータから動的に取得
    reference_price = params_dict.get("reference_price", 0)
    
    # セグメントに基づく調整係数をパラメータから動的に取得
    segment_adjustments = params_dict.get("segment_adjustments", {})
    
    # セグメント調整を適用、存在しない場合はデフォルト値を使用
    default_adjustments = {"Re": 1.0, "Co": 1.0, "I": 1.0}
    adjustments = segment_adjustments.get(segment_id, default_adjustments)
    
    # 収益向上価値の動的計算を行う
    implementation_years = params_dict.get("implementation_years")
    annual_revenue = params_dict.get("annual_revenue")
    
    # 収益向上価値の計算式を動的に決定
    service_type = params_dict.get("service_type")
    industry = params_dict.get("industry")
    
    # 完全に動的な計算構造を作成
    revenue_components = {}
    revenue_formulas = {}
    revenue_parameters = {}
    
    # サービスタイプごとの変数名を取得
    component_config = params_dict.get("revenue_components", {})
    
    # 新規収益（Rn）の動的パラメータ設定
    if "new_revenue" in component_config:
        config = component_config["new_revenue"]
        formula = config.get("formula")
        revenue_formulas["new_revenue"] = formula
        
        # 必要なパラメータを取得
        param_values = {}
        for param in config.get("parameters", []):
            param_values[param] = params_dict.get(param)
        revenue_parameters["new_revenue"] = param_values
        
        # 計算ロジックを動的に適用
        calculation_function = config.get("calculation_function")
        if calculation_function == "standard":
            if all(k in param_values for k in ["new_customers", "average_customer_value", "new_products", "product_revenue"]):
                revenue_components["new_revenue"] = (
                    param_values["new_customers"] * param_values["average_customer_value"] + 
                    param_values["new_products"] * param_values["product_revenue"]
                ) * adjustments["Re"]
        elif calculation_function == "saas":
            if all(k in param_values for k in ["new_customers", "average_arpu", "expansion_revenue"]):
                revenue_components["new_revenue"] = (
                    param_values["new_customers"] * param_values["average_arpu"] + 
                    param_values["expansion_revenue"]
                ) * adjustments["Re"]
        elif calculation_function == "manufacturing":
            if all(k in param_values for k in ["new_clients", "units_per_client", "unit_price"]):
                revenue_components["new_revenue"] = (
                    param_values["new_clients"] * param_values["units_per_client"] * 
                    param_values["unit_price"]
                ) * adjustments["Re"]
        elif calculation_function == "custom":
            # カスタム計算の場合、直接計算結果を受け取る
            if "calculated_value" in param_values:
                revenue_components["new_revenue"] = param_values["calculated_value"] * adjustments["Re"]
    
    # 既存顧客維持による収益（Rr）の動的計算
    if "retention_revenue" in component_config:
        config = component_config["retention_revenue"]
        formula = config.get("formula")
        revenue_formulas["retention_revenue"] = formula
        
        # 必要なパラメータを取得
        param_values = {}
        for param in config.get("parameters", []):
            param_values[param] = params_dict.get(param)
        revenue_parameters["retention_revenue"] = param_values
        
        # 計算ロジックを動的に適用
        calculation_function = config.get("calculation_function")
        if calculation_function == "standard":
            if all(k in param_values for k in ["retained_customers", "customer_lifetime_value"]):
                revenue_components["retention_revenue"] = (
                    param_values["retained_customers"] * param_values["customer_lifetime_value"]
                ) * adjustments["Re"]
        elif calculation_function == "subscription":
            if all(k in param_values for k in ["churn_reduction", "current_customers", "annual_contract_value"]):
                revenue_components["retention_revenue"] = (
                    param_values["churn_reduction"] * param_values["current_customers"] * 
                    param_values["annual_contract_value"]
                ) * adjustments["Re"]
        elif calculation_function == "custom":
            if "calculated_value" in param_values:
                revenue_components["retention_revenue"] = param_values["calculated_value"] * adjustments["Re"]
    
    # 価格最適化による収益（Rp）の動的計算
    if "pricing_revenue" in component_config:
        config = component_config["pricing_revenue"]
        formula = config.get("formula")
        revenue_formulas["pricing_revenue"] = formula
        
        # 必要なパラメータを取得
        param_values = {}
        for param in config.get("parameters", []):
            param_values[param] = params_dict.get(param)
        revenue_parameters["pricing_revenue"] = param_values
        
        # 計算ロジックを動的に適用
        calculation_function = config.get("calculation_function")
        if calculation_function == "standard":
            if all(k in param_values for k in ["price_increase", "customer_base", "revenue_per_customer"]):
                revenue_components["pricing_revenue"] = (
                    param_values["price_increase"] * param_values["customer_base"] * 
                    param_values["revenue_per_customer"]
                ) * adjustments["Re"]
        elif calculation_function == "premium":
            if all(k in param_values for k in ["price_premium", "target_segment_size", "revenue_per_customer"]):
                revenue_components["pricing_revenue"] = (
                    param_values["price_premium"] * param_values["target_segment_size"] * 
                    param_values["revenue_per_customer"]
                ) * adjustments["Re"]
        elif calculation_function == "custom":
            if "calculated_value" in param_values:
                revenue_components["pricing_revenue"] = param_values["calculated_value"] * adjustments["Re"]
    
    # 取引頻度向上による収益（Rt）の動的計算
    if "transaction_revenue" in component_config:
        config = component_config["transaction_revenue"]
        formula = config.get("formula")
        revenue_formulas["transaction_revenue"] = formula
        
        # 必要なパラメータを取得
        param_values = {}
        for param in config.get("parameters", []):
            param_values[param] = params_dict.get(param)
        revenue_parameters["transaction_revenue"] = param_values
        
        # 計算ロジックを動的に適用
        calculation_function = config.get("calculation_function")
        if calculation_function == "standard":
            if all(k in param_values for k in ["transaction_increase", "customer_base", "average_transaction_value"]):
                revenue_components["transaction_revenue"] = (
                    param_values["transaction_increase"] * param_values["customer_base"] * 
                    param_values["average_transaction_value"]
                ) * adjustments["Re"]
        elif calculation_function == "custom":
            if "calculated_value" in param_values:
                revenue_components["transaction_revenue"] = param_values["calculated_value"] * adjustments["Re"]
    
    # カスタムコンポーネントを動的に追加
    custom_components = component_config.get("custom_components", [])
    for component_name in custom_components:
        if component_name in parameters:
            config = parameters[component_name]
            formula = config.get("formula")
            revenue_formulas[component_name] = formula
            
            # カスタムコンポーネントのパラメータを取得
            param_values = {}
            for param in config.get("parameters", []):
                param_values[param] = params_dict.get(param)
            revenue_parameters[component_name] = param_values
            
            # 計算値を取得
            if "calculated_value" in config:
                revenue_components[component_name] = config["calculated_value"] * adjustments["Re"]
    
    # 収益向上価値の総額計算
    revenue_enhancement_value = sum(revenue_components.values()) if revenue_components else 0
    
    # コスト最適化価値の動的計算を行う
    annual_cost = params_dict.get("annual_cost")
    
    # 完全に動的なコスト計算構造を作成
    cost_components = {}
    cost_formulas = {}
    cost_parameters = {}
    
    # サービスタイプごとのコストコンフィグを取得
    component_config = params_dict.get("cost_components", {})
    
    # 直接コスト削減（Cd）の動的パラメータ設定
    if "direct_cost_reduction" in component_config:
        config = component_config["direct_cost_reduction"]
        formula = config.get("formula")
        cost_formulas["direct_cost_reduction"] = formula
        
        # 必要なパラメータを取得
        param_values = {}
        for param in config.get("parameters", []):
            param_values[param] = params_dict.get(param)
        cost_parameters["direct_cost_reduction"] = param_values
        
        # 計算ロジックを動的に適用
        calculation_function = config.get("calculation_function")
        if calculation_function == "standard":
            if all(k in param_values for k in ["manual_hours", "automated_hours", "hourly_rate", "resource_savings"]):
                cost_components["direct_cost_reduction"] = (
                    (param_values["manual_hours"] - param_values["automated_hours"]) * 
                    param_values["hourly_rate"] + param_values["resource_savings"]
                ) * adjustments["Co"]
        elif calculation_function == "cloud_migration":
            if all(k in param_values for k in ["infrastructure_cost_current", "infrastructure_cost_cloud", "maintenance_reduction"]):
                cost_components["direct_cost_reduction"] = (
                    (param_values["infrastructure_cost_current"] - param_values["infrastructure_cost_cloud"]) + 
                    param_values["maintenance_reduction"]
                ) * adjustments["Co"]
        elif calculation_function == "custom":
            if "calculated_value" in param_values:
                cost_components["direct_cost_reduction"] = param_values["calculated_value"] * adjustments["Co"]
    
    # 品質関連コスト削減（Cq）の動的計算
    if "quality_cost_reduction" in component_config:
        config = component_config["quality_cost_reduction"]
        formula = config.get("formula")
        cost_formulas["quality_cost_reduction"] = formula
        
        # 必要なパラメータを取得
        param_values = {}
        for param in config.get("parameters", []):
            param_values[param] = params_dict.get(param)
        cost_parameters["quality_cost_reduction"] = param_values
        
        # 計算ロジックを動的に適用
        calculation_function = config.get("calculation_function")
        if calculation_function == "standard":
            if all(k in param_values for k in ["defect_reduction", "defect_cost", "complaint_reduction", "complaint_cost"]):
                cost_components["quality_cost_reduction"] = (
                    param_values["defect_reduction"] * param_values["defect_cost"] + 
                    param_values["complaint_reduction"] * param_values["complaint_cost"]
                ) * adjustments["Co"]
        elif calculation_function == "six_sigma":
            if all(k in param_values for k in ["sigma_improvement", "defect_rate_reduction", "quality_cost_per_defect", "production_volume"]):
                cost_components["quality_cost_reduction"] = (
                    param_values["defect_rate_reduction"] * param_values["quality_cost_per_defect"] * 
                    param_values["production_volume"]
                ) * adjustments["Co"]
        elif calculation_function == "custom":
            if "calculated_value" in param_values:
                cost_components["quality_cost_reduction"] = param_values["calculated_value"] * adjustments["Co"]
    
    # リスク関連コスト削減（Cr）の動的計算
    if "risk_cost_reduction" in component_config:
        config = component_config["risk_cost_reduction"]
        formula = config.get("formula")
        cost_formulas["risk_cost_reduction"] = formula
        
        # 必要なパラメータを取得
        param_values = {}
        for param in config.get("parameters", []):
            param_values[param] = params_dict.get(param)
        cost_parameters["risk_cost_reduction"] = param_values
        
        # 計算ロジックを動的に適用
        calculation_function = config.get("calculation_function")
        if calculation_function == "standard":
            if all(k in param_values for k in ["risk_reduction_factor", "risk_exposure_value"]):
                cost_components["risk_cost_reduction"] = (
                    param_values["risk_reduction_factor"] * param_values["risk_exposure_value"]
                ) * adjustments["Co"]
        elif calculation_function == "compliance":
            if all(k in param_values for k in ["compliance_penalty_reduction", "incident_probability_reduction", "average_incident_cost"]):
                cost_components["risk_cost_reduction"] = (
                    param_values["compliance_penalty_reduction"] + 
                    param_values["incident_probability_reduction"] * param_values["average_incident_cost"]
                ) * adjustments["Co"]
        elif calculation_function == "custom":
            if "calculated_value" in param_values:
                cost_components["risk_cost_reduction"] = param_values["calculated_value"] * adjustments["Co"]
    
    # 時間関連コスト削減（Ct）の動的計算
    if "time_cost_reduction" in component_config:
        config = component_config["time_cost_reduction"]
        formula = config.get("formula")
        cost_formulas["time_cost_reduction"] = formula
        
        # 必要なパラメータを取得
        param_values = {}
        for param in config.get("parameters", []):
            param_values[param] = params_dict.get(param)
        cost_parameters["time_cost_reduction"] = param_values
        
        # 計算ロジックを動的に適用
        calculation_function = config.get("calculation_function")
        if calculation_function == "standard":
            if all(k in param_values for k in ["decision_time_savings", "opportunity_cost_rate"]):
                cost_components["time_cost_reduction"] = (
                    param_values["decision_time_savings"] * param_values["opportunity_cost_rate"]
                ) * adjustments["Co"]
        elif calculation_function == "process_improvement":
            if all(k in param_values for k in ["process_time_reduction", "process_frequency", "employee_cost_per_hour"]):
                cost_components["time_cost_reduction"] = (
                    param_values["process_time_reduction"] * param_values["process_frequency"] * 
                    param_values["employee_cost_per_hour"] / 60
                ) * adjustments["Co"]
        elif calculation_function == "custom":
            if "calculated_value" in param_values:
                cost_components["time_cost_reduction"] = param_values["calculated_value"] * adjustments["Co"]
    
    # カスタムコストコンポーネントを動的に追加
    custom_components = component_config.get("custom_components", [])
    for component_name in custom_components:
        if component_name in parameters:
            config = parameters[component_name]
            formula = config.get("formula")
            cost_formulas[component_name] = formula
            
            # カスタムコンポーネントのパラメータを取得
            param_values = {}
            for param in config.get("parameters", []):
                param_values[param] = params_dict.get(param)
            cost_parameters[component_name] = param_values
            
            # 計算値を取得
            if "calculated_value" in config:
                cost_components[component_name] = config["calculated_value"] * adjustments["Co"]
    
    # コスト最適化価値の総額計算
    cost_optimization_value = sum(cost_components.values()) if cost_components else 0
    
    # 導入コストの動的計算
    # 導入コストコンポーネントの動的設定
    implementation_cost_components = {}
    implementation_cost_formulas = {}
    implementation_cost_parameters = {}
    
    # 初期コストと運用コストをパラメータから取得
    initial_cost = params_dict.get("initial_cost", 0)
    recurring_cost = params_dict.get("recurring_cost", 0)
    
    # 計算式を記録
    implementation_cost_formula = "I = initial_cost + recurring_cost × implementation_years"
    implementation_cost_formulas["implementation_cost"] = implementation_cost_formula
    
    # 導入コストの計算
    implementation_cost_value = (initial_cost + recurring_cost * implementation_years) * adjustments["I"]
    
    # 導入コストコンポーネントの情報を保存
    implementation_cost_components["implementation_cost"] = implementation_cost_value
    implementation_cost_parameters["implementation_cost"] = {
        "initial_cost": initial_cost,
        "recurring_cost": recurring_cost,
        "implementation_years": implementation_years
    }
    
    # EVC計算
    evc_value = reference_price + (revenue_enhancement_value + cost_optimization_value) - implementation_cost_value
    
    # 結果の構築
    # 動的に生成された収益向上価値のコンポーネントを準備
    revenue_enhancement_components = {}
    
    # 各コンポーネントの詳細な計算情報を追加
    for component_name, value in revenue_components.items():
        component_info = {
            "value": value,
            "formula": revenue_formulas.get(component_name, ""),
            "parameters": revenue_parameters.get(component_name, {})
        }
        revenue_enhancement_components[component_name] = component_info
    
    # 収益向上価値のオブジェクトを生成
    revenue_enhancement = ValueComponent(
        name="収益向上価値",
        description="サービス導入による売上向上効果",
        formula="Re = " + " + ".join([k for k in revenue_components.keys()]),
        value=revenue_enhancement_value,
        calculation_details={
            "formula": "Re = " + " + ".join([k for k in revenue_components.keys()]),
            "total_value": revenue_enhancement_value,
            "components": revenue_enhancement_components,
            "adjustment": adjustments["Re"]
        }
    )
    
    # 動的に生成されたコスト最適化価値のコンポーネントを準備
    cost_optimization_components = {}
    
    # 各コンポーネントの詳細な計算情報を追加
    for component_name, value in cost_components.items():
        component_info = {
            "value": value,
            "formula": cost_formulas.get(component_name, ""),
            "parameters": cost_parameters.get(component_name, {})
        }
        cost_optimization_components[component_name] = component_info
    
    # コスト最適化価値のオブジェクトを生成
    cost_optimization = ValueComponent(
        name="コスト最適化価値",
        description="サービス導入によるコスト削減効果",
        formula="Co = " + " + ".join([k for k in cost_components.keys()]),
        value=cost_optimization_value,
        calculation_details={
            "formula": "Co = " + " + ".join([k for k in cost_components.keys()]),
            "total_value": cost_optimization_value,
            "components": cost_optimization_components,
            "adjustment": adjustments["Co"]
        }
    )
    
    # 導入コストオブジェクトの生成
    implementation_cost_obj = ValueComponent(
        name="導入コスト",
        description="サービス導入に必要なコスト",
        formula=implementation_cost_formula,
        value=implementation_cost_value,
        calculation_details={
            "formula": implementation_cost_formula,
            "total_value": implementation_cost_value,
            "components": {
                "initial_cost": initial_cost,
                "recurring_cost": recurring_cost * implementation_years
            },
            "adjustment": adjustments["I"]
        }
    )
    
    components = EVCComponents(
        reference_price=reference_price,
        revenue_enhancement=revenue_enhancement,
        cost_optimization=cost_optimization,
        implementation_cost=implementation_cost_value
    )
    
    # セグメント名のマッピング
    segment_names = {
        "s1": "大企業・高価値",
        "s2": "大企業・低価値",
        "s3": "中小企業・高価値",
        "s4": "中小企業・低価値"
    }
    
    return EVCResult(
        segment_id=segment_id,
        segment_name=segment_names.get(segment_id, f"セグメント {segment_id}"),
        evc_value=evc_value,
        components=components,
        calculation_details={
            "formula": "EVC = R + (Re + Co) - I",
            "evc_value": evc_value,
            "reference_price": reference_price,
            "revenue_enhancement_value": revenue_enhancement_value,
            "cost_optimization_value": cost_optimization_value,
            "implementation_cost": implementation_cost_value
        }
    )


# 内部実装（非同期）
async def _calculate_all_segment_evc_impl(formula: str, segment_parameters: str) -> List[EVCResult]:
    """全セグメントのEVCを計算します - 内部実装

    Args:
        formula: EVC計算フォーミュラ
        segment_parameters: セグメント別のパラメータ

    Returns:
        全セグメントのEVC計算結果
    """
    # セグメントパラメータを解析
    import logging
    try:
        # セグメントIDを抽出（パラメータ文字列からセグメントIDを取得）
        segment_ids = []
        if isinstance(segment_parameters, str) and ':' in segment_parameters:
            # s1: 'パラメータ', s2: 'パラメータ' の形式を解析
            parts = segment_parameters.split(',')
            for part in parts:
                if ':' in part:
                    segment_id = part.split(':', 1)[0].strip()
                    if segment_id.startswith('s'):
                        segment_ids.append(segment_id)
        
        if not segment_ids:  # セグメントIDが取得できない場合はデフォルト値を使用
            segment_ids = ["s1", "s2", "s3", "s4"]
    except Exception as e:
        logging.warning(f"セグメントパラメータの解析に失敗しました: {e}")
        segment_ids = ["s1", "s2", "s3", "s4"]
    
    # 各セグメントのEVCを計算
    results = []
    
    for segment_id in segment_ids:
        # セグメントごとのパラメータを取得
        segment_param = "{}"
        if segment_id in segment_parameters:
            # s1: '売上増加率: 0.10, 年間売上: 100000000, ...' からパラメータを抽出
            segment_start = segment_parameters.find(f"{segment_id}:")
            if segment_start >= 0:
                segment_end = segment_parameters.find(",", segment_start)
                if segment_end < 0:  # 最後のセグメントの場合
                    segment_end = len(segment_parameters)
                segment_param = segment_parameters[segment_start:segment_end].split(':', 1)[1].strip().strip('\'"')
        
        # EVCを計算
        result = await calculate_evc(segment_id, formula, segment_param)
        results.append(result)
    
    return results

# ラッパー関数（同期的に呼び出し可能）
def _calculate_all_segment_evc_wrapper(formula: str, segment_parameters: str) -> List[EVCResult]:
    """全セグメントのEVCを計算します - ラッパー

    Args:
        formula: EVC計算フォーミュラ
        segment_parameters: セグメント別のパラメータ

    Returns:
        全セグメントのEVC計算結果
    """
    import asyncio
    import logging
    try:
        # 現在のイベントループを取得
        loop = asyncio.get_event_loop()
        # 非同期関数を同期的に実行
        return loop.run_until_complete(_calculate_all_segment_evc_impl(formula, segment_parameters))
    except RuntimeError as e:
        # 現在のループが閉じられている場合は新しいループを作成
        if "There is no current event loop in thread" in str(e):
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(_calculate_all_segment_evc_impl(formula, segment_parameters))
            finally:
                new_loop.close()
        # 実行中のループ内からの呼び出しの場合は、空のリストを返す
        # これはエラーを返すよりも、処理を継続させるためのフォールバック
        logging.warning(f"EVC計算中に非同期エラーが発生しました: {e}")
        return []

# function_toolの設定
calculate_all_segment_evc = function_tool(_calculate_all_segment_evc_wrapper)


@function_tool
async def analyze_value_factors(reference_products: str) -> str:
    """参照製品の価値要因を分析します。

    Args:
        reference_products: 参照製品のリスト

    Returns:
        価値要因分析結果
    """
    # 実際の実装では、参照製品を分析して価値要因を特定します
    # この例では、モックデータを返します
    return """{
        "revenue_enhancement": {
            "factors": [
                {"name": "営業効率化", "impact": "high", "description": "営業活動の効率化による売上向上"},
                {"name": "顧客維持率向上", "impact": "medium", "description": "既存顧客の維持率向上による売上安定化"},
                {"name": "クロスセル機会", "impact": "medium", "description": "関連商品の提案による追加売上"}
            ],
            "average_impact": 0.12
        },
        "cost_optimization": {
            "factors": [
                {"name": "人件費削減", "impact": "high", "description": "営業プロセスの自動化による人件費削減"},
                {"name": "営業コスト削減", "impact": "medium", "description": "効率的な顧客アプローチによる営業コスト削減"},
                {"name": "管理コスト削減", "impact": "low", "description": "一元管理による管理コスト削減"}
            ],
            "average_impact": 0.15
        },
        "reference_price": {
            "average": 15000,
            "range": [5000, 30000],
            "factors": [
                {"name": "基本機能", "value": 5000},
                {"name": "分析機能", "value": 5000},
                {"name": "連携機能", "value": 3000},
                {"name": "サポート", "value": 2000}
            ]
        },
        "implementation_cost": {
            "factors": [
                {"name": "初期設定", "impact": "medium", "description": "システム設定と初期データ移行"},
                {"name": "トレーニング", "impact": "medium", "description": "ユーザートレーニングコスト"},
                {"name": "運用管理", "impact": "low", "description": "継続的な運用管理コスト"}
            ],
            "average_initial": 20000,
            "average_operation": 5000
        }
    }"""
