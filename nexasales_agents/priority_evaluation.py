"""
優先度評価エージェント

このモジュールでは、EVC計算と市場ポテンシャル分析の結果を統合して、セグメント別の優先度を評価するエージェントを定義します。
"""

from typing import Dict, Any, List
# OpenAI Agents SDK
from agents import Agent, function_tool
from models.models import PriorityReport, CustomerSegment, MarketPotential, EVCResult


@function_tool
async def integrate_evc_and_market_potential(
    evc_results: List[str],
    market_potentials: List[str]
) -> str:
    """EVC計算結果と市場ポテンシャル分析結果を統合します。

    Args:
        evc_results: EVC計算結果のリスト
        market_potentials: 市場ポテンシャル分析結果のリスト

    Returns:
        統合結果
    """
    import json
    import logging
    
    # EVCデータの処理と解析
    processed_evc_results = []
    for i, result in enumerate(evc_results):
        try:
            if isinstance(result, str):
                if result.strip().startswith('{') and result.strip().endswith('}'): 
                    try:
                        evc_data = json.loads(result)
                    except json.JSONDecodeError:
                        try:
                            # シングルクォートをダブルクォートに変換するなどの修正を試みる
                            fixed_json = result.replace("'", "\"").replace("\n", " ")
                            evc_data = json.loads(fixed_json)
                        except:
                            # JSONパースに失敗した場合は、テキストからデータを抽出
                            evc_data = extract_data_from_text(result, "EVC")
                else:
                    # JSONとして解析できない場合はテキストから情報を抽出
                    evc_data = extract_data_from_text(result, "EVC")
            elif isinstance(result, dict):
                evc_data = result
            else:
                logging.error(f"EVC結果{i}の型が不正です: {type(result)}")
                evc_data = {}
        except Exception as e:
            logging.error(f"EVC結果{i}の処理中にエラーが発生しました: {str(e)}")
            evc_data = {}
        
        processed_evc_results.append(evc_data)
    
    # 市場ポテンシャルデータの処理と解析
    processed_market_potentials = []
    for i, potential in enumerate(market_potentials):
        try:
            if isinstance(potential, str):
                if potential.strip().startswith('{') and potential.strip().endswith('}'): 
                    try:
                        market_data = json.loads(potential)
                    except json.JSONDecodeError:
                        try:
                            # シングルクォートをダブルクォートに変換するなどの修正を試みる
                            fixed_json = potential.replace("'", "\"").replace("\n", " ")
                            market_data = json.loads(fixed_json)
                        except:
                            # JSONパースに失敗した場合は、テキストからデータを抽出
                            market_data = extract_data_from_text(potential, "市場ポテンシャル")
                else:
                    # JSONとして解析できない場合はテキストから情報を抽出
                    market_data = extract_data_from_text(potential, "市場ポテンシャル")
            elif isinstance(potential, dict):
                market_data = potential
            else:
                logging.error(f"市場ポテンシャル結果{i}の型が不正です: {type(potential)}")
                market_data = {}
        except Exception as e:
            logging.error(f"市場ポテンシャル結果{i}の処理中にエラーが発生しました: {str(e)}")
            market_data = {}
        
        processed_market_potentials.append(market_data)
    
    # セグメントIDをキーとした辞書を作成
    evc_by_segment = {result.get("segment_id"): result for result in processed_evc_results if result.get("segment_id")}
    potential_by_segment = {potential.get("segment_id"): potential for potential in processed_market_potentials if potential.get("segment_id")}
    
    # すべてのセグメントIDを取得
    all_segment_ids = set(list(evc_by_segment.keys()) + list(potential_by_segment.keys()))
    
    # 統合結果
    integrated_results = []
    
    for segment_id in all_segment_ids:
        evc_result = evc_by_segment.get(segment_id, {})
        market_potential = potential_by_segment.get(segment_id, {})
        
        # セグメント名の取得
        segment_name = evc_result.get("segment_name") or market_potential.get("segment_name") or f"セグメント {segment_id}"
        
        # EVC値の取得
        evc_value = evc_result.get("evc_value", 0)
        
        # 市場ポテンシャルの取得
        market_size = market_potential.get("market_size", 0)
        acquisition_probability = market_potential.get("acquisition_probability", 0)
        total_potential_value = market_potential.get("total_potential_value", 0)
        
        # 統合結果の作成
        integrated_result = {
            "segment_id": segment_id,
            "segment_name": segment_name,
            "evc_value": evc_value,
            "market_size": market_size,
            "acquisition_probability": acquisition_probability,
            "total_potential_value": total_potential_value,
            "evc_components": evc_result.get("components", {}),
            "market_analysis": market_potential.get("analysis_details", {})
        }
        
        integrated_results.append(integrated_result)
    
    return str({
        "integrated_results": integrated_results
    })


@function_tool
async def calculate_priority_scores(integrated_results: List[str]) -> str:
    """セグメント別の優先度スコアを計算します。

    Args:
        integrated_results: 統合結果のリスト

    Returns:
        優先度スコア計算結果
    """
    import json
    import logging
    
    # 統合結果の解析
    processed_integrated_results = []
    try:
        if isinstance(integrated_results, str):
            try:
                if integrated_results.strip().startswith('{') and integrated_results.strip().endswith('}'): 
                    try:
                        integrated_data = json.loads(integrated_results)
                        # 統合結果がキー「integrated_results」の下にある場合
                        if "integrated_results" in integrated_data:
                            processed_integrated_results = integrated_data["integrated_results"]
                        else:
                            processed_integrated_results = [integrated_data]
                    except json.JSONDecodeError:
                        try:
                            # シングルクォートをダブルクォートに変換するなどの修正を試みる
                            fixed_json = integrated_results.replace("'", "\"").replace("\n", " ")
                            integrated_data = json.loads(fixed_json)
                            if "integrated_results" in integrated_data:
                                processed_integrated_results = integrated_data["integrated_results"]
                            else:
                                processed_integrated_results = [integrated_data]
                        except:
                            logging.error(f"統合結果のパースに失敗しました。")
                            processed_integrated_results = []
                else:
                    # 辞書リストの場合はそのまま使用
                    if isinstance(integrated_results, list):
                        processed_integrated_results = integrated_results
                    else:
                        logging.warning(f"統合結果がJSON形式ではありません。")
                        processed_integrated_results = []
            except Exception as e:
                logging.error(f"統合結果の処理中にエラーが発生しました: {str(e)}")
                processed_integrated_results = []
        elif isinstance(integrated_results, dict):
            if "integrated_results" in integrated_results:
                processed_integrated_results = integrated_results["integrated_results"]
            else:
                processed_integrated_results = [integrated_results]
        elif isinstance(integrated_results, list):
            processed_integrated_results = integrated_results
        else:
            logging.error(f"統合結果の型が不正です: {type(integrated_results)}")
            processed_integrated_results = []
    except Exception as e:
        logging.error(f"統合結果の処理中にエラーが発生しました: {str(e)}")
        processed_integrated_results = []
    # 優先度スコアの計算パラメータ
    weights = {
        "evc_value": 0.4,          # EVC値の重み
        "market_size": 0.2,         # 市場規模の重み
        "acquisition_probability": 0.3,  # 獲得確率の重み
        "growth_potential": 0.1     # 成長ポテンシャルの重み
    }
    
    # 各指標の最大値を取得（正規化のため）
    max_evc = max([result.get("evc_value", 0) for result in integrated_results]) if integrated_results else 1
    max_market_size = max([result.get("market_size", 0) for result in integrated_results]) if integrated_results else 1
    max_potential = max([result.get("total_potential_value", 0) for result in integrated_results]) if integrated_results else 1
    
    # 優先度スコアの計算
    priority_scores = []
    
    for result in integrated_results:
        segment_id = result.get("segment_id")
        segment_name = result.get("segment_name")
        
        # 各指標の正規化
        normalized_evc = result.get("evc_value", 0) / max_evc if max_evc > 0 else 0
        normalized_market_size = result.get("market_size", 0) / max_market_size if max_market_size > 0 else 0
        normalized_acquisition = result.get("acquisition_probability", 0)  # 確率は既に0-1の範囲
        
        # 成長ポテンシャルの計算（市場分析から）
        market_analysis = result.get("market_analysis", {})
        growth_rate = market_analysis.get("market_growth_rate", 0)
        normalized_growth = min(growth_rate / 0.1, 1)  # 10%以上の成長率を1として正規化
        
        # 優先度スコアの計算
        priority_score = (
            weights["evc_value"] * normalized_evc +
            weights["market_size"] * normalized_market_size +
            weights["acquisition_probability"] * normalized_acquisition +
            weights["growth_potential"] * normalized_growth
        )
        
        # 優先度ランクの決定
        if priority_score >= 0.8:
            priority_rank = "最優先"
        elif priority_score >= 0.6:
            priority_rank = "高優先"
        elif priority_score >= 0.4:
            priority_rank = "中優先"
        elif priority_score >= 0.2:
            priority_rank = "低優先"
        else:
            priority_rank = "最低優先"
        
        # 優先度スコア情報の作成
        priority_score_info = {
            "segment_id": segment_id,
            "segment_name": segment_name,
            "priority_score": priority_score,
            "priority_rank": priority_rank,
            "score_components": {
                "evc_value": {
                    "raw_value": result.get("evc_value", 0),
                    "normalized_value": normalized_evc,
                    "weight": weights["evc_value"],
                    "contribution": weights["evc_value"] * normalized_evc
                },
                "market_size": {
                    "raw_value": result.get("market_size", 0),
                    "normalized_value": normalized_market_size,
                    "weight": weights["market_size"],
                    "contribution": weights["market_size"] * normalized_market_size
                },
                "acquisition_probability": {
                    "raw_value": result.get("acquisition_probability", 0),
                    "normalized_value": normalized_acquisition,
                    "weight": weights["acquisition_probability"],
                    "contribution": weights["acquisition_probability"] * normalized_acquisition
                },
                "growth_potential": {
                    "raw_value": growth_rate,
                    "normalized_value": normalized_growth,
                    "weight": weights["growth_potential"],
                    "contribution": weights["growth_potential"] * normalized_growth
                }
            }
        }
        
        priority_scores.append(priority_score_info)
    
    # 優先度スコアの降順でソート
    priority_scores.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return str({
        "priority_scores": priority_scores,
        "weights": weights
    })


@function_tool
async def generate_segment_strategies(priority_scores: List[str]) -> str:
    """セグメント別の戦略を生成します。

    Args:
        priority_scores: 優先度スコア計算結果のリスト

    Returns:
        セグメント戦略
    """
    import json
    import logging
    
    # 優先度スコアの解析
    processed_priority_scores = []
    try:
        if isinstance(priority_scores, str):
            try:
                if priority_scores.strip().startswith('{') and priority_scores.strip().endswith('}'): 
                    try:
                        scores_data = json.loads(priority_scores)
                        # 優先度スコアがキー「priority_scores」の下にある場合
                        if "priority_scores" in scores_data:
                            processed_priority_scores = scores_data["priority_scores"]
                        else:
                            processed_priority_scores = [scores_data]
                    except json.JSONDecodeError:
                        try:
                            # シングルクォートをダブルクォートに変換するなどの修正を試みる
                            fixed_json = priority_scores.replace("'", "\"").replace("\n", " ")
                            scores_data = json.loads(fixed_json)
                            if "priority_scores" in scores_data:
                                processed_priority_scores = scores_data["priority_scores"]
                            else:
                                processed_priority_scores = [scores_data]
                        except:
                            logging.error(f"優先度スコアのパースに失敗しました。")
                            processed_priority_scores = []
                else:
                    # 辞書リストの場合はそのまま使用
                    if isinstance(priority_scores, list):
                        processed_priority_scores = priority_scores
                    else:
                        logging.warning(f"優先度スコアがJSON形式ではありません。")
                        processed_priority_scores = []
            except Exception as e:
                logging.error(f"優先度スコアの処理中にエラーが発生しました: {str(e)}")
                processed_priority_scores = []
        elif isinstance(priority_scores, dict):
            if "priority_scores" in priority_scores:
                processed_priority_scores = priority_scores["priority_scores"]
            else:
                processed_priority_scores = [priority_scores]
        elif isinstance(priority_scores, list):
            processed_priority_scores = priority_scores
        else:
            logging.error(f"優先度スコアの型が不正です: {type(priority_scores)}")
            processed_priority_scores = []
    except Exception as e:
        logging.error(f"優先度スコアの処理中にエラーが発生しました: {str(e)}")
        processed_priority_scores = []
    # セグメント別の戦略テンプレート
    strategy_templates = {
        "最優先": {
            "approach": "積極的投資",
            "resource_allocation": "最大リソース配分",
            "timeline": "即時開始",
            "key_tactics": [
                "専任営業チームの編成",
                "カスタマイズされた提案資料の作成",
                "トップマネジメントへの直接アプローチ",
                "業界イベントでの集中的なプロモーション"
            ]
        },
        "高優先": {
            "approach": "重点投資",
            "resource_allocation": "高リソース配分",
            "timeline": "1-2ヶ月以内に開始",
            "key_tactics": [
                "専門営業担当者のアサイン",
                "セグメント特化型マーケティング資料の作成",
                "業界セミナーの開催",
                "既存顧客からの紹介プログラムの活用"
            ]
        },
        "中優先": {
            "approach": "選択的投資",
            "resource_allocation": "中程度のリソース配分",
            "timeline": "3-6ヶ月以内に開始",
            "key_tactics": [
                "標準的な営業プロセスの適用",
                "デジタルマーケティングの活用",
                "パートナー企業との協業",
                "成功事例の共有"
            ]
        },
        "低優先": {
            "approach": "効率的アプローチ",
            "resource_allocation": "限定的なリソース配分",
            "timeline": "6-12ヶ月以内に開始",
            "key_tactics": [
                "インバウンドマーケティングの活用",
                "セルフサービス型の導入プロセス",
                "オンラインセミナーの開催",
                "自動化されたフォローアップ"
            ]
        },
        "最低優先": {
            "approach": "最小限の投資",
            "resource_allocation": "最小限のリソース配分",
            "timeline": "機会があれば対応",
            "key_tactics": [
                "標準製品の提供",
                "セルフサービスポータルの活用",
                "自動化されたマーケティング",
                "パートナー企業への委託"
            ]
        }
    }
    
    # セグメント別の戦略を生成
    segment_strategies = []
    
    for score_info in priority_scores:
        segment_id = score_info.get("segment_id")
        segment_name = score_info.get("segment_name")
        priority_rank = score_info.get("priority_rank")
        
        # 優先度ランクに基づく戦略テンプレートの取得
        template = strategy_templates.get(priority_rank, strategy_templates["最低優先"])
        
        # セグメント固有の戦略の生成
        if segment_id == "s1":  # 大企業・高価値
            specific_tactics = [
                "AIを活用した高精度な売上予測機能の強調",
                "エンタープライズ統合機能の強化",
                "セキュリティ機能の強調",
                "トップマネジメント向けのエグゼクティブブリーフィングの実施"
            ]
            value_proposition = "高度な分析機能とエンタープライズ統合による業務効率化と売上向上"
        elif segment_id == "s2":  # 大企業・低価値
            specific_tactics = [
                "コスト最適化価値の明確な提示",
                "既存システムとの統合の容易さの強調",
                "シンプルな操作性の強調",
                "段階的な導入プランの提案"
            ]
            value_proposition = "コスト効率と既存システム統合による業務プロセスの最適化"
        elif segment_id == "s3":  # 中小企業・高価値
            specific_tactics = [
                "成長支援機能の強調",
                "コストパフォーマンスの高さの提示",
                "使いやすさと短期間での導入の強調",
                "成功事例の共有"
            ]
            value_proposition = "成長企業向けの機能とコストパフォーマンスによる競争力強化"
        elif segment_id == "s4":  # 中小企業・低価値
            specific_tactics = [
                "低価格プランの提供",
                "シンプルな機能セットの強調",
                "セルフサービス型の導入プロセスの提供",
                "オンラインサポートの充実"
            ]
            value_proposition = "低コストで導入可能なシンプルなソリューションによる業務効率化"
        else:
            specific_tactics = template["key_tactics"]
            value_proposition = "顧客ニーズに合わせたソリューションの提供"
        
        # 戦略情報の作成
        strategy = {
            "segment_id": segment_id,
            "segment_name": segment_name,
            "priority_rank": priority_rank,
            "priority_score": score_info.get("priority_score", 0),
            "approach": template["approach"],
            "resource_allocation": template["resource_allocation"],
            "timeline": template["timeline"],
            "value_proposition": value_proposition,
            "key_tactics": specific_tactics
        }
        
        segment_strategies.append(strategy)
    
    return str({
        "segment_strategies": segment_strategies
    })


def extract_data_from_text(text: str, data_type: str) -> Dict[str, Any]:
    """
    テキストからデータを抽出する
    
    Args:
        text: 抽出対象のテキスト
        data_type: データの種類(「EVC」または「市場ポテンシャル」)
        
    Returns:
        抽出されたデータ
    """
    import re
    import logging
    
    result = {}
    
    # セグメント情報をマッチングするパターン
    segment_patterns = [
        r"セグメントs(\d+)\s*\((.*?)\)", # セグメントs1 (大企業・高価値)
        r"セグメント:\s*(大企業・高価値|大企業・低価値|中小企業・高価値|中小企業・低価値)", # セグメント: 大企業・高価値
        r"\*\*セグメント:(.*?)\*\*" # **セグメント:大企業・高価値**
    ]
    
    # セグメント名を抽出
    segment_name = None
    for pattern in segment_patterns:
        matches = re.search(pattern, text)
        if matches:
            if len(matches.groups()) == 2:
                segment_id = f"s{matches.group(1)}"
                segment_name = matches.group(2).strip()
            else:
                segment_name = matches.group(1).strip()
                # IDが取得できなかった場合、名前からIDを推測
                if "大企業・高価値" in segment_name:
                    segment_id = "s1"
                elif "大企業・低価値" in segment_name:
                    segment_id = "s2"
                elif "中小企業・高価値" in segment_name:
                    segment_id = "s3"
                elif "中小企業・低価値" in segment_name:
                    segment_id = "s4"
                else:
                    segment_id = "s0"
            break
    
    if segment_name:
        result["segment_id"] = segment_id
        result["segment_name"] = segment_name
        
        # データタイプに基づいて、特定の値を抽出
        if data_type == "EVC":
            # EVC値を抽出
            evc_match = re.search(r"EVC\D+(\d+[,.]?\d*億?万?円)", text)
            if evc_match:
                result["evc_value"] = evc_match.group(1)
                
            # 各要素の値を抽出
            components = {
                "reference_price": r"参照価格\D+(\d+[,.]?\d*億?万?円)",
                "revenue_enhancement": r"収益向上価値\D+(\d+[,.]?\d*億?万?円)",
                "cost_optimization": r"コスト最適化価値\D+(\d+[,.]?\d*億?万?円)",
                "implementation_cost": r"導入コスト\D+(\d+[,.]?\d*億?万?円)"
            }
            
            for key, pattern in components.items():
                match = re.search(pattern, text)
                if match:
                    result[key] = match.group(1)
                    
        elif data_type == "市場ポテンシャル":
            # 市場ポテンシャル情報を抽出
            patterns = {
                "company_count": r"総企業数\D+(\d+[,.]?\d*)",
                "acquisition_probability": r"調整後獲得確率\D+(\d+)%",
                "market_potential": r"総市場ポテンシャル\D+(\d+[,.]?\d*億?万?円)"
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, text)
                if match:
                    result[key] = match.group(1)
    
    return result
