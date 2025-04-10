"""
NexaSales顧客セグメンテーションシステムのデータモデル定義

このモジュールでは、システム全体で使用するデータモデルを定義します。
Pydanticを使用して型安全なモデルを提供します。
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class ValuePotential(str, Enum):
    """価値創出ポテンシャルの列挙型"""
    HIGH = "high"
    LOW = "low"


class ImplementationEase(str, Enum):
    """実現容易性の列挙型"""
    HIGH = "high"
    LOW = "low"


class SegmentType(str, Enum):
    """セグメントタイプの列挙型"""
    HIGH_VALUE_LOW_BARRIER = "high_value_low_barrier"  # 高価値・低障壁（最優先）
    HIGH_VALUE_HIGH_BARRIER = "high_value_high_barrier"  # 高価値・高障壁
    LOW_VALUE_LOW_BARRIER = "low_value_low_barrier"    # 低価値・低障壁
    LOW_VALUE_HIGH_BARRIER = "low_value_high_barrier"  # 低価値・高障壁


class BANTBudget(BaseModel):
    """予算（Budget）情報モデル"""
    range: Optional[str] = None  # 予算の範囲
    cycle: Optional[str] = None  # 予算サイクル
    decision_maker: Optional[str] = None  # 予算決定者

    class Config:
        extra = "forbid"

class BANTAuthority(BaseModel):
    """権限（Authority）情報モデル"""
    final_decision_maker: Optional[str] = None  # 最終決定者
    champion: Optional[str] = None  # 推進者
    process: Optional[str] = None  # 意思決定プロセス

    class Config:
        extra = "forbid"

class BANTTimeline(BaseModel):
    """タイムライン（Timeline）情報モデル"""
    consideration_period: Optional[str] = None  # 検討期間
    cycle: Optional[str] = None  # 導入サイクル
    urgency: Optional[str] = None  # 緊急度

    class Config:
        extra = "forbid"

class BANTInformation(BaseModel):
    """BANT情報モデル"""
    budget: BANTBudget = Field(default_factory=BANTBudget)
    authority: BANTAuthority = Field(default_factory=BANTAuthority)
    need: List[str] = Field(default_factory=list)
    timeline: BANTTimeline = Field(default_factory=BANTTimeline)

    class Config:
        extra = "forbid"

class CustomerSegment(BaseModel):
    """顧客セグメントモデル"""
    segment_id: str
    name: str
    value_potential: ValuePotential
    implementation_ease: ImplementationEase
    segment_type: Optional[SegmentType] = None  # セグメントタイプ（自動判定可能）
    description: str
    characteristics: List[str]
    industry_categories: List[str] = Field(default_factory=list)  # 業界カテゴリのリスト
    example_companies: List[str] = Field(default_factory=list)  # 具体的な企業例のリスト
    bant_information: BANTInformation = Field(default_factory=BANTInformation)  # BANT情報
    market_size: Optional[int] = None
    acquisition_probability: Optional[float] = None
    
    class Config:
        extra = "forbid"


class ServiceFeature(BaseModel):
    """サービス機能モデル"""
    name: str
    description: str
    benefits: List[str]
    
    class Config:
        extra = "forbid"


class ServiceInfo(BaseModel):
    """サービス情報モデル"""
    name: str
    description: str
    business_model: str
    delivery_method: str
    features: List[ServiceFeature]
    unique_selling_points: List[str]
    
    class Config:
        extra = "forbid"


class ReferenceProduct(BaseModel):
    """参照製品モデル"""
    name: str
    company: str
    description: str
    features: List[str]
    pricing: Optional[str] = None
    market_share: Optional[float] = None
    strengths: List[str]
    weaknesses: List[str]
    
    class Config:
        extra = "forbid"


class ValueComponent(BaseModel):
    """価値要素モデル"""
    name: str
    description: str
    formula: str
    value: float
    calculation_details: Dict[str, Any]
    
    class Config:
        extra = "forbid"


class EVCComponents(BaseModel):
    """EVC構成要素モデル"""
    reference_price: float = Field(..., description="参照価格 (R)")
    revenue_enhancement: ValueComponent = Field(..., description="収益向上価値 (Re)")
    cost_optimization: ValueComponent = Field(..., description="コスト最適化価値 (Co)")
    implementation_cost: float = Field(..., description="導入コスト (I)")
    
    class Config:
        extra = "forbid"


class EVCResult(BaseModel):
    """EVC計算結果モデル"""
    segment_id: str
    segment_name: str
    evc_value: float
    components: EVCComponents
    calculation_details: Dict[str, Union[float, str]]
    
    class Config:
        extra = "forbid"


class MarketPotential(BaseModel):
    """市場ポテンシャルモデル"""
    segment_id: str
    segment_name: str
    market_size: int = Field(..., description="セグメント企業数")
    acquisition_probability: float = Field(..., description="獲得確率")
    total_potential_value: float = Field(..., description="総市場ポテンシャル")
    analysis_details: Dict[str, Union[float, str]]
    
    class Config:
        extra = "forbid"


class SegmentPriority(BaseModel):
    """セグメント優先度モデル"""
    segment_id: str
    segment_name: str
    priority_score: float
    evc_value: float
    market_size: int
    acquisition_probability: float
    relative_importance: float = Field(..., description="相対的重要度（0-1）")
    recommended_resource_allocation: float = Field(..., description="推奨リソース配分比率（%）")
    
    class Config:
        extra = "forbid"


class ApproachStrategy(BaseModel):
    """アプローチ戦略モデル"""
    segment_id: str
    segment_name: str
    key_messages: List[str]
    value_proposition: str
    sales_tactics: List[str]
    objection_handling: Dict[str, str]
    success_metrics: List[str]
    
    class Config:
        extra = "forbid"


class ServiceAnalysisReport(BaseModel):
    """サービス分析レポートモデル"""
    service_info: ServiceInfo
    features_analysis: List[Dict[str, Any]]
    business_model_analysis: Dict[str, Any]
    delivery_method_analysis: Dict[str, Any]
    unique_selling_points: List[str]
    summary: str
    
    class Config:
        extra = "forbid"


class ValueComparisonReport(BaseModel):
    """価値比較レポートモデル"""
    segment_id: str
    segment_name: str
    reference_products: List[ReferenceProduct]
    value_matrix: Dict[str, Any]
    plus_minus_matrix: Dict[str, Any]
    value_gaps: List[Dict[str, Any]]
    summary: str
    
    class Config:
        extra = "forbid"


class PriorityReport(BaseModel):
    """優先度評価レポートモデル"""
    segment_priorities: List[SegmentPriority]
    approach_strategies: List[ApproachStrategy]
    summary: str
    recommendations: List[str]
    resource_allocation: Dict[str, float]
    
    class Config:
        extra = "forbid"


class FinalReport(BaseModel):
    """最終レポートモデル"""
    service_info: ServiceInfo
    segments: List[CustomerSegment]
    evc_results: List[EVCResult]
    market_potentials: List[MarketPotential]
    segment_priorities: List[SegmentPriority]
    approach_strategies: List[ApproachStrategy]
    summary: str
    recommendations: List[str]
    
    class Config:
        extra = "forbid"
