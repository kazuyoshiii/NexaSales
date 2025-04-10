"""
優先度評価エージェント（パート2）

このモジュールでは、優先度評価エージェントの残りの関数とエージェント定義を提供します。
"""

from typing import Dict, Any, List
# OpenAI Agents SDK
from agents import Agent, function_tool


@function_tool
async def create_action_plan(segment_strategies: List[str]) -> str:
    """セグメント戦略に基づいて行動計画を作成します。

    Args:
        segment_strategies: セグメント戦略のリスト

    Returns:
        行動計画
    """
    import json
    import logging
    
    # セグメント戦略の解析
    processed_segment_strategies = []
    try:
        if isinstance(segment_strategies, str):
            try:
                if segment_strategies.strip().startswith('{') and segment_strategies.strip().endswith('}'): 
                    try:
                        strategies_data = json.loads(segment_strategies)
                        # セグメント戦略がキー「segment_strategies」の下にある場合
                        if "segment_strategies" in strategies_data:
                            processed_segment_strategies = strategies_data["segment_strategies"]
                        else:
                            processed_segment_strategies = [strategies_data]
                    except json.JSONDecodeError:
                        try:
                            # シングルクォートをダブルクォートに変換するなどの修正を試みる
                            fixed_json = segment_strategies.replace("'", "\"").replace("\n", " ")
                            strategies_data = json.loads(fixed_json)
                            if "segment_strategies" in strategies_data:
                                processed_segment_strategies = strategies_data["segment_strategies"]
                            else:
                                processed_segment_strategies = [strategies_data]
                        except:
                            logging.error(f"セグメント戦略のパースに失敗しました。")
                            processed_segment_strategies = []
                else:
                    # 辞書リストの場合はそのまま使用
                    if isinstance(segment_strategies, list):
                        processed_segment_strategies = segment_strategies
                    else:
                        logging.warning(f"セグメント戦略がJSON形式ではありません。")
                        processed_segment_strategies = []
            except Exception as e:
                logging.error(f"セグメント戦略の処理中にエラーが発生しました: {str(e)}")
                processed_segment_strategies = []
        elif isinstance(segment_strategies, dict):
            if "segment_strategies" in segment_strategies:
                processed_segment_strategies = segment_strategies["segment_strategies"]
            else:
                processed_segment_strategies = [segment_strategies]
        elif isinstance(segment_strategies, list):
            processed_segment_strategies = segment_strategies
        else:
            logging.error(f"セグメント戦略の型が不正です: {type(segment_strategies)}")
            processed_segment_strategies = []
    except Exception as e:
        logging.error(f"セグメント戦略の処理中にエラーが発生しました: {str(e)}")
        processed_segment_strategies = []
    # 優先度ランク別の行動計画テンプレート
    action_plan_templates = {
        "最優先": {
            "immediate_actions": [
                "専任営業チームの編成（1週間以内）",
                "カスタマイズされた提案資料の作成（2週間以内）",
                "トップ企業リストの作成（1週間以内）",
                "初回アプローチ計画の策定（2週間以内）"
            ],
            "short_term_actions": [
                "トップマネジメントへの直接アプローチ開始（1ヶ月以内）",
                "業界イベントでのプロモーション計画策定（1ヶ月以内）",
                "初回商談の実施（1-2ヶ月以内）",
                "フィードバックの収集と提案の改善（2-3ヶ月以内）"
            ],
            "mid_term_actions": [
                "成約率向上のための戦略見直し（3ヶ月ごと）",
                "成功事例の作成と共有（6ヶ月以内）",
                "アップセル・クロスセル戦略の策定（6ヶ月以内）"
            ],
            "kpis": [
                "初回商談実施数：月間10件",
                "提案書提出数：月間5件",
                "成約数：四半期5件",
                "平均成約額：1,500万円"
            ]
        },
        "高優先": {
            "immediate_actions": [
                "専門営業担当者のアサイン（2週間以内）",
                "セグメント特化型マーケティング資料の作成（3週間以内）",
                "ターゲット企業リストの作成（2週間以内）"
            ],
            "short_term_actions": [
                "業界セミナーの企画（1-2ヶ月以内）",
                "既存顧客からの紹介プログラムの開始（1-2ヶ月以内）",
                "初回アプローチの開始（1ヶ月以内）"
            ],
            "mid_term_actions": [
                "セミナー実施と見込み客の獲得（3-4ヶ月以内）",
                "成功事例の作成（6ヶ月以内）",
                "アプローチ方法の見直し（四半期ごと）"
            ],
            "kpis": [
                "初回商談実施数：月間5件",
                "提案書提出数：月間3件",
                "成約数：四半期3件",
                "平均成約額：1,000万円"
            ]
        },
        "中優先": {
            "immediate_actions": [
                "標準的な営業プロセスの準備（1ヶ月以内）",
                "デジタルマーケティング施策の計画（1ヶ月以内）"
            ],
            "short_term_actions": [
                "デジタルマーケティングの開始（2-3ヶ月以内）",
                "パートナー企業との協業計画の策定（2-3ヶ月以内）",
                "成功事例の収集（3-4ヶ月以内）"
            ],
            "mid_term_actions": [
                "パートナー企業との協業開始（4-6ヶ月以内）",
                "成功事例の共有開始（6ヶ月以内）",
                "アプローチ方法の効果測定と改善（半年ごと）"
            ],
            "kpis": [
                "マーケティングリード獲得数：月間10件",
                "初回商談実施数：月間3件",
                "成約数：四半期2件",
                "平均成約額：500万円"
            ]
        },
        "低優先": {
            "immediate_actions": [
                "インバウンドマーケティング施策の計画（2ヶ月以内）",
                "セルフサービス型導入プロセスの準備（2ヶ月以内）"
            ],
            "short_term_actions": [
                "オンラインセミナーの企画（3-4ヶ月以内）",
                "自動化されたフォローアップの設定（3-4ヶ月以内）"
            ],
            "mid_term_actions": [
                "オンラインセミナーの実施（6ヶ月以内）",
                "インバウンドマーケティングの効果測定と改善（半年ごと）"
            ],
            "kpis": [
                "ウェブサイト訪問数：月間100件",
                "資料ダウンロード数：月間20件",
                "問い合わせ数：月間5件",
                "成約数：四半期1件",
                "平均成約額：300万円"
            ]
        },
        "最低優先": {
            "immediate_actions": [
                "標準製品の提供準備（3ヶ月以内）",
                "セルフサービスポータルの準備（3ヶ月以内）"
            ],
            "short_term_actions": [
                "自動化されたマーケティングの設定（6ヶ月以内）",
                "パートナー企業への委託計画の策定（6ヶ月以内）"
            ],
            "mid_term_actions": [
                "パートナー企業への委託開始（9-12ヶ月以内）",
                "効果測定と改善（年1回）"
            ],
            "kpis": [
                "資料ダウンロード数：月間10件",
                "問い合わせ数：月間2件",
                "成約数：半年1件",
                "平均成約額：100万円"
            ]
        }
    }
    
    # セグメント別の行動計画を作成
    segment_action_plans = []
    segment_recommendations = []
    
    for strategy in processed_segment_strategies:
        segment_id = strategy.get("segment_id")
        segment_name = strategy.get("segment_name")
        priority_rank = strategy.get("priority_rank")
        
        # 優先度ランクに基づく行動計画テンプレートの取得
        template = action_plan_templates.get(priority_rank, action_plan_templates["最低優先"])
        
        # セグメント固有の行動の生成
        if segment_id == "s1":  # 大企業・高価値
            specific_immediate_actions = [
                "AIを活用した高精度な売上予測機能のデモ準備（2週間以内）",
                "エンタープライズ統合機能の事例集作成（2週間以内）",
                "セキュリティ機能の説明資料作成（1週間以内）",
                "トップマネジメント向けエグゼクティブブリーフィングの準備（2週間以内）"
            ]
            specific_kpis = [
                "エグゼクティブブリーフィング実施数：月間2件",
                "PoC実施数：四半期2件",
                "大規模導入案件成約数：半年2件"
            ]
        elif segment_id == "s2":  # 大企業・低価値
            specific_immediate_actions = [
                "コスト最適化価値の数値化資料作成（2週間以内）",
                "既存システム統合事例の収集（2週間以内）",
                "段階的導入プランのテンプレート作成（1週間以内）"
            ]
            specific_kpis = [
                "コスト削減効果提示数：月間3件",
                "既存システム統合提案数：月間2件",
                "段階的導入提案採用率：50%"
            ]
        elif segment_id == "s3":  # 中小企業・高価値
            specific_immediate_actions = [
                "成長支援機能のデモ準備（2週間以内）",
                "コストパフォーマンス比較資料作成（1週間以内）",
                "短期導入事例の収集（2週間以内）"
            ]
            specific_kpis = [
                "成長企業向けセミナー参加者数：月間20名",
                "トライアル開始数：月間5件",
                "トライアルからの成約率：40%"
            ]
        elif segment_id == "s4":  # 中小企業・低価値
            specific_immediate_actions = [
                "低価格プランの詳細設計（2週間以内）",
                "セルフサービス型導入ガイドの作成（2週間以内）",
                "オンラインサポート体制の整備（1週間以内）"
            ]
            specific_kpis = [
                "低価格プラン問い合わせ数：月間10件",
                "セルフサービス導入完了率：30%",
                "サポート満足度：80%以上"
            ]
        else:
            specific_immediate_actions = template["immediate_actions"]
            specific_kpis = template["kpis"]
        
        # 行動計画の作成
        action_plan = {
            "segment_id": segment_id,
            "segment_name": segment_name,
            "priority_rank": priority_rank,
            "immediate_actions": specific_immediate_actions,
            "short_term_actions": template["short_term_actions"],
            "mid_term_actions": template["mid_term_actions"],
            "kpis": specific_kpis + [kpi for kpi in template["kpis"] if kpi not in specific_kpis]
        }
        recommendation = {
            "segment_id": segment_id,
            "segment_name": segment_name,
            "priority_rank": priority_rank,
            "immediate_actions": specific_immediate_actions,
            "short_term_actions": template["short_term_actions"],
            "mid_term_actions": template["mid_term_actions"],
            "kpis": specific_kpis + [kpi for kpi in template["kpis"] if kpi not in specific_kpis]
        }
        
        segment_action_plans.append(action_plan)
        segment_recommendations.append(recommendation)
    
    # 全体の行動計画
    overall_action_plan = {
        "highest_priority_segments": [
            plan for plan in segment_action_plans 
            if plan["priority_rank"] in ["最優先", "高優先"]
        ],
        "immediate_focus_areas": [
            "最優先セグメントへの専任チーム編成と集中的アプローチ",
            "高優先セグメント向けのマーケティング資料と営業プロセスの整備",
            "全セグメントのターゲット企業リストの作成と優先順位付け"
        ],
        "resource_allocation_guidelines": {
            "sales_resources": {
                "最優先セグメント": "40%",
                "高優先セグメント": "30%",
                "中優先セグメント": "20%",
                "低優先セグメント": "10%",
                "最低優先セグメント": "0%"
            },
            "marketing_resources": {
                "最優先セグメント": "30%",
                "高優先セグメント": "30%",
                "中優先セグメント": "20%",
                "低優先セグメント": "15%",
                "最低優先セグメント": "5%"
            },
            "product_development_resources": {
                "最優先セグメント": "35%",
                "高優先セグメント": "25%",
                "中優先セグメント": "20%",
                "低優先セグメント": "15%",
                "最低優先セグメント": "5%"
            }
        },
        "quarterly_review_points": [
            "セグメント別KPI達成状況の評価",
            "市場環境の変化の分析",
            "競合状況の変化の分析",
            "優先度ランクの見直し",
            "リソース配分の調整"
        ]
    }
    
    # 行動計画情報の追加
    if isinstance(segment_recommendations, list):
        for recommendation in segment_recommendations:
            segment_id = recommendation.get("segment_id")
            for plan in segment_action_plans:
                if plan.get("segment_id") == segment_id:
                    recommendation["immediate_actions"] = plan.get("immediate_actions", [])
                    recommendation["short_term_actions"] = plan.get("short_term_actions", [])
                    recommendation["mid_term_actions"] = plan.get("mid_term_actions", [])
                    recommendation["kpis"] = plan.get("kpis", [])
    
    return str({
        "segment_action_plans": segment_action_plans,
        "segment_recommendations": segment_recommendations,
        "overall_action_plan": overall_action_plan
    })


@function_tool
async def create_priority_report(
    integrated_results: str,
    priority_scores: str,
    segment_strategies: str,
    action_plans: str
) -> str:
    """優先度評価レポートを作成します。

    Args:
        integrated_results: 統合結果
        priority_scores: 優先度スコア計算結果
        segment_strategies: セグメント戦略
        action_plans: 行動計画

    Returns:
        優先度評価レポート
    """
    import json
    import logging
    
    # 各データの処理と解析
    try:
        # 統合結果の解析
        if isinstance(integrated_results, str):
            try:
                integrated_data = json.loads(integrated_results.replace("'", "\""))
                if "integrated_results" in integrated_data:
                    processed_integrated_results = integrated_data["integrated_results"]
                else:
                    processed_integrated_results = integrated_data
            except:
                logging.warning("統合結果の解析に失敗しました。")
                processed_integrated_results = {}
        elif isinstance(integrated_results, dict):
            processed_integrated_results = integrated_results
        else:
            processed_integrated_results = {}
            
        # 優先度スコアの解析
        if isinstance(priority_scores, str):
            try:
                scores_data = json.loads(priority_scores.replace("'", "\""))
                if "priority_scores" in scores_data:
                    processed_priority_scores = scores_data["priority_scores"]
                else:
                    processed_priority_scores = scores_data
            except:
                logging.warning("優先度スコアの解析に失敗しました。")
                processed_priority_scores = []
        elif isinstance(priority_scores, dict):
            if "priority_scores" in priority_scores:
                processed_priority_scores = priority_scores["priority_scores"]
            else:
                processed_priority_scores = priority_scores
        elif isinstance(priority_scores, list):
            processed_priority_scores = priority_scores
        else:
            processed_priority_scores = []
            
        # セグメント戦略の解析
        if isinstance(segment_strategies, str):
            try:
                strategies_data = json.loads(segment_strategies.replace("'", "\""))
                if "segment_strategies" in strategies_data:
                    processed_segment_strategies = strategies_data["segment_strategies"]
                else:
                    processed_segment_strategies = strategies_data
            except:
                logging.warning("セグメント戦略の解析に失敗しました。")
                processed_segment_strategies = []
        elif isinstance(segment_strategies, dict):
            if "segment_strategies" in segment_strategies:
                processed_segment_strategies = segment_strategies["segment_strategies"]
            else:
                processed_segment_strategies = segment_strategies
        elif isinstance(segment_strategies, list):
            processed_segment_strategies = segment_strategies
        else:
            processed_segment_strategies = []
            
        # 行動計画の解析
        if isinstance(action_plans, str):
            try:
                plans_data = json.loads(action_plans.replace("'", "\""))
                if "action_plans" in plans_data:
                    processed_action_plans = plans_data["action_plans"]
                else:
                    processed_action_plans = plans_data
            except:
                logging.warning("行動計画の解析に失敗しました。")
                processed_action_plans = []
        elif isinstance(action_plans, dict):
            if "action_plans" in action_plans:
                processed_action_plans = action_plans["action_plans"]
            else:
                processed_action_plans = action_plans
        elif isinstance(action_plans, list):
            processed_action_plans = action_plans
        else:
            processed_action_plans = []
    except Exception as e:
        logging.error(f"データの処理中にエラーが発生しました: {str(e)}")
        processed_integrated_results = {}
        processed_priority_scores = []
        processed_segment_strategies = []
        processed_action_plans = []
    # 処理済みデータの活用
    # セグメント情報を取得
    if isinstance(processed_integrated_results, dict):
        segments = processed_integrated_results.get("integrated_results", [])
    elif isinstance(processed_integrated_results, list):
        segments = processed_integrated_results
    else:
        segments = []
    
    # 優先度スコアを使用
    scores = processed_priority_scores if processed_priority_scores else []
    
    # セグメント戦略を使用
    strategies = processed_segment_strategies if processed_segment_strategies else []
    
    # 行動計画を使用
    plans = processed_action_plans if processed_action_plans else []
    if isinstance(processed_action_plans, dict):
        overall_action_plan = processed_action_plans.get("overall_action_plan", {})
    else:
        overall_action_plan = {}
    
    # セグメント戦略情報の追加
    if isinstance(strategies, list):
        for strategy in strategies:
            segment_id = strategy.get("segment_id")
            for score in scores:
                if score.get("segment_id") == segment_id:
                    score["strategy"] = strategy.get("approach", "")
                    score["resource_allocation"] = strategy.get("resource_allocation", "")
                    score["key_tactics"] = strategy.get("key_tactics", [])
    
    # 優先度評価レポートの作成
    report = {
        "title": "顧客セグメント優先度評価レポート",
        "summary": {
            "total_segments": len(segments),
            "priority_distribution": {
                "最優先": len([s for s in scores if s.get("priority_rank") == "最優先"]),
                "高優先": len([s for s in scores if s.get("priority_rank") == "高優先"]),
                "中優先": len([s for s in scores if s.get("priority_rank") == "中優先"]),
                "低優先": len([s for s in scores if s.get("priority_rank") == "低優先"]),
                "最低優先": len([s for s in scores if s.get("priority_rank") == "最低優先"])
            },
            "top_priority_segments": [
                {
                    "segment_id": s.get("segment_id"),
                    "segment_name": s.get("segment_name"),
                    "priority_score": s.get("priority_score"),
                    "priority_rank": s.get("priority_rank")
                }
                # 上位2つのセグメントを取得
                for s in (scores[:2] if len(scores) >= 2 else scores)
            ]
        },
        "segment_evaluations": [
            {
                "segment_id": score.get("segment_id"),
                "segment_name": score.get("segment_name"),
                "priority_score": score.get("priority_score"),
                "priority_rank": score.get("priority_rank"),
                "score_components": score.get("score_components", {}),
                "strategy": score.get("strategy", ""),
                "resource_allocation": score.get("resource_allocation", ""),
                "key_tactics": score.get("key_tactics", []),
                "action_plan": next(
                    (p for p in plans if p.get("segment_id") == score.get("segment_id")),
                    {}
                )
            }
            for score in scores
        ],
        "overall_strategy": {
            "resource_allocation": overall_action_plan.get("resource_allocation_guidelines", {}),
            "immediate_focus_areas": overall_action_plan.get("immediate_focus_areas", []),
            "quarterly_review_points": overall_action_plan.get("quarterly_review_points", [])
        },
        "key_insights": [
            "最優先セグメントである「大企業・高価値」は、高いEVC値と比較的高い獲得確率により、最も高い優先度スコアを獲得しています。",
            "「中小企業・高価値」セグメントは、高い成長率と強い競争優位性により、「高優先」ランクとなっています。",
            "「大企業・低価値」セグメントは、大きな市場規模を持ちますが、低い獲得確率により「中優先」ランクとなっています。",
            "「中小企業・低価値」セグメントは、すべての指標で低いスコアとなり、「最低優先」ランクとなっています。",
            "リソース配分は最優先および高優先セグメントに集中させ、低優先および最低優先セグメントには効率的なアプローチを採用することが推奨されます。"
        ],
        "recommendations": [
            "最優先セグメントには専任営業チームを編成し、トップマネジメントへの直接アプローチを行うことで、高いEVC値を持つ案件の獲得を目指します。",
            "高優先セグメントには成長支援機能を強調し、コストパフォーマンスの高さを訴求することで、成長企業の獲得を目指します。",
            "中優先セグメントにはコスト最適化価値を明確に示し、既存システムとの統合の容易さを強調することで、大企業の低価値セグメントの獲得を目指します。",
            "低優先および最低優先セグメントには、デジタルマーケティングとセルフサービス型の導入プロセスを活用し、最小限のリソースで効率的にアプローチします。",
            "四半期ごとに優先度評価を見直し、市場環境や競合状況の変化に応じて戦略とリソース配分を調整します。"
        ]
    }
    
    return str(report)
