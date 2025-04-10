"""
NexaSales - 顧客セグメンテーションと市場優先度評価フレームワーク

このモジュールは、セグメンテーションワークフローを提供します。
"""
import json
import logging
import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
import re
import json
import traceback

from openai import OpenAI
from openai.types.beta.threads import Run

# SDK v1.x 向けインポート
try:
    from openai.agents import Agent, Handoff, RunContextWrapper
    from openai.agents.runners import Runner
    # トレース機能をインポート
    from openai.agents import gen_trace_id
    SDK_VERSION = "v1"
except ImportError:
    # SDK v0.x 向けインポート
    try:
        from openai.beta.agents import Agent, Handoff
        from openai.beta.agents.runners import Runner
        # トレース機能をインポート
        from openai.beta.agents import gen_trace_id
        SDK_VERSION = "v0"
    except ImportError:
        # どのバージョンもインポートできない場合の処理
        Agent = None
        Handoff = None
        Runner = None
        gen_trace_id = None
        SDK_VERSION = "unknown"

# ローカルモジュールをインポート
from nexasales_agents.service_analysis import get_service_analysis_agent
from nexasales_agents.customer_segment import get_customer_segment_agent
from nexasales_agents.reference_product import get_reference_product_agent
from nexasales_agents.value_comparison import get_value_comparison_agent
from nexasales_agents.formula_design import get_formula_design_agent
from nexasales_agents.evc_calculation import get_evc_calculation_agent
from nexasales_agents.market_potential import get_market_potential_agent
from nexasales_agents.priority_evaluation_final import get_priority_evaluation_agent
from utils.agent_utils import call_agent, get_tracer

async def extract_service_analysis_results(text: str) -> str:
    """サービス分析結果を抽出します。

    Args:
        text: サービス分析結果のテキスト

    Returns:
        抽出されたサービス分析結果
    """
    return text


async def extract_customer_segments(text: str) -> str:
    """顧客セグメント情報を抽出し、標準化されたフォーマットに変換します。

    Args:
        text: 顧客セグメント情報のテキスト

    Returns:
        構造化された顧客セグメント情報のJSON文字列
    """
    try:
        segments = []
        # セグメント情報の抽出（マークダウン形式、テキスト形式どちらにも対応）
        segment_pattern = r'(?:###\s*セグメント:\s*|セグメント[：:]\s*)(.*?)(?:\n|$)'
        for segment_match in re.finditer(segment_pattern, text, re.MULTILINE):
            segment_text = text[segment_match.start():].split('\n\n', 1)[0]
            
            # セグメント名を抽出
            segment_name = segment_match.group(1).strip()
            
            # セグメントID抽出（s1形式または名称そのもの）
            segment_id_match = re.search(r'セグメントID[：:]\s*(.*?)(?:\n|$)', segment_text)
            segment_id = segment_id_match.group(1).strip() if segment_id_match else f"s{len(segments)+1}"
            
            # 既存のs1形式でない場合は、sX形式に統一する
            if not re.match(r'^s\d+$', segment_id):
                # 既に日本語名の場合は、新しいsX形式のIDを割り当てる
                segment_id = f"s{len(segments)+1}"
            
            # 価値創出ポテンシャル抽出
            value_potential_match = re.search(r'価値創出ポテンシャル[：:]\s*(高|low|middle|medium|低|high|HIGH|LOW)', segment_text, re.IGNORECASE)
            value_potential = value_potential_match.group(1).lower() if value_potential_match else "medium"
            # 「高」「低」を「high」「low」に変換
            if value_potential == "高":
                value_potential = "high"
            elif value_potential == "低":
                value_potential = "low"
            elif value_potential in ["middle", "medium"]:
                value_potential = "medium"  # 中間値も許容
            
            # 実現容易性抽出
            impl_ease_match = re.search(r'実現容易性[：:]\s*(高|low|middle|medium|低|high|HIGH|LOW)', segment_text, re.IGNORECASE)
            impl_ease = impl_ease_match.group(1).lower() if impl_ease_match else "medium"
            # 「高」「低」を「high」「low」に変換
            if impl_ease == "高":
                impl_ease = "high"
            elif impl_ease == "低":
                impl_ease = "low"
            elif impl_ease in ["middle", "medium"]:
                impl_ease = "medium"  # 中間値も許容
            
            # 特性リスト抽出
            characteristics = []
            char_match = re.search(r'特性[：:]\s*(.*?)(?:\n\n|$)', segment_text, re.DOTALL)
            if char_match:
                char_text = char_match.group(1).strip()
                # リスト形式の特性を抽出
                for line in char_text.split('\n'):
                    line = line.strip()
                    if line.startswith('-') or line.startswith('*'):
                        char = line[1:].strip()
                        if char:
                            characteristics.append(char)
            
            # 説明文抽出
            desc_match = re.search(r'説明[：:]\s*(.*?)(?:\n\n|$)', segment_text, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # セグメントタイプの判定（ビジネス要件に沿った4つの基本タイプ）
            segment_type = None
            # 価値創出ポテンシャルと実現容易性の組み合わせでセグメントタイプを判定
            if value_potential == "high" and impl_ease == "high":
                segment_type = "high_value_low_barrier"  # 高価値・低障壁（最優先）
            elif value_potential == "high" and (impl_ease == "low" or impl_ease == "medium"):
                segment_type = "high_value_high_barrier"  # 高価値・高障壁
            elif (value_potential == "low" or value_potential == "medium") and impl_ease == "high":
                segment_type = "low_value_low_barrier"    # 低価値・低障壁
            elif (value_potential == "low" or value_potential == "medium") and (impl_ease == "low" or impl_ease == "medium"):
                segment_type = "low_value_high_barrier"  # 低価値・高障壁
            
            # セグメント情報を構造化
            segment = {
                "segment_id": segment_id,
                "name": segment_name,
                "value_potential": value_potential,
                "implementation_ease": impl_ease,
                "segment_type": segment_type,
                "characteristics": characteristics,
                "description": description
            }
            segments.append(segment)
        
        # 一意のsXフォーマットのIDを持つセグメントリストを返す
        return json.dumps({"segments": segments}, ensure_ascii=False)
    except Exception as e:
        logging.error(f"セグメント抽出エラー: {str(e)}\n{traceback.format_exc()}")
        # エラー時は元のテキストを返す
        return text


async def extract_reference_products(text: str) -> str:
    """参照製品情報を抽出します。

    Args:
        text: 参照製品情報のテキスト

    Returns:
        抽出された参照製品情報
    """
    return text


async def extract_value_comparison(text: str) -> str:
    """価値比較情報を抽出します。

    Args:
        text: 価値比較情報のテキスト

    Returns:
        抽出された価値比較情報
    """
    return text


async def extract_formula_design(text: str) -> str:
    """フォーミュラ設計情報を抽出します。

    Args:
        text: フォーミュラ設計情報のテキスト

    Returns:
        抽出されたフォーミュラ設計情報
    """
    return text


async def extract_evc_calculation(text: str) -> str:
    """EVC計算情報を抽出します。

    Args:
        text: EVC計算情報のテキスト

    Returns:
        抽出されたEVC計算情報
    """
    return text


async def extract_market_potential(text: str) -> str:
    """市場ポテンシャル分析情報を抽出します。

    Args:
        text: 市場ポテンシャル分析情報のテキスト

    Returns:
        抽出された市場ポテンシャル分析情報
    """
    return text


async def extract_priority_evaluation(text: str) -> str:
    """優先度評価情報を抽出します。

    Args:
        text: 優先度評価情報のテキスト

    Returns:
        抽出された優先度評価情報
    """
    return text


async def integrate_evc_and_market_potential(evc_data: str, market_data: str) -> str:
    """EVCデータと市場ポテンシャルデータを統合します。

    Args:
        evc_data: EVCデータ
        market_data: 市場ポテンシャルデータ

    Returns:
        統合されたデータ
    """
    # 両方のデータが利用可能かチェック
    if not evc_data or not market_data:
        return "統合結果はありません"

    try:
        # 両方のデータが文字列の場合、統合を試みる
        if isinstance(evc_data, str) and isinstance(market_data, str):
            try:
                # JSONとしてパースを試みる
                evc_json = json.loads(evc_data)
                market_json = json.loads(market_data)

                # 統合データを作成
                integrated_data = {
                    "economic_value": evc_json,
                    "market_potential": market_json
                }

                return json.dumps(integrated_data, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                # JSONデコードに失敗した場合はテキスト統合を試みる
                return extract_data_from_text(evc_data, market_data)

        # 少なくとも1つが辞書の場合
        if isinstance(evc_data, dict) or isinstance(market_data, dict):
            evc_dict = evc_data if isinstance(evc_data, dict) else {"text": evc_data}
            market_dict = market_data if isinstance(market_data, dict) else {"text": market_data}

            # 統合データを作成
            integrated_data = {
                "economic_value": evc_dict,
                "market_potential": market_dict
            }

            return json.dumps(integrated_data, ensure_ascii=False, indent=2)

        # その他の場合はシンプルな文字列結合
        return f"EVC:\n{evc_data}\n\n市場ポテンシャル:\n{market_data}"

    except Exception as e:
        # エラーハンドリング
        error_msg = f"データ統合中にエラーが発生しました: {str(e)}"
        print(error_msg)
        return error_msg


def extract_data_from_text(evc_text: str, market_text: str) -> str:
    """テキストデータから構造化データを抽出します。

    Args:
        evc_text: EVCテキストデータ
        market_text: 市場ポテンシャルテキストデータ

    Returns:
        統合された構造化データ
    """
    # EVC情報の抽出
    evc_segments = {}
    evc_pattern = r"(?:セグメント|Segment)\s*(\d+)[^:]*?:\s*([0-9,.]+)"
    evc_matches = re.finditer(evc_pattern, evc_text, re.IGNORECASE)

    for match in evc_matches:
        segment_id = match.group(1)
        evc_value = match.group(2).replace(',', '')
        try:
            evc_segments[f"segment_{segment_id}"] = float(evc_value)
        except ValueError:
            evc_segments[f"segment_{segment_id}"] = evc_value

    # 市場ポテンシャル情報の抽出
    market_segments = {}
    market_pattern = r"(?:セグメント|Segment)\s*(\d+)[^:]*?:\s*([0-9,.]+)(?:\s*[万億兆]*人|\s*社|\s*組織)*"
    market_matches = re.finditer(market_pattern, market_text, re.IGNORECASE)

    for match in market_matches:
        segment_id = match.group(1)
        market_value = match.group(2).replace(',', '')
        try:
            market_segments[f"segment_{segment_id}"] = float(market_value)
        except ValueError:
            market_segments[f"segment_{segment_id}"] = market_value

    # 統合データを作成
    integrated_data = {
        "economic_value": evc_segments if evc_segments else {"text": evc_text},
        "market_potential": market_segments if market_segments else {"text": market_text}
    }

    return json.dumps(integrated_data, ensure_ascii=False, indent=2)


def get_segmentation_workflow():
    """セグメンテーションワークフローを取得します。

    Returns:
        セグメンテーションワークフローのインスタンス
    """
    return SegmentationWorkflow()


class SegmentationWorkflow:
    """顧客セグメンテーションと市場優先度評価のワークフローを管理するクラスです。"""

    def __init__(self):
        """SegmentationWorkflowクラスのコンストラクタ"""
        self.service_analysis_agent = get_service_analysis_agent()
        self.customer_segment_agent = get_customer_segment_agent()
        self.reference_product_agent = get_reference_product_agent()
        self.value_comparison_agent = get_value_comparison_agent()
        self.formula_design_agent = get_formula_design_agent()
        self.evc_calculation_agent = get_evc_calculation_agent()
        self.market_potential_agent = get_market_potential_agent()
        self.priority_evaluation_agent = get_priority_evaluation_agent()
        self.logger = logging.getLogger(__name__)

    async def _run_agent(self, agent, message: str, shared_context=None) -> Dict[str, Any]:
        """
        エージェントを実行するためのヘルパーメソッド

        公式ドキュメントに基づくシンプルな実装です。
        グローバルトレーサーを使用して、すべてのエージェント呼び出しが同じトレースに記録されます。

        Args:
            agent: 実行するエージェント
            message: エージェントに送信するメッセージ
            shared_context: 共有コンテキスト（オプション）
            
        Returns:
            エージェントからのレスポンス
        """
        # コンテキストがない場合は空の辞書を使用
        context_data = shared_context or {}
            
        try:
            # シンプルなAPI呼び出し
            self.logger.info(f"エージェント {agent.__class__.__name__} を実行します")
            result = await call_agent(agent, message, context_data)
            
            # 結果がない場合のフォールバック処理
            if result is None:
                self.logger.warning("エージェントからの応答がありません。デフォルト値を使用します。")
                return {"result": "エージェントからの応答を取得できませんでした"}

            return result

        except Exception as e:
            self.logger.error(f"エージェント実行中にエラーが発生しました: {e}")
            traceback.print_exc()
            # 例外が発生してもクラッシュせず、エラー情報を返す
            return {"error": str(e), "result": "エージェントの実行中にエラーが発生しました"}

    async def run_workflow(self, service_description: str, market_data: str) -> Dict[str, Any]:
        """ワークフローを実行します。

        Args:
            service_description: サービス説明
            market_data: 市場データ

        Returns:
            ワークフロー実行結果
        """
        # 初期化
        workflow_id = f"workflow-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        results = {
            "workflow_id": workflow_id,
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }
        
        # 共有コンテキストの初期化
        shared_context = {
            "workflow_id": workflow_id,
            "service_description": service_description,
            "market_data": market_data
        }
        
        # OpenAI Agents SDKの標準形式のトレースIDを生成
        if gen_trace_id:
            # 標準関数を使用してトレースIDを生成
            trace_id = gen_trace_id()
        else:
            # 代替手段として型に合ったトレースIDを生成
            trace_id = f"trace_{uuid.uuid4().hex}"
            
        # トレース情報を共有コンテキストに設定
        shared_context["trace_id"] = trace_id
        shared_context["workflow_name"] = "NexaSales顧客セグメンテーションワークフロー"
        
        self.logger.info(f"統一トレースIDを生成しました: {trace_id}")
        
        try:
            # ステップ1: サービス分析
            self.logger.info("サービス分析を開始します")
            service_analysis_result = await self._run_agent(self.service_analysis_agent, service_description, shared_context)
            results["service_analysis"] = service_analysis_result
            
            if service_analysis_result.get("error"):
                self.logger.error(f"サービス分析でエラーが発生しました: {service_analysis_result['error']}")
                results["error"] = service_analysis_result["error"]
                results["status"] = "failed"
                results["completed_at"] = datetime.now().isoformat()
                return results

            # ステップ2: 顧客セグメント抽出
            self.logger.info("顧客セグメント抽出を開始します")
            customer_segment_message = f"# サービス分析結果\n{json.dumps(service_analysis_result, indent=2, ensure_ascii=False)}\n\n# 市場データ\n{market_data}"
            customer_segments = await self._run_agent(self.customer_segment_agent, customer_segment_message, shared_context)
            results["customer_segments"] = customer_segments

            if customer_segments.get("error"):
                self.logger.error(f"顧客セグメント抽出でエラーが発生しました: {customer_segments['error']}")
                results["error"] = customer_segments["error"]
                results["status"] = "failed"
                results["completed_at"] = datetime.now().isoformat()
                return results

            # ステップ3: 参照製品の特定
            self.logger.info("参照製品の特定を開始します")
            reference_product_message = f"# サービス分析結果\n{json.dumps(service_analysis_result, indent=2, ensure_ascii=False)}\n\n# 顧客セグメント\n{json.dumps(customer_segments, indent=2, ensure_ascii=False)}"
            reference_products = await self._run_agent(self.reference_product_agent, reference_product_message, shared_context)
            results["reference_products"] = reference_products

            if reference_products.get("error"):
                self.logger.error(f"参照製品の特定でエラーが発生しました: {reference_products['error']}")
                results["error"] = reference_products["error"]
                results["status"] = "failed"
                results["completed_at"] = datetime.now().isoformat()
                return results

            # ステップ4: 価値比較
            self.logger.info("価値比較を開始します")
            value_comparison_message = f"# サービス分析結果\n{json.dumps(service_analysis_result, indent=2, ensure_ascii=False)}\n\n# 参照製品\n{json.dumps(reference_products, indent=2, ensure_ascii=False)}"
            value_comparisons = await self._run_agent(self.value_comparison_agent, value_comparison_message, shared_context)
            results["value_comparisons"] = value_comparisons

            if value_comparisons.get("error"):
                self.logger.error(f"価値比較でエラーが発生しました: {value_comparisons['error']}")
                results["error"] = value_comparisons["error"]
                results["status"] = "failed"
                results["completed_at"] = datetime.now().isoformat()
                return results

            # ステップ5: 計算式設計
            self.logger.info("計算式設計を開始します")
            formula_design_message = f"# 価値比較\n{json.dumps(value_comparisons, indent=2, ensure_ascii=False)}\n\n# 顧客セグメント\n{json.dumps(customer_segments, indent=2, ensure_ascii=False)}"
            formula_designs = await self._run_agent(self.formula_design_agent, formula_design_message, shared_context)
            results["formula_designs"] = formula_designs

            if formula_designs.get("error"):
                self.logger.error(f"計算式設計でエラーが発生しました: {formula_designs['error']}")
                results["error"] = formula_designs["error"]
                results["status"] = "failed"
                results["completed_at"] = datetime.now().isoformat()
                return results

            # ステップ6: EVC計算
            self.logger.info("EVC計算を開始します")
            evc_calculation_message = f"# 計算式設計\n{json.dumps(formula_designs, indent=2, ensure_ascii=False)}\n\n# 顧客セグメント\n{json.dumps(customer_segments, indent=2, ensure_ascii=False)}"
            evc_calculations = await self._run_agent(self.evc_calculation_agent, evc_calculation_message, shared_context)
            results["evc_calculations"] = evc_calculations

            if evc_calculations.get("error"):
                self.logger.error(f"EVC計算でエラーが発生しました: {evc_calculations['error']}")
                results["error"] = evc_calculations["error"]
                results["status"] = "failed"
                results["completed_at"] = datetime.now().isoformat()
                return results

            # ステップ7: 市場ポテンシャル分析
            self.logger.info("市場ポテンシャル分析を開始します")
            market_potential_message = f"# EVC計算結果\n{json.dumps(evc_calculations, indent=2, ensure_ascii=False)}\n\n# 顧客セグメント\n{json.dumps(customer_segments, indent=2, ensure_ascii=False)}\n\n# 市場データ\n{market_data}"
            market_potentials = await self._run_agent(self.market_potential_agent, market_potential_message, shared_context)
            results["market_potentials"] = market_potentials

            if market_potentials.get("error"):
                self.logger.error(f"市場ポテンシャル分析でエラーが発生しました: {market_potentials['error']}")
                results["error"] = market_potentials["error"]
                results["status"] = "failed"
                results["completed_at"] = datetime.now().isoformat()
                return results

            # ステップ8: 優先度評価
            self.logger.info("優先度評価を開始します")
            priority_evaluation_message = f"# 市場ポテンシャル分析\n{json.dumps(market_potentials, indent=2, ensure_ascii=False)}\n\n# EVC計算結果\n{json.dumps(evc_calculations, indent=2, ensure_ascii=False)}"
            priority_evaluations = await self._run_agent(self.priority_evaluation_agent, priority_evaluation_message, shared_context)
            results["priority_evaluations"] = priority_evaluations

            if priority_evaluations.get("error"):
                self.logger.error(f"優先度評価でエラーが発生しました: {priority_evaluations['error']}")
                results["error"] = priority_evaluations["error"]
                results["status"] = "failed"
                results["completed_at"] = datetime.now().isoformat()
                return results
            self.logger.info("優先度評価が完了しました")

            # 正常完了
            results["status"] = "success"
            results["completed_at"] = datetime.now().isoformat()

            self.logger.info("顧客セグメンテーションと市場優先度評価ワークフローが完了しました")
            
            # 実行完了ログ
            self.logger.info("すべてのエージェント呼び出しが完了しました")
                
            # トレースIDを結果に含める
            results["trace_id"] = trace_id
            return results
        
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"ワークフロー実行中にエラーが発生しました: {error_msg}")
            self.logger.error(traceback.format_exc())
            
            # エラー情報を返す
            results["error"] = error_msg
            results["status"] = "failed"
            results["completed_at"] = datetime.now().isoformat()
            results["trace_id"] = trace_id
            return results
