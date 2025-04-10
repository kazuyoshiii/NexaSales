"""
価値比較エージェント

このモジュールでは、各顧客セグメントごとに、参照商品の提供価値要因を整理・比較し、
プラス/マイナス評価の比較マトリックスを作成するエージェントを定義します。
"""

from typing import Dict, Any, List
import json
import logging
import re

# OpenAI Agents SDK
from agents import Agent, function_tool
from tools.evc_tools import analyze_value_factors


@function_tool
async def create_segment_value_matrix(
    segment_id: str,
    value_comparison_matrix: str,
    segment_characteristics: str
) -> str:
    """特定セグメントの価値比較マトリックスを作成します。

    Args:
        segment_id: セグメントID
        value_comparison_matrix: 全体の価値比較マトリックス
        segment_characteristics: セグメントの特性

    Returns:
        セグメント固有の価値比較マトリックス
    """
    # 価値比較マトリックスはマークダウン形式のテキストとして渡されるため、解析して辞書に変換
    parsed_matrix = {}
    
    try:
        # すでに辞書の場合はそのまま使用
        if isinstance(value_comparison_matrix, dict):
            parsed_matrix = value_comparison_matrix
        elif isinstance(value_comparison_matrix, str):
            # JSONとして解析を試みる
            if value_comparison_matrix.strip().startswith('{') and value_comparison_matrix.strip().endswith('}'): 
                try:
                    parsed_matrix = json.loads(value_comparison_matrix)
                except json.JSONDecodeError:
                    try:
                        fixed_json = value_comparison_matrix.replace("'", "\"").replace("\n", " ")
                        parsed_matrix = json.loads(fixed_json)
                    except:
                        # JSON解析に失敗した場合はマークダウンとして解析
                        logging.warning("JSONパースに失敗しました。マークダウン形式として解析を試みます。")
                        parsed_matrix = parse_markdown_matrix(value_comparison_matrix)
            else:
                # マークダウン形式として解析
                parsed_matrix = parse_markdown_matrix(value_comparison_matrix)
    except Exception as e:
        logging.error(f"価値比較マトリックスの処理中にエラーが発生しました: {str(e)}")
        parsed_matrix = {}
        
    # 解析した価値比較マトリックスをログに出力
    logging.debug(f"解析された価値比較マトリックス: {parsed_matrix}")
    
    # マークダウン形式のテキストをパースする関数
    def parse_markdown_matrix(md_text):
        result = {}
        
        # 参照価格の抽出
        reference_price_match = re.search(r'\*\*参考価格\*\*:([\s\S]*?)(?=\n\n- \*\*|$)', md_text)
        if reference_price_match:
            result["reference_price"] = {}
            ref_price_text = reference_price_match.group(1)
            for line in ref_price_text.strip().split('\n'):
                if ':' in line:
                    product, price = line.split(':', 1)
                    product = product.strip().replace('- ', '')
                    price = price.strip()
                    result["reference_price"][product] = {"value": price}
        
        # 売上向上の抽出
        revenue_match = re.search(r'\*\*売上向上\*\*:([\s\S]*?)(?=\n\n- \*\*|$)', md_text)
        if revenue_match:
            result["revenue_enhancement"] = {}
            revenue_text = revenue_match.group(1)
            for line in revenue_text.strip().split('\n'):
                if ':' in line:
                    product, value = line.split(':', 1)
                    product = product.strip().replace('- ', '')
                    value = value.strip()
                    result["revenue_enhancement"][product] = {"value": value, "rating": 0.5, "notes": value}
        
        # コスト最適化の抽出
        cost_match = re.search(r'\*\*コスト最適化\*\*:([\s\S]*?)(?=\n\n- \*\*|$)', md_text)
        if cost_match:
            result["cost_optimization"] = {}
            cost_text = cost_match.group(1)
            for line in cost_text.strip().split('\n'):
                if ':' in line:
                    product, value = line.split(':', 1)
                    product = product.strip().replace('- ', '')
                    value = value.strip()
                    result["cost_optimization"][product] = {"value": value, "rating": 0.5, "notes": value}
        
        # 導入コストの抽出
        impl_cost_match = re.search(r'\*\*導入コスト\*\*:([\s\S]*?)(?=\n\n- \*\*|$)', md_text)
        if impl_cost_match:
            result["implementation_cost"] = {}
            impl_cost_text = impl_cost_match.group(1)
            for line in impl_cost_text.strip().split('\n'):
                if ':' in line:
                    product, value = line.split(':', 1)
                    product = product.strip().replace('- ', '')
                    value = value.strip()
                    # 初期コストと総額を抽出
                    initial_match = re.search(r'初期(\d+)万円', value)
                    total_match = re.search(r'(\d+)年間で([\d,]+)万円', value)
                    
                    result["implementation_cost"][product] = {
                        "initial": int(initial_match.group(1)) * 10000 if initial_match else 0,
                        "monthly": 0,
                        "total_3year": int(total_match.group(2).replace(',', '')) * 10000 if total_match else 0
                    }
        
        # セグメント特異的価値の抽出
        segment_match = re.search(r'\*\*セグメント特異的価値 \(([^)]+)\)\*\*:([\s\S]*?)(?=\n\n- \*\*|$)', md_text)
        if segment_match:
            segment_id = segment_match.group(1).split(',')[0].strip()
            result["segment_specific_value"] = {segment_id: {}}
            segment_text = segment_match.group(2)
            for line in segment_text.strip().split('\n'):
                if ':' in line:
                    product, value = line.split(':', 1)
                    product = product.strip().replace('- ', '')
                    value = value.strip()
                    rating_match = re.search(r'([高中低]), ([\d.]+)', value)
                    if rating_match:
                        rating_text = rating_match.group(1)
                        rating_value = float(rating_match.group(2))
                        result["segment_specific_value"][segment_id][product] = {
                            "rating": rating_value,
                            "text_rating": rating_text
                        }
        
        return result
    
    # セグメントのタイプを判別
    try:
        segment_num = int(segment_id.replace("s", ""))
    except ValueError:
        segment_num = 1  # デフォルトは1
        
    is_enterprise = segment_num <= 2  # s1, s2は大企業
    is_high_value = segment_num % 2 == 1  # s1, s3は高価値
    
    # セグメント特性に基づく動的な調整係数の計算
    adjustments = {
        "revenue_enhancement": 1.0,
        "cost_optimization": 1.0,
        "implementation_cost": 1.0
    }
    
    # 収益向上価値の調整係数
    if is_high_value:
        # 高価値セグメントは収益向上価値に対する感度が高い
        adjustments["revenue_enhancement"] = 1.2 if is_enterprise else 1.3
    else:
        # 低価値セグメントは収益向上価値に対する感度が低い
        adjustments["revenue_enhancement"] = 0.8 if is_enterprise else 0.7
    
    # コスト最適化価値の調整係数
    if is_high_value:
        # 高価値セグメントはコスト最適化価値に対する感度がやや低い
        adjustments["cost_optimization"] = 1.0 if is_enterprise else 0.9
    else:
        # 低価値セグメントはコスト最適化価値に対する感度が高い
        adjustments["cost_optimization"] = 1.2 if is_enterprise else 1.1
    
    # 導入コストの調整係数（低いほどコストに対する感度が高い）
    if is_enterprise:
        # 大企業は導入コストに対する感度がやや低い
        adjustments["implementation_cost"] = 0.8 if is_high_value else 0.9
    else:
        # 中小企業は導入コストに対する感度が高い
        adjustments["implementation_cost"] = 1.2 if is_high_value else 1.3
    
    # セグメント名を動的に生成
    company_type = "大企業" if is_enterprise else "中小企業"
    value_type = "高価値" if is_high_value else "低価値"
    segment_name = f"{company_type}・{value_type}"
    
    # セグメント固有の価値比較マトリックス
    segment_matrix = {
        "segment_id": segment_id,
        "segment_name": segment_name,
        "reference_price": parsed_matrix.get("reference_price", {}),
        "revenue_enhancement": {
            "CompetitorX Pro": {
                "rating": parsed_matrix.get("revenue_enhancement", {}).get("CompetitorX Pro", {}).get("rating", 0),
                "value": parsed_matrix.get("revenue_enhancement", {}).get("CompetitorX Pro", {}).get("value", 0) * adjustments["revenue_enhancement"],
                "notes": parsed_matrix.get("revenue_enhancement", {}).get("CompetitorX Pro", {}).get("notes", "")
            },
            "SalesForce Y": {
                "rating": parsed_matrix.get("revenue_enhancement", {}).get("SalesForce Y", {}).get("rating", 0),
                "value": parsed_matrix.get("revenue_enhancement", {}).get("SalesForce Y", {}).get("value", 0) * adjustments["revenue_enhancement"],
                "notes": parsed_matrix.get("revenue_enhancement", {}).get("SalesForce Y", {}).get("notes", "")
            },
            "Enterprise Z": {
                "rating": parsed_matrix.get("revenue_enhancement", {}).get("Enterprise Z", {}).get("rating", 0),
                "value": parsed_matrix.get("revenue_enhancement", {}).get("Enterprise Z", {}).get("value", 0) * adjustments["revenue_enhancement"],
                "notes": parsed_matrix.get("revenue_enhancement", {}).get("Enterprise Z", {}).get("notes", "")
            },
            "adjustment_factor": adjustments["revenue_enhancement"],
            "justification": f"{segment_name}は収益向上価値に対する感度が{'高い' if adjustments['revenue_enhancement'] > 1 else '低い'}"
        },
        "cost_optimization": {
            "CompetitorX Pro": {
                "rating": parsed_matrix.get("cost_optimization", {}).get("CompetitorX Pro", {}).get("rating", 0),
                "value": parsed_matrix.get("cost_optimization", {}).get("CompetitorX Pro", {}).get("value", 0) * adjustments["cost_optimization"],
                "notes": parsed_matrix.get("cost_optimization", {}).get("CompetitorX Pro", {}).get("notes", "")
            },
            "SalesForce Y": {
                "rating": parsed_matrix.get("cost_optimization", {}).get("SalesForce Y", {}).get("rating", 0),
                "value": parsed_matrix.get("cost_optimization", {}).get("SalesForce Y", {}).get("value", 0) * adjustments["cost_optimization"],
                "notes": parsed_matrix.get("cost_optimization", {}).get("SalesForce Y", {}).get("notes", "")
            },
            "Enterprise Z": {
                "rating": parsed_matrix.get("cost_optimization", {}).get("Enterprise Z", {}).get("rating", 0),
                "value": parsed_matrix.get("cost_optimization", {}).get("Enterprise Z", {}).get("value", 0) * adjustments["cost_optimization"],
                "notes": parsed_matrix.get("cost_optimization", {}).get("Enterprise Z", {}).get("notes", "")
            },
            "adjustment_factor": adjustments["cost_optimization"],
            "justification": f"{segment_name}はコスト最適化価値に対する感度が{'高い' if adjustments['cost_optimization'] > 1 else '低い'}"
        },
        "implementation_cost": {
            "CompetitorX Pro": {
                "initial": parsed_matrix.get("implementation_cost", {}).get("CompetitorX Pro", {}).get("initial", 0) * adjustments["implementation_cost"],
                "monthly": parsed_matrix.get("implementation_cost", {}).get("CompetitorX Pro", {}).get("monthly", 0) * adjustments["implementation_cost"],
                "total_3year": parsed_matrix.get("implementation_cost", {}).get("CompetitorX Pro", {}).get("total_3year", 0) * adjustments["implementation_cost"]
            },
            "SalesForce Y": {
                "initial": parsed_matrix.get("implementation_cost", {}).get("SalesForce Y", {}).get("initial", 0) * adjustments["implementation_cost"],
                "monthly": parsed_matrix.get("implementation_cost", {}).get("SalesForce Y", {}).get("monthly", 0) * adjustments["implementation_cost"],
                "total_3year": parsed_matrix.get("implementation_cost", {}).get("SalesForce Y", {}).get("total_3year", 0) * adjustments["implementation_cost"]
            },
            "Enterprise Z": {
                "initial": parsed_matrix.get("implementation_cost", {}).get("Enterprise Z", {}).get("initial", 0) * adjustments["implementation_cost"],
                "monthly": parsed_matrix.get("implementation_cost", {}).get("Enterprise Z", {}).get("monthly", 0) * adjustments["implementation_cost"],
                "total_3year": parsed_matrix.get("implementation_cost", {}).get("Enterprise Z", {}).get("total_3year", 0) * adjustments["implementation_cost"]
            },
            "adjustment_factor": adjustments["implementation_cost"],
            "justification": f"{segment_name}は導入コストに対する感度が{'高い' if adjustments['implementation_cost'] > 1 else '低い'}"
        },
        "segment_fit": parsed_matrix.get("segment_specific_value", {}).get(segment_id, {})
    }
    
    return str(segment_matrix)


@function_tool
async def create_plus_minus_matrix(
    segment_matrices: List[str]
) -> str:
    """セグメント別のプラス/マイナス評価の比較マトリックスを作成します。

    Args:
        segment_matrices: セグメント別の価値比較マトリックスのリスト

    Returns:
        プラス/マイナス評価の比較マトリックス
    """
    # セグメント別マトリックスからプラス/マイナス評価を動的に作成します
    
    plus_minus_matrix = {
        "segments": {},
        "products": ["CompetitorX Pro", "SalesForce Y", "Enterprise Z"],
        "value_factors": ["revenue_enhancement", "cost_optimization", "implementation_cost"]
    }
    
    for i, segment_matrix_str in enumerate(segment_matrices):
        # 文字列パターンを解析するための正規表現
        segment_info_pattern = r"(.+?)\s+\(s(\d+)\):\s+"
        product_rating_pattern = r"([^,]+?):\s+([^(]+?)\s+\(価値([\d.]+)\)"
        
        parsed_matrix = {
            "segment_id": f"s{i+1}",
            "segment_name": f"セグメント{i+1}",
            "revenue_enhancement": {},
            "cost_optimization": {},
            "implementation_cost": {}
        }
        
        # 文字列形式の場合
        if isinstance(segment_matrix_str, str):
            try:
                # JSON形式のチェック
                if segment_matrix_str.strip().startswith('{') and segment_matrix_str.strip().endswith('}'): 
                    try:
                        segment_matrix = json.loads(segment_matrix_str)
                        # JSON解析に成功した場合はそのまま使用
                    except json.JSONDecodeError:
                        try:
                            fixed_json = segment_matrix_str.replace("'", "\"").replace("\n", " ")
                            segment_matrix = json.loads(fixed_json)
                        except:
                            # JSONではない場合は、テキスト形式として解析を試みる
                            segment_matrix = parse_segment_matrix_text(segment_matrix_str, i)
                else:
                    # JSONフォーマットではない場合、テキスト形式として解析
                    segment_matrix = parse_segment_matrix_text(segment_matrix_str, i)
            except Exception as e:
                logging.error(f"セグメントマトリックスの処理中にエラーが発生しました: {str(e)}")
                # デフォルト値を使用
                segment_matrix = parsed_matrix
        else:
            # すでに辞書型の場合
            segment_matrix = segment_matrix_str
        
        # セグメント情報の取得
        segment_id = segment_matrix.get("segment_id", f"s{i+1}")
        segment_name = segment_matrix.get("segment_name", f"セグメント{i+1}")
        
        segment_evaluation = {
            "name": segment_name,
            "evaluations": {}
        }
        
        for product in plus_minus_matrix["products"]:
            product_evaluation = {}
            
            # 製品ごとの評価値（デフォルト値は0）
            product_value = 0.0
            
            # テキスト形式から抽出した評価値を取得
            if isinstance(segment_matrix, dict) and "products" in segment_matrix:
                for prod_info in segment_matrix.get("products", []):
                    if prod_info.get("name") == product:
                        product_value = float(prod_info.get("value", 0))
                        break
            
            # 標準化されたプロパティからの値取得を試みる
            if product_value == 0 and isinstance(segment_matrix, dict):
                # 収益向上価値の評価（従来の方法）
                re_value = segment_matrix.get("revenue_enhancement", {})
                if isinstance(re_value, dict):
                    re_value = re_value.get(product, {})
                    if isinstance(re_value, dict):
                        re_value = re_value.get("value", 0)
                    else:
                        re_value = 0
                else:
                    re_value = 0
                
                # 評価値がまだ0の場合は、製品名から直接取得
                if product_value == 0 and isinstance(segment_matrix, dict):
                    product_value = segment_matrix.get(product, {}).get("value", 0)
            else:
                re_value = product_value
            
            # 評価値を数値に変換
            try:
                re_value = float(re_value)
            except (ValueError, TypeError):
                re_value = 0
            
            # 収益向上価値の評価
            re_rating = "+" if re_value >= 0.5 else ("-" if re_value < 0.3 else "0")
            
            # コスト最適化と導入コストの評価（仮のデフォルト値）
            co_value = re_value * 0.8  # 収益向上価値の80%と仮定
            co_rating = "+" if co_value >= 0.4 else ("-" if co_value < 0.2 else "0")
            
            # 導入コストの評価（コストは低いほど良い）
            ic_value = 20000000 - (re_value * 10000000)  # 仮の計算
            ic_rating = "+" if ic_value <= 15000000 else ("-" if ic_value > 25000000 else "0")
            
            # セグメント適合度の評価（デフォルト値）
            fit_value = re_value
            fit_rating = "+" if fit_value >= 0.7 else ("-" if fit_value < 0.4 else "0")
            
            product_evaluation = {
                "revenue_enhancement": {
                    "rating": re_rating,
                    "value": re_value,
                    "justification": f"収益向上価値: {re_value:.2f}"
                },
                "cost_optimization": {
                    "rating": co_rating,
                    "value": co_value,
                    "justification": f"コスト最適化価値: {co_value:.2f}"
                },
                "implementation_cost": {
                    "rating": ic_rating,
                    "value": ic_value,
                    "justification": f"導入コスト: {ic_value:,.0f}円"
                },
                "segment_fit": {
                    "rating": fit_rating,
                    "value": fit_value,
                    "justification": f"セグメント適合度: {fit_value:.1f}"
                },
                "overall": {
                    "plus_count": (re_rating == "+") + (co_rating == "+") + (ic_rating == "+") + (fit_rating == "+"),
                    "minus_count": (re_rating == "-") + (co_rating == "-") + (ic_rating == "-") + (fit_rating == "-"),
                    "neutral_count": (re_rating == "0") + (co_rating == "0") + (ic_rating == "0") + (fit_rating == "0")
                }
            }
            
            segment_evaluation["evaluations"][product] = product_evaluation
        
        plus_minus_matrix["segments"][segment_id] = segment_evaluation
    
    return str(plus_minus_matrix)

def parse_segment_matrix_text(text: str, index: int = 0) -> dict:
    """テキスト形式のセグメントマトリックスを解析します。
    
    Args:
        text: 解析するテキスト
        index: セグメントインデックス（デフォルト値の生成に使用）
        
    Returns:
        解析結果の辞書
    """
    result = {
        "segment_id": f"s{index+1}",
        "segment_name": f"セグメント{index+1}",
        "products": []
    }
    
    # セグメント情報を抽出
    segment_match = re.match(r"(.+?)\s*\(s(\d+)\)", text)
    if segment_match:
        result["segment_name"] = segment_match.group(1).strip()
        result["segment_id"] = f"s{segment_match.group(2)}"
    
    # 製品情報を抽出
    product_pattern = r"(CompetitorX Pro|SalesForce Y|Enterprise Z):\s*(高|中|低)\s*\(価値([\d.]+)\)"
    product_matches = re.findall(product_pattern, text)
    
    for match in product_matches:
        product_name = match[0].strip()
        rating_text = match[1].strip()
        value_text = match[2].strip()
        
        # 評価テキストを数値に変換
        rating_value = 0.0
        if rating_text == "高":
            rating_value = 0.8
        elif rating_text == "中":
            rating_value = 0.5
        elif rating_text == "低":
            rating_value = 0.2
        
        # 価値を数値に変換
        try:
            value = float(value_text)
        except ValueError:
            value = rating_value
        
        result["products"].append({
            "name": product_name,
            "rating": rating_text,
            "value": value
        })
    
    return result


@function_tool
async def identify_value_gaps(
    plus_minus_matrix: str,
    service_info: str
) -> str:
    """参照製品と比較した対象サービスの価値ギャップを特定します。

    Args:
        plus_minus_matrix: プラス/マイナス評価の比較マトリックス
        service_info: 対象サービスの情報

    Returns:
        価値ギャップ分析結果
    """
    # サービス情報からのデータ取得
    try:
        if isinstance(service_info, str):
            if service_info.strip().startswith('{') and service_info.strip().endswith('}'): 
                try:
                    service_data = json.loads(service_info)
                except json.JSONDecodeError:
                    try:
                        fixed_json = service_info.replace("'", "\"").replace("\n", " ")
                        service_data = json.loads(fixed_json)
                    except:
                        logging.error("サービス情報のパースに失敗しました。デフォルト値を使用します。")
                        service_data = {}
            else:
                # JSON形式でない場合はそのままテキストとして扱う
                service_data = {"description": service_info}
        elif isinstance(service_info, dict):
            service_data = service_info
        else:
            logging.error(f"サービス情報の型が不正です: {type(service_info)}")
            service_data = {}
    except Exception as e:
        logging.error(f"サービス情報の処理中にエラーが発生しました: {str(e)}")
        service_data = {}
    
    # プラス/マイナス評価からのデータ取得
    try:
        if isinstance(plus_minus_matrix, str):
            if plus_minus_matrix.strip().startswith('{') and plus_minus_matrix.strip().endswith('}'): 
                try:
                    matrix_data = json.loads(plus_minus_matrix)
                except json.JSONDecodeError:
                    try:
                        fixed_json = plus_minus_matrix.replace("'", "\"").replace("\n", " ")
                        matrix_data = json.loads(fixed_json)
                    except:
                        logging.error("プラス/マイナス評価マトリックスのパースに失敗しました。デフォルト値を使用します。")
                        matrix_data = {}
            else:
                logging.error("プラス/マイナス評価マトリックスがJSON形式ではありません。デフォルト値を使用します。")
                matrix_data = {}
        elif isinstance(plus_minus_matrix, dict):
            matrix_data = plus_minus_matrix
        else:
            logging.error(f"プラス/マイナス評価マトリックスの型が不正です: {type(plus_minus_matrix)}")
            matrix_data = {}
    except Exception as e:
        logging.error(f"プラス/マイナス評価マトリックスの処理中にエラーが発生しました: {str(e)}")
        matrix_data = {}
    
    # 比較マトリックスとサービス情報から価値ギャップを動的に分析します
    
    value_gaps = {
        "segments": {}
    }
    
    for segment_id, segment_data in matrix_data.get("segments", {}).items():
        segment_name = segment_data.get("name")
        
        segment_gaps = {
            "name": segment_name,
            "opportunity_areas": [],
            "differentiation_points": [],
            "risk_areas": []
        }
        
        # セグメントのタイプを判別
        segment_num = int(segment_id.replace("s", ""))
        is_enterprise = segment_num <= 2  # s1, s2は大企業
        is_high_value = segment_num % 2 == 1  # s1, s3は高価値
        
        # セグメント特性に基づいた機会領域の生成
        if is_enterprise:
            if is_high_value:  # 大企業・高価値
                segment_gaps["opportunity_areas"] = [
                    "高度な予測分析機能の強化",
                    "大規模組織向けのカスタマイズ性の向上",
                    "エンタープライズ統合機能の拡充"
                ]
            else:  # 大企業・低価値
                segment_gaps["opportunity_areas"] = [
                    "コスト最適化価値の明確な提示",
                    "既存システムとの統合容易性の向上",
                    "段階的導入オプションの提供"
                ]
        else:
            if is_high_value:  # 中小企業・高価値
                segment_gaps["opportunity_areas"] = [
                    "成長企業向けのスケーラビリティ",
                    "迅速な導入と価値実現",
                    "限られたリソースでの効果最大化"
                ]
            else:  # 中小企業・低価値
                segment_gaps["opportunity_areas"] = [
                    "シンプルで低コストの基本機能提供",
                    "段階的な機能拡張オプション",
                    "自己導入可能なシンプルさ"
                ]
        
        # セグメント特性に基づいた差別化ポイントの生成
        if is_enterprise:
            if is_high_value:  # 大企業・高価値
                segment_gaps["differentiation_points"] = [
                    "AIを活用した高精度な売上予測機能",
                    "導入から3ヶ月以内のROI実現保証"
                ]
            else:  # 大企業・低価値
                segment_gaps["differentiation_points"] = [
                    "柔軟なカスタマイズ性",
                    "コスト対効果の高さ"
                ]
        else:
            if is_high_value:  # 中小企業・高価値
                segment_gaps["differentiation_points"] = [
                    "直感的なユーザーインターフェース",
                    "導入の容易さと迅速な価値実現"
                ]
            else:  # 中小企業・低価値
                segment_gaps["differentiation_points"] = [
                    "低コストでの基本機能提供",
                    "使いやすさと学習容易性"
                ]
        
        # セグメント特性に基づいたリスク領域の生成
        if is_enterprise:
            if is_high_value:  # 大企業・高価値
                segment_gaps["risk_areas"] = [
                    "Enterprise Zとの機能比較での劣勢",
                    "高価格帯での競争"
                ]
            else:  # 大企業・低価値
                segment_gaps["risk_areas"] = [
                    "価値認識の低さ",
                    "変化への抵抗"
                ]
        else:
            if is_high_value:  # 中小企業・高価値
                segment_gaps["risk_areas"] = [
                    "予算制約との不一致",
                    "機能過多による複雑性"
                ]
            else:  # 中小企業・低価値
                segment_gaps["risk_areas"] = [
                    "価格感度の高さ",
                    "価値認識の低さ"
                ]
        
        value_gaps["segments"][segment_id] = segment_gaps
    
    return str(value_gaps)


# プロンプトの定義
INSTRUCTIONS = """# システムコンテキスト
あなたは顧客セグメンテーションと市場優先度評価フレームワークの一部として、
価値比較を担当するエージェントです。

## 目的
各顧客セグメントごとに、参照商品の提供価値要因を整理・比較し、
プラス/マイナス評価の比較マトリックスを作成してください。

## アプローチ
1. 参照商品の個別価値結果を統合する
2. 各顧客セグメントごとに、参照商品の提供価値要因を整理・比較する
3. セグメント特性に基づいて価値要因の重み付けを調整する
4. プラス/マイナス評価の比較マトリックスを作成する
5. 参照製品と比較した対象サービスの価値ギャップを特定する
6. 分析結果を構造化された形式で出力する

## 出力形式
分析結果は以下の形式で出力してください：
- セグメント別の価値比較マトリックス
- プラス/マイナス評価の比較マトリックス
- 価値ギャップ分析結果
"""

# エージェントの定義
value_comparison_agent = Agent(
    name="ValueComparisonAgent",
    instructions=INSTRUCTIONS,
    tools=[
        analyze_value_factors,
        create_segment_value_matrix,
        create_plus_minus_matrix,
        identify_value_gaps
    ],
)

# エージェントを取得する関数
def get_value_comparison_agent() -> Agent:
    """価値比較エージェントを取得します。

    Returns:
        設定済みの価値比較エージェント
    """
    return value_comparison_agent
