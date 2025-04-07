# 顧客セグメンテーションと市場優先度評価フレームワーク

本ドキュメントでは、新サービスの顧客セグメンテーション戦略と市場優先度評価フレームワークを定義します。EVCの定量化と市場ポテンシャルを組み合わせることで、より効果的な営業戦略を策定します。

## ユースケース：営業本部長の課題解決

### 課題を抱える人物
営業本部長の田中氏（45歳）は、新サービス「NexaSales」の市場投入を控え、限られた営業リソースをどの顧客セグメントに集中すべきか判断に迷っています。

### 抱えている課題
1. リソース配分の最適化: 100名の営業部隊をどのセグメントに何人配置すべきか
2. 投資対効果の最大化: 営業活動の費用対効果を最大化する顧客ターゲティング
3. 短期・中長期のバランス: 短期的な売上と中長期的な市場シェア拡大のバランス
4. 定量的根拠の不足: 「この顧客が最も価値が高い」という主張の裏付けデータがない
5. セグメント間の優先順位: 大企業と中小企業のどちらを優先すべきか判断基準がない

### 解決方法
本フレームワークは以下の方法で田中氏の課題を解決します：

1. EVCと市場規模の両面評価: 単純な顧客単価だけでなく、市場規模と獲得確率を加味した総合評価
2. セグメント別の具体的戦略: 各セグメントに対する最適なアプローチ方法の明確化
3. リソース配分の数値化: 各セグメントへの営業リソース配分比率の具体的提案
4. 定量的な優先順位付け: 「セグメント優先度 = EVC × 企業数 × 獲得確率」による客観的評価
5. 実行可能なアクションプラン: 各セグメントへの具体的なアプローチ方法と価値訴求ポイント

### 期待される成果
- 営業リソースの最適配分による売上最大化（前年比130%）
- 営業コスト効率の20%向上
- 顧客獲得コストの15%削減
- 戦略的意思決定の迅速化（判断時間50%短縮）
- データに基づく営業戦略の社内浸透


## 1. セグメンテーションの基本軸

顧客セグメンテーションは以下の2軸で整理します：

1. 価値創出ポテンシャル：サービスが顧客にもたらす潜在的な価値の大きさ
2. 実現容易性：その価値を実際に顧客が享受できるようになるまでの障壁の低さ

## 2. 4つの顧客セグメント

```
価値創出ポテンシャル
    ↑
    │
高  │  高価値・高障壁   高価値・低障壁
    │  (高価値・    (高価値・
    │   高障壁)      低障壁)
    │
    │----------------------------→ 実現容易性
    │
低  │  低価値・高障壁   低価値・低障壁
    │  (低価値・    (低価値・
    │   高障壁)      低障壁)
    │
    ↓
      低           高
```

- 高価値・低障壁セグメント：高い価値をすぐに実現できる顧客
- 高価値・高障壁セグメント：高い価値だが実現に障壁がある顧客
- 低価値・低障壁セグメント：中程度の価値をすぐに実現できる顧客
- 低価値・高障壁セグメント：現時点では価値も実現も限定的な顧客

## 3. MECE価値分類

顧客に提供する価値は、財務諸表の2大要素に対応する形で分類します：

### 収益向上価値（Revenue Enhancement Value）
- 新規収益（Rn）：新規顧客獲得、新製品売上
- 既存顧客維持による収益（Rr）：解約防止、継続利用
- 価格最適化による収益（Rp）：価格プレミアム設定
- 取引頻度向上による収益（Rt）：クロスセル、アップセル

### コスト最適化価値（Cost Optimization Value）
- 直接コスト削減（Cd）：人件費、運用コスト
- 品質関連コスト削減（Cq）：不良、クレーム対応
- リスク関連コスト削減（Cr）：保険、対策、事故対応
- 時間関連コスト削減（Ct）：意思決定、市場投入時間

## 4. 定量化されたEVC計算式

```
EVC = R + (Re + Co) - I

ここで、
Re = 収益向上価値（円/年）= Rn + Rr + Rp + Rt
Co = コスト最適化価値（円/年）= Cd + Cq + Cr + Ct
R = 参照価格（円/年）
I = 導入コスト（円）
```

## 5. 市場ポテンシャルを加味した優先度評価

単純なEVCだけでは大企業が有利になるため、市場規模と獲得可能性を加味した総合評価が必要です：

```
セグメント優先度 = セグメント別EVC × セグメント企業数 × 獲得確率
```

## 6. エージェントシステム設計

以下は、各セグメントごとにEVCを算出するエージェントシステムの設計です。

### 6.1 エージェントシステムの処理フロー

このエージェントシステムは以下のステップで動作します：

1. サービス分析フェーズ：
   - ServiceAnalysisAgentが内部ドキュメントや公開情報からサービスの機能、ビジネスモデル、提供方法を抽出
   - サービスの特徴、ユニークセリングポイント、機能一覧を含むサービス概要レポートを作成
   - このレポートは後続のすべてのエージェントの基礎情報となる

2. 市場・顧客分析フェーズ（並列処理）：
   - 顧客セグメント抽出：CustomerSegmentExtractionAgentが公開市場調査データ、業界レポート、専門家インタビューに基づいて「価値創出ポテンシャル」と「実現容易性」の2軸でセグメントを分類
   - 各セグメントの市場規模と獲得確率を業界レポートや専門家予測から推定
   - 参照商品特定：ReferenceProductIdentificationAgentがサービス概要レポートと公開市場・競合情報から、対象サービスと競合する参照製品3つを特定
   - 参照商品価値分析：ReferenceProductValueAnalysisAgentが各参照商品について、公開情報、利用者レビュー、製品デモなどから提供価値要因を個別に定量化

3. 価値比較・統合フェーズ：
   - 参照商品の個別価値結果を統合
   - ValueComparisonAgentが各顧客セグメントごとに、参照商品の提供価値要因を整理・比較し、プラス/マイナス評価の比較マトリックスを作成

4. 並列計算フェーズ：
   - EVC計算プロセス：
     - FormulaDesignAgentが比較マトリックスを基に、改良された集約数式 'EVC = R + (Re + Co) - I' に従った、各セグメント用のEVC計算フォーミュラを設計
     - 各価値要因の重み・調整値を決定し、その根拠をログに記録
     - SegmentSpecificEVCCalculationAgentが設計されたフォーミュラに、各セグメント固有のパラメータを投入し、具体的なEVC数値とその内訳を算出
   - 市場ポテンシャル計算プロセス（並列実行）：
     - MarketPotentialAnalysisAgent（新規エージェント）が各セグメントの市場規模を分析
     - 業界レポート、市場調査、専門家予測から各セグメントの企業数を算出
     - 競合状況、市場動向、商品適合性からセグメント別の獲得確率を推定

5. 統合・優先度評価フェーズ：
   - PriorityEvaluationAgent（新規エージェント）がEVC計算結果と市場ポテンシャル分析結果を統合
   - 市場ポテンシャル評価式（セグメント優先度 = セグメント別EVC × セグメント企業数 × 獲得確率）を適用
   - 各セグメントの優先順位を算出し、セグメント間の相対的な重要度を定量化

6. 戦略立案・出力フェーズ：
   - IntegrationAndOutputAgentが全エージェントからの出力を統合
   - セグメント別の具体的アプローチ戦略を立案
   - セグメント優先度に基づく営業リソース配分案を生成
   - 最終的なセグメント優先度レポート、セグメント別アプローチガイド、リソース配分推奨を生成

### 6.2 各エージェントの具体的な役割と入出力

各エージェントは以下の役割を担い、特定の入出力を処理します：

```json
{
  "system_overview": "公開市場情報と内部データに基づき、対象サービスの競合製品を3つ特定し、それぞれの提供価値を定量化する。その後、4つの顧客セグメント（高価値・低障壁、高価値・高障壁、低価値・低障壁、低価値・高障壁）ごとに改良された集約数式 'EVC = R + (Re + Co) - I' によりEVCを算出し、市場ポテンシャルを評価するシステム。",
  "common_aggregation_formula": "EVC = R + (Re + Co) - I",
  "value_components_formulas": {
    "RevenueEnhancement": {
      "final_formula": "Re = Rn + Rr + Rp + Rt",
      "description": "収益向上価値の総和",
      "components": {
        "NewRevenue": {
          "formula": "Rn = NewCustomers  AverageCustomerValue + NewProducts  ProductRevenue",
          "description": "新規顧客獲得と新製品による収益"
        },
        "RetentionRevenue": {
          "formula": "Rr = RetainedCustomers  CustomerLifetimeValue",
          "description": "顧客維持による収益"
        },
        "PricingRevenue": {
          "formula": "Rp = PriceIncrease  CustomerBase",
          "description": "価格最適化による収益"
        },
        "TransactionRevenue": {
          "formula": "Rt = TransactionIncrease  AverageTransactionValue",
          "description": "取引頻度向上による収益"
        }
      }
    },
    "CostOptimization": {
      "final_formula": "Co = Cd + Cq + Cr + Ct",
      "description": "コスト最適化価値の総和",
      "components": {
        "DirectCostReduction": {
          "formula": "Cd = (ManualHours - AutomatedHours)  HourlyRate + ResourceSavings",
          "description": "人件費と運用コスト削減"
        },
        "QualityCostReduction": {
          "formula": "Cq = DefectReduction  DefectCost + ComplaintReduction  ComplaintCost",
          "description": "品質関連コスト削減"
        },
        "RiskCostReduction": {
          "formula": "Cr = RiskReductionFactor  RiskExposureValue",
          "description": "リスク関連コスト削減"
        },
        "TimeCostReduction": {
          "formula": "Ct = DecisionTimeSavings  OpportunityCostRate",
          "description": "時間関連コスト削減"
        }
      }
    }
  },
  "agents": [
    {
      "agent_id": 1,
      "agent_name": "ServiceAnalysisAgent",
      "role": "サービス公式ウェブサイト、公開事例紹介、プレスリリースからサービスの機能、ビジネスモデル、提供方法を抽出し、サービス概要レポートを作成する。",
      "inputs": ["サービス公式ウェブサイト", "公開事例紹介", "プレスリリース"],
      "outputs": ["サービス概要レポート"]
    },
    {
      "agent_id": 2,
      "agent_name": "CustomerSegmentExtractionAgent",
      "role": "競合企業のウェブサイト、サービス紹介ページ、公開事例紹介に基づいて顧客セグメントを抽出する。価値創出ポテンシャルと実現容易性の2軸で4つのセグメント（高価値・低障壁、高価値・高障壁、低価値・低障壁、低価値・高障壁）を生成する。",
      "inputs": ["競合企業のウェブサイト", "サービス紹介ページ", "公開事例紹介"],
      "outputs": ["顧客セグメントリスト (4セグメント)", "セグメント市場規模推定", "獲得確率予測"]
    },
    {
      "agent_id": 3,
      "agent_name": "ReferenceProductIdentificationAgent",
      "role": "サービス概要レポートと競合企業のウェブサイト、サービス紹介ページ、公開事例紹介から、対象サービスと競合する参照製品を3つ特定する。",
      "inputs": ["サービス概要レポート", "競合企業のウェブサイト", "サービス紹介ページ", "公開事例紹介"],
      "outputs": ["参照商品リスト (3製品)"]
    },
    {
      "agent_id": 4,
      "agent_name": "ReferenceProductValueAnalysisAgent",
      "role": "各参照商品について、競合企業のウェブサイト、サービス紹介ページ、公開事例紹介から提供価値要因（収益向上価値とコスト最適化価値）を個別に定量化する。",
      "inputs": ["参照商品リスト", "競合企業のウェブサイト", "サービス紹介ページ", "公開事例紹介"],
      "outputs": ["参照商品の個別提供価値要因リスト"]
    },
    {
      "agent_id": 5,
      "agent_name": "ValueComparisonAgent",
      "role": "各顧客セグメントごとに、参照商品の提供価値要因を整理・比較し、プラス/マイナス評価の比較マトリックスを作成する。",
      "inputs": ["参照商品の個別提供価値要因リスト", "顧客セグメントリスト"],
      "outputs": ["セグメント別比較マトリックス"]
    },
    {
      "agent_id": 6,
      "agent_name": "FormulaDesignAgent",
      "role": "ValueComparisonAgentの結果を基に、改良された集約数式 'EVC = R + (Re + Co) - I' に従った、各セグメント用のEVC計算フォーミュラを設計する。各価値要因の重み・調整値を決定し、その根拠をログに記録する。",
      "inputs": ["セグメント別比較マトリックス", "Reference Price (R)", "Installation Cost (I)"],
      "outputs": ["セグメント別EVC計算フォーミュラ", "重み・調整値ログ"]
    },
    {
      "agent_id": 7,
      "agent_name": "SegmentSpecificEVCCalculationAgent",
      "role": "FormulaDesignAgentで設計された各セグメント用のフォーミュラに、各セグメント固有のパラメータを投入し、具体的なEVC数値とその内訳を算出する。",
      "inputs": ["セグメント別EVC計算フォーミュラ", "各セグメント固有の外部パラメータ推定値"],
      "outputs": ["各セグメントの最終EVC数値", "EVC内訳レポート"],
      "example_calculation": {
        "HighValueLowBarrierSegment": {
          "R": 10000000,
          "Re": {
            "Rn": 18000000,
            "Rr": 1000000,
            "Rp": 2000000,
            "Rt": 5000000,
            "Total": 26000000
          },
          "Co": {
            "Cd": 61200000,
            "Cq": 6100000,
            "Cr": 7200000,
            "Ct": 15000000,
            "Total": 89500000
          },
          "I": 20000000,
          "FinalEVC": 105500000,
          "MarketPotential": {
            "SegmentSize": 200,
            "AcquisitionProbability": 0.3,
            "TotalPotential": 6330000000
          }
        },
        "HighValueHighBarrierSegment": {
          "R": 10000000,
          "Re": {
            "Rn": 12600000,
            "Rr": 1000000,
            "Rp": 2000000,
            "Rt": 2600000,
            "Total": 18200000
          },
          "Co": {
            "Cd": 42840000,
            "Cq": 6100000,
            "Cr": 7200000,
            "Ct": 15460000,
            "Total": 71600000
          },
          "I": 30000000,
          "FinalEVC": 69800000,
          "MarketPotential": {
            "SegmentSize": 500,
            "AcquisitionProbability": 0.2,
            "TotalPotential": 6980000000
          }
        },
        "LowValueLowBarrierSegment": {
          "R": 5000000,
          "Re": {
            "Rn": 5400000,
            "Rr": 300000,
            "Rp": 600000,
            "Rt": 1500000,
            "Total": 7800000
          },
          "Co": {
            "Cd": 12240000,
            "Cq": 1220000,
            "Cr": 1440000,
            "Ct": 3000000,
            "Total": 17900000
          },
          "I": 5000000,
          "FinalEVC": 25700000,
          "MarketPotential": {
            "SegmentSize": 10000,
            "AcquisitionProbability": 0.05,
            "TotalPotential": 12850000000
          }
        },
        "LowValueHighBarrierSegment": {
          "R": 2000000,
          "Re": {
            "Rn": 1800000,
            "Rr": 100000,
            "Rp": 200000,
            "Rt": 500000,
            "Total": 2600000
          },
          "Co": {
            "Cd": 3060000,
            "Cq": 305000,
            "Cr": 360000,
            "Ct": 750000,
            "Total": 4475000
          },
          "I": 3000000,
          "FinalEVC": 6075000,
          "MarketPotential": {
            "SegmentSize": 50000,
            "AcquisitionProbability": 0.01,
            "TotalPotential": 3037500000
          }
        }
      }
    },
    {
      "agent_id": 8,
      "agent_name": "MarketPotentialAnalysisAgent",
      "role": "各セグメントの市場規模と獲得可能性を公開情報から推定し、市場ポテンシャルを定量化する。EVC計算と並行して実行される。",
      "inputs": [
        "競合企業のウェブサイト",
        "サービス紹介ページ",
        "顧客セグメントリスト",
        "公開事例紹介",
        "企業の公開財務情報"
      ],
      "outputs": [
        "セグメント別市場規模データ",
        "セグメント別獲得確率予測",
        "市場動向分析レポート"
      ],
      "example_calculation": {
        "HighValueLowBarrierSegment": {
          "MarketSize": 200,
          "AcquisitionProbability": 0.3,
          "GrowthRate": "5%",
          "CompetitiveIntensity": "Medium",
          "ProductFitScore": 8.5
        },
        "HighValueHighBarrierSegment": {
          "MarketSize": 500,
          "AcquisitionProbability": 0.2,
          "GrowthRate": "8%",
          "CompetitiveIntensity": "High",
          "ProductFitScore": 7.2
        },
        "LowValueLowBarrierSegment": {
          "MarketSize": 10000,
          "AcquisitionProbability": 0.05,
          "GrowthRate": "12%",
          "CompetitiveIntensity": "Low",
          "ProductFitScore": 9.0
        },
        "LowValueHighBarrierSegment": {
          "MarketSize": 50000,
          "AcquisitionProbability": 0.01,
          "GrowthRate": "15%",
          "CompetitiveIntensity": "Very Low",
          "ProductFitScore": 6.5
        }
      }
    },
    {
      "agent_id": 9,
      "agent_name": "PriorityEvaluationAgent",
      "role": "EVC計算結果と市場ポテンシャル分析結果を統合し、セグメント優先度を算出する。市場ポテンシャル評価式（セグメント優先度 = セグメント別EVC × セグメント企業数 × 獲得確率）を適用する。",
      "inputs": [
        "各セグメントの最終EVC数値",
        "セグメント別市場規模データ",
        "セグメント別獲得確率予測"
      ],
      "outputs": [
        "セグメント優先度評価",
        "セグメント間相対重要度",
        "優先順位根拠レポート"
      ],
      "example_calculation": {
        "HighValueLowBarrierSegment": {
          "EVC": 105500000,
          "MarketSize": 200,
          "AcquisitionProbability": 0.3,
          "TotalPotential": 6330000000,
          "RelativeImportance": 0.25,
          "Priority": 3
        },
        "HighValueHighBarrierSegment": {
          "EVC": 69800000,
          "MarketSize": 500,
          "AcquisitionProbability": 0.2,
          "TotalPotential": 6980000000,
          "RelativeImportance": 0.25,
          "Priority": 2
        },
        "LowValueLowBarrierSegment": {
          "EVC": 25700000,
          "MarketSize": 10000,
          "AcquisitionProbability": 0.05,
          "TotalPotential": 12850000000,
          "RelativeImportance": 0.45,
          "Priority": 1
        },
        "LowValueHighBarrierSegment": {
          "EVC": 6075000,
          "MarketSize": 50000,
          "AcquisitionProbability": 0.01,
          "TotalPotential": 3037500000,
          "RelativeImportance": 0.05,
          "Priority": 4
        }
      }
    },
    {
      "agent_id": 10,
      "agent_name": "IntegrationAndOutputAgent",
      "role": "全エージェントからの出力を統合し、セグメント別のアプローチ戦略を立案し、最終的なレポートと実行計画を生成する。",
      "inputs": [
        "サービス概要レポート",
        "顧客セグメントリスト",
        "参照商品リスト",
        "各セグメントのEVC内訳レポート",
        "市場動向分析レポート",
        "セグメント優先度評価",
        "セグメント間相対重要度"
      ],
      "outputs": [
        "セグメント優先度レポート",
        "セグメント別アプローチガイド",
        "営業リソース配分推奨",
        "実行タイムライン",
        "ダッシュボード（グラフ、テーブル）",
        "詳細システムログ"
      ]
    }
  ],
  "communication_protocol": {
    "standard": "FIPA準拠のACL",
    "error_handling": "各エージェントは入力検証とエラーチェックを実施。エラー発生時は統合エージェントへ通知し、リトライ処理を実施。",
    "logging": "各エージェントは計算プロセスと意思決定根拠を詳細にログとして記録し、統合エージェントに提供"
  },
  "feedback_loop": {
    "description": "IntegrationAndOutputAgentは最終EVCレポートに対するフィードバックを収集し、必要に応じてFormulaDesignAgentに再計算・パラメータ調整の指示を送る仕組みを持つ。",
    "cycle": "定期的な評価と改善サイクルを実施"
  }
}
```

## 7. セグメント別の市場アプローチ戦略

### 低価値・低障壁セグメント（最優先）
- 戦略: スケーラブルな営業モデル構築
- アプローチ: デジタルマーケティング、ウェビナー、自動化されたオンボーディング
- 価格戦略: 手頃な価格帯、段階的な機能拡張モデル
- 価値訴求: 「手頃な投資で業務効率化と売上拡大を同時実現」

### 高価値・高障壁セグメント（第2優先）
- 戦略: 業界別ソリューション開発
- アプローチ: 業界イベント、専門コンサルタント連携、規制対応支援
- 価格戦略: 業界特化型パッケージ、長期契約モデル
- 価値訴求: 「コンプライアンスリスク低減と品質向上で競争優位性確保」

### 高価値・低障壁セグメント（第3優先）
- 戦略: ハイタッチ営業モデル
- アプローチ: エグゼクティブ向けイベント、カスタマイズ提案、専任サポート
- 価格戦略: プレミアム価格、包括的サービス
- 価値訴求: 「人件費削減と業務効率化で短期間で投資回収」

### 低価値・高障壁セグメント（長期視点）
- 戦略: 認知度向上と教育
- アプローチ: 業界団体連携、成功事例共有、無料トライアル
- 価格戦略: エントリーレベル製品、従量課金モデル
- 価値訴求: 「限定的な投資で将来の成長基盤を構築」

## 8. 実装のポイント

1. 定量化の徹底：すべての価値要素を金銭的に換算
2. セグメント特性の反映：各セグメントの特性に応じた価値要素の重み付け
3. 具体的な判断基準：セグメント判定のための明確な指標設定
4. 顧客視点の価値提案：財務的インパクトを中心とした説得力ある提案
5. 市場規模の考慮：単純なEVCだけでなく、市場ポテンシャルを加味した優先順位付け

---

### テキスト図（並列実行・参照商品個別分析、4セグメント対応）

```
                         ┌─────────────────────────────┐
                         │ Service Analysis Agent      │
                         │ (サービス概要抽出)          │
                         └────────────┬──────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────────┐
                         │ Service Overview Report     │
                         └────────────┬──────────────┘
                                      │
                                      ▼
             ┌─────────────────────────────────────────────────────────┐
             │                    並列処理フェーズ1                    │
             │  (以下の処理を同時に実行)                                 │
             ├─────────────┬─────────────────────────────────────────┐
             │             │                                         │
             ▼             ▼                                         │
  ┌─────────────────┐  ┌─────────────────────────────┐                │
  │Customer Segment │  │Reference Product            │                │
  │Extraction Agent │  │Identification Agent         │                │
  │ ───────────── │  │(競合製品特定)               │                │
  │ • 高価値・低障壁 │  └────────────┬──────────────┘                │
  │ • 高価値・高障壁 │             │                                    │
  │ • 低価値・低障壁 │             │                                    │
  │ • 低価値・高障壁 │             │                                    │
  │ • その他顧客   │             │                                    │
  └───────┬────────┘             │                                    │
          │                      ▼                                    │
          │             ┌─────────────────────────────┐                │
          │             │ Reference Product List      │                │
          │             │ ────────────────────── │                │
          │             │ • 参照製品1               │                │
          │             │ • 参照製品2               │                │
          │             │ • 参照製品3               │                │
          │             └────────────┬──────────────┘                │
          │                          │                                │
          │                          ▼                                │
          │             ┌─────────────────────────────┐                │
          │             │Reference Product Value      │                │
          │             │Analysis Agent               │                │
          │             │ ────────────────────── │                │
          │             │ • 参照製品1の価値算出    │                │
          │             │ • 参照製品2の価値算出    │                │
          │             │ • 参照製品3の価値算出    │                │
          │             └────────────┬──────────────┘                │
          │                          │                                │
          │                          ▼                                │
          │             ┌─────────────────────────────┐                │
          │             │ Combined Value Factors      │                │
          │             │ (参照商品の個別価値結果統合)  │                │
          │             └────────────┬──────────────┘                │
          └─────────────────────────┐│                                │
                                    ▼▼                                │
                      ┌─────────────────────────────┐                │
                      │ Value Comparison Agent      │                │
                      │ (セグメント別比較マトリックス)│                │
                      └────────────┬──────────────┘                │
                                   │                                  │
                                   ▼                                  │
                      ┌─────────────────────────────┐                │
                      │ Formula Design Agent        │                │
                      │ (各セグメント用EVC数式設計)   │                │
                      └────────────┬──────────────┘                │
                                   │                                  │
                                   ▼                                  │
             ┌─────────────────────────────────────────────────────┐  │
             │                    並列処理フェーズ2                 │  │
             │  (以下の処理を同時に実行)                              │  │
             ├─────────────────────┬───────────────────────────────┘  │
             │                     │                                   │
             ▼                     ▼                                   │
┌─────────────────────┐   ┌─────────────────────────────┐              │
│Market Potential     │   │ Segment-specific EVC        │              │
│Analysis Agent       │   │ Calculation Agent           │              │
│ ───────────────── │   │ ───────────────────── │              │
│ • 高価値・低障壁   │   │ • 高価値・低障壁のEVC算出 │              │
│ • 高価値・高障壁   │   │ • 高価値・高障壁のEVC算出 │              │
│ • 低価値・低障壁   │   │ • 低価値・低障壁のEVC算出 │              │
│ • 低価値・高障壁   │   │ • 低価値・高障壁のEVC算出 │              │
│ • その他顧客     │   │ • その他顧客のEVC算出   │              │
└─────────┬───────────┘   └────────────┬──────────────┘              │
          │                            │                               │
          └────────────────┬───────────┘                               │
                           ▼                                           │
                ┌─────────────────────────────┐                        │
                │ Priority Evaluation Agent   │                        │
                │ (優先度評価エージェント)    │                        │
                └────────────┬──────────────┘                        │
                             │                                         │
                             ▼                                         │
                ┌─────────────────────────────┐                        │
                │ Integration & Output Agent  │                        │
                │ (最終レポート生成)          │                        │
                └─────────────────────────────┘                        │
```

この設計により、参照商品を3つ特定した後に、各参照商品ごとの提供価値を個別に算出し、統合して4つの顧客セグメント（高価値・低障壁、高価値・高障壁、低価値・低障壁、低価値・高障壁）に対するEVCを算出・比較するプロセスが実現されます。