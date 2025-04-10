/**
 * エージェントシステムの型定義
 */

// 顧客セグメントの定義
export enum CustomerSegment {
  HighValueLowBarrier = "高価値・低障壁",
  HighValueHighBarrier = "高価値・高障壁",
  LowValueLowBarrier = "低価値・低障壁",
  LowValueHighBarrier = "低価値・高障壁"
}

// 収益向上価値の構成要素
export interface RevenueEnhancement {
  newRevenue: number; // 新規収益（Rn）
  retentionRevenue: number; // 既存顧客維持による収益（Rr）
  pricingRevenue: number; // 価格最適化による収益（Rp）
  transactionRevenue: number; // 取引頻度向上による収益（Rt）
  total: number; // 合計 (Re = Rn + Rr + Rp + Rt)
}

// コスト最適化価値の構成要素
export interface CostOptimization {
  directCostReduction: number; // 直接コスト削減（Cd）
  qualityCostReduction: number; // 品質関連コスト削減（Cq）
  riskCostReduction: number; // リスク関連コスト削減（Cr）
  timeCostReduction: number; // 時間関連コスト削減（Ct）
  total: number; // 合計 (Co = Cd + Cq + Cr + Ct)
}

// EVC計算結果
export interface EVCResult {
  referencePrice: number; // 参照価格（R）
  revenueEnhancement: RevenueEnhancement; // 収益向上価値（Re）
  costOptimization: CostOptimization; // コスト最適化価値（Co）
  implementationCost: number; // 導入コスト（I）
  totalEVC: number; // 合計EVC (EVC = R + (Re + Co) - I)
}

// 市場ポテンシャル分析結果
export interface MarketPotential {
  segmentSize: number; // セグメント企業数
  acquisitionProbability: number; // 獲得確率
  potentialValue: number; // 市場ポテンシャル値
}

// セグメント優先度評価結果
export interface SegmentPriority {
  segment: CustomerSegment; // 顧客セグメント
  evcResult: EVCResult; // EVC計算結果
  marketPotential: MarketPotential; // 市場ポテンシャル
  priorityScore: number; // 優先度スコア (セグメント優先度 = セグメント別EVC × セグメント企業数 × 獲得確率)
  recommendedResourceAllocation: number; // 推奨リソース配分比率（%）
}

// サービス分析結果
export interface ServiceAnalysis {
  serviceName: string; // サービス名
  serviceDescription: string; // サービス概要
  keyFeatures: string[]; // 主要機能
  uniqueSellingPoints: string[]; // ユニークセリングポイント
  businessModel: string; // ビジネスモデル
  targetMarket: string; // ターゲット市場
}

// 参照商品情報
export interface ReferenceProduct {
  productName: string; // 商品名
  productDescription: string; // 商品概要
  pricing: string; // 価格設定
  keyFeatures: string[]; // 主要機能
  valueProposition: string; // 価値提案
}

// 顧客セグメント情報
export interface SegmentInfo {
  segment: CustomerSegment; // セグメント名
  description: string; // セグメント説明
  characteristics: string[]; // 特徴
  painPoints: string[]; // 課題
  valueDrivers: string[]; // 価値ドライバー
}

// エージェント間の共通メッセージ形式
export interface AgentMessage {
  agentId: string; // 送信元エージェントID
  messageType: string; // メッセージタイプ
  content: any; // メッセージ内容
  timestamp: string; // タイムスタンプ
}
