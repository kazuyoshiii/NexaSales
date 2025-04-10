# NexaSales エージェントの入出力形式ドキュメント

このドキュメントでは、NexaSalesシステムで使用されている各エージェントのJSON入出力形式について詳細に説明します。

## 目次

- [NexaSales エージェントの入出力形式ドキュメント](#nexasales-エージェントの入出力形式ドキュメント)
  - [目次](#目次)
  - [全体概要](#全体概要)
  - [サービス分析エージェント](#サービス分析エージェント)
    - [入力形式](#入力形式)
    - [出力形式](#出力形式)
  - [顧客セグメント抽出エージェント](#顧客セグメント抽出エージェント)
    - [入力形式](#入力形式-1)
    - [出力形式](#出力形式-1)
  - [参照製品特定エージェント](#参照製品特定エージェント)
    - [入力形式](#入力形式-2)
    - [出力形式](#出力形式-2)
  - [価値比較エージェント](#価値比較エージェント)
    - [入力形式](#入力形式-3)
    - [出力形式](#出力形式-3)
  - [計算式設計エージェント](#計算式設計エージェント)
    - [入力形式](#入力形式-4)
    - [出力形式](#出力形式-4)
  - [EVC計算エージェント](#evc計算エージェント)
    - [入力形式](#入力形式-5)
    - [出力形式](#出力形式-5)
  - [優先度評価エージェント](#優先度評価エージェント)
    - [入力形式](#入力形式-6)
    - [出力形式](#出力形式-6)
  - [共通の注意事項](#共通の注意事項)
  - [エージェント間のデータフロー](#エージェント間のデータフロー)

## 全体概要

NexaSalesシステムでは、各エージェントは基本的に文字列形式のJSON（または辞書をstr関数で文字列化したもの）を入出力します。本ドキュメントでは、各エージェントの関数の入出力形式を説明します。

## サービス分析エージェント

### 入力形式

サービス分析エージェントの主な入力は、サービスの説明文です。

```python
service_description: str
```

### 出力形式

サービス分析エージェントの出力は、`ServiceInfo`モデルに基づくJSONです。

```json
{
  "name": "サービス名",
  "description": "サービスの説明",
  "business_model": "ビジネスモデル（SaaS/ライセンス/コンサルティング等）",
  "delivery_method": "提供方法（クラウド/オンプレミス等）",
  "features": [
    {
      "name": "機能名",
      "description": "機能の説明",
      "benefits": ["利点1", "利点2", "利点3"]
    }
  ],
  "unique_selling_points": [
    "USP1", "USP2", "USP3"
  ]
}
```

## 顧客セグメント抽出エージェント

### 入力形式

顧客セグメント抽出エージェントの入力は、サービスの説明と市場データです。

```python
service_description: str
market_data: str
```

### 出力形式

顧客セグメント抽出エージェントの出力は、`CustomerSegment`モデルのリストをベースとしたJSONです。

```json
[
  {
    "segment_id": "s1",
    "name": "セグメント名",
    "value_potential": "high",
    "implementation_ease": "low",
    "segment_type": "high_value_high_barrier",
    "description": "セグメントの説明",
    "characteristics": ["特性1", "特性2", "特性3"],
    "industry_categories": ["業界1", "業界2"],
    "example_companies": ["企業例1", "企業例2"],
    "bant_information": {
      "budget": {
        "range": "予算範囲",
        "cycle": "予算サイクル",
        "decision_maker": "予算決定者"
      },
      "authority": {
        "final_decision_maker": "最終決定者",
        "champion": "推進者",
        "process": "意思決定プロセス"
      },
      "need": ["ニーズ1", "ニーズ2"],
      "timeline": {
        "consideration_period": "検討期間",
        "cycle": "導入サイクル",
        "urgency": "緊急度"
      }
    },
    "market_size": 100,
    "acquisition_probability": 0.3
  }
]
```

## 参照製品特定エージェント

### 入力形式

参照製品特定エージェントの入力は、サービスの説明と市場データです。

```python
service_description: str
market_data: str
```

### 出力形式

参照製品特定エージェントの出力は、`ReferenceProduct`モデルのリストをベースとしたJSONです。

```json
[
  {
    "name": "製品名",
    "company": "企業名",
    "description": "製品説明",
    "features": ["機能1", "機能2", "機能3"],
    "pricing": "価格情報",
    "market_share": 0.2,
    "strengths": ["強み1", "強み2"],
    "weaknesses": ["弱み1", "弱み2"]
  }
]
```

## 価値比較エージェント

### 入力形式

価値比較エージェントの入力は、セグメント情報と参照製品情報です。

```python
segments: List[CustomerSegment]
reference_products: List[ReferenceProduct]
```

### 出力形式

価値比較エージェントの出力は、`ValueComparisonReport`モデルをベースとしたJSONです。

```jsonjson
{
  "segment_id": "s1",
  "segment_name": "セグメント名",
  "reference_products": [
    {
      "name": "製品名",
      "company": "企業名",
      "description": "製品説明",
      "features": ["機能1", "機能2", "機能3"],
      "pricing": "価格情報",
      "market_share": 0.2,
      "strengths": ["強み1", "強み2"],
      "weaknesses": ["弱み1", "弱み2"]
    }
  ],
  "value_matrix": {
    "criteria1": {"製品1": 4, "製品2": 3},
    "criteria2": {"製品1": 2, "製品2": 4}
  },
  "plus_minus_matrix": {
    "criteria1": {"製品1": "+", "製品2": "-"},
    "criteria2": {"製品1": "-", "製品2": "+"}
  },
  "value_gaps": [
    {
      "gap_name": "ギャップ名",
      "description": "ギャップの説明",
      "opportunity": "機会の説明"
    }
  ],
  "summary": "比較サマリー"
}
```

## 計算式設計エージェント

### 入力形式

計算式設計エージェントの入力は、セグメント情報と価値比較情報です。

```python
segments: List[CustomerSegment]
value_comparisons: List[ValueComparisonReport]
```

### 出力形式

計算式設計エージェントの出力は、フォーミュラ設計情報を含むJSONです。

```json
{
  "base_formula": "EVC = R + (Re + Co) - I",
  "components": {
    "R": {
      "name": "参照価格",
      "description": "競合製品の価格に基づく参照価格",
      "weight": 1.0
    },
    "Re": {
      "name": "収益向上価値",
      "description": "製品による追加収益の価値",
      "weight": 1.2
    },
    "Co": {
      "name": "コスト最適化価値",
      "description": "製品によるコスト削減の価値",
      "weight": 1.0
    },
    "I": {
      "name": "導入コスト",
      "description": "製品導入・運用にかかるコスト",
      "weight": 1.0
    }
  },
  "segment_specific_parameters": {
    "annual_revenue": 10000000,
    "annual_cost": 5000000,
    "implementation_years": 3,
    "revenue_increase_rate": 0.1,
    "cost_reduction_rate": 0.15,
    "reference_price": 1000000,
    "initial_cost": 500000,
    "operation_cost": 200000
  },
  "segment_id": "s1"
}
```

## EVC計算エージェント

### 入力形式

EVC計算エージェントの入力は、セグメントID、計算式、パラメータです。

```python
segment_id: str
formula: str  # JSON文字列または計算式文字列
parameters: str  # パラメータを含むJSON文字列
```

### 出力形式

EVC計算エージェントの出力は、`EVCResult`モデルをベースとしたJSONです。

```json
{
  "segment_id": "s1",
  "segment_name": "セグメント名",
  "evc_value": 1500000,
  "components": {
    "reference_price": 1000000,
    "revenue_enhancement": {
      "name": "収益向上価値",
      "description": "製品による追加収益の価値",
      "formula": "年間収益 * 増加率 * 年数",
      "value": 3000000,
      "calculation_details": {
        "annual_revenue": 10000000,
        "increase_rate": 0.1,
        "years": 3
      }
    },
    "cost_optimization": {
      "name": "コスト最適化価値",
      "description": "製品によるコスト削減の価値",
      "formula": "年間コスト * 削減率 * 年数",
      "value": 2250000,
      "calculation_details": {
        "annual_cost": 5000000,
        "reduction_rate": 0.15,
        "years": 3
      }
    },
    "implementation_cost": 700000
  },
  "calculation_details": {
    "formula": "EVC = R + (Re + Co) - I",
    "R": 1000000,
    "Re": 3000000,
    "Co": 2250000,
    "I": 700000,
    "weighted_Re": 3600000,
    "weighted_Co": 2250000,
    "final_evc": 6150000
  }
}
```

## 優先度評価エージェント

### 入力形式

優先度評価エージェントの入力は、セグメント情報とEVC計算結果です。

```python
segments: List[CustomerSegment]
evc_results: List[EVCResult]
market_potentials: List[MarketPotential]
```

### 出力形式

優先度評価エージェントの出力は、`PriorityReport`モデルをベースとしたJSONです。

```json
{
  "segment_priorities": [
    {
      "segment_id": "s1",
      "segment_name": "セグメント名",
      "priority_score": 85.5,
      "evc_value": 6150000,
      "market_size": 100,
      "acquisition_probability": 0.3,
      "relative_importance": 0.4,
      "recommended_resource_allocation": 40
    }
  ],
  "approach_strategies": [
    {
      "segment_id": "s1",
      "segment_name": "セグメント名",
      "key_messages": ["メッセージ1", "メッセージ2"],
      "value_proposition": "価値提案文",
      "sales_tactics": ["戦術1", "戦術2"],
      "objection_handling": {
        "反論1": "対応策1",
        "反論2": "対応策2"
      },
      "success_metrics": ["指標1", "指標2"]
    }
  ],
  "summary": "優先度評価サマリー",
  "recommendations": ["推奨事項1", "推奨事項2"],
  "resource_allocation": {
    "セグメント1": 40,
    "セグメント2": 30,
    "セグメント3": 20,
    "セグメント4": 10
  }
}
```

## 共通の注意事項

1. **文字列形式の扱い**：多くの関数では、JSONをそのまま扱わず、文字列として渡されたパラメータをJSON.loads()を使って辞書に変換しています。入力パラメータが文字列の場合は、常にJSON解析を試みるべきです。

2. **エラーハンドリング**：パラメータの解析に失敗した場合、適切なエラーハンドリングが必要です。一般的なパターンとして、try-except構文でJSONのパースエラーを捕捉し、単一引用符をダブルクォートに変換するなどの回復処理を試みます。

3. **型変換**：パラメータの型変換（例：文字列→辞書）について一貫したアプローチを採用しましょう。

4. **出力の一貫性**：出力は必ずJSONとして解析可能な文字列形式にする必要があります。`str(dict_object)`では正確なJSON形式にならない場合があるため、`json.dumps(dict_object)`の使用が推奨されます。

## エージェント間のデータフロー

エージェント間のデータフローは以下の通りです：

1. サービス分析 → 顧客セグメント抽出 → 参照製品特定 → 価値比較
2. 価値比較 → 計算式設計 → EVC計算
3. EVC計算 → 優先度評価

各エージェントの出力は、次のエージェントの入力として使用されるため、一貫した形式を維持することが重要です。
