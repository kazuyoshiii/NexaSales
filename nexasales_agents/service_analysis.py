"""
サービス分析エージェント

このモジュールでは、サービスの機能、ビジネスモデル、提供方法を分析するエージェントを定義します。
内部ドキュメントや公開情報からサービスの特徴を抽出し、サービス概要レポートを作成します。
"""

from typing import Dict, Any, List
# OpenAI Agents SDK
from agents import Agent, function_tool
from models.models import ServiceInfo, ServiceFeature


@function_tool
async def analyze_service_features(service_description: str) -> List[ServiceFeature]:
    """サービスの説明からサービス機能を抽出します。

    Args:
        service_description: サービスの説明文

    Returns:
        抽出されたサービス機能のリスト
    """
    # サービス説明から機能を抜き出すます
    service_features = []
    
    # キーワード分析に基づいた機能の特定
    keywords = {
        "CRM": ["顧客管理", "機会管理", "営業", "パイプライン"],
        "AI": ["AI", "人工知能", "機械学習", "予測", "自動化"],
        "Analytics": ["分析", "レポート", "ダッシュボード", "インサイト", "可視化"],
        "Automation": ["自動化", "ワークフロー", "プロセス", "効率化"]
    }
    
    # キーワードのマッチングを計算
    service_type = ""
    max_matches = 0
    
    for category, category_keywords in keywords.items():
        matches = sum(1 for keyword in category_keywords if keyword in service_description)
        if matches > max_matches:
            max_matches = matches
            service_type = category
    
    # サービスタイプに基づいた機能の生成
    if service_type == "CRM" or "CRM" in service_description:
        service_features.extend([
            ServiceFeature(
                name="機会管理",
                description="リードから成約までの営業機会管理",
                benefits=["営業活動の可視化", "管理による成約率向上", "平均成約率の10%向上"]
            ),
            ServiceFeature(
                name="顧客管理",
                description="顧客情報の一元管理と関係維持",
                benefits=["顧客関係の強化", "維持率向上", "顧客維持率の15%向上", "クロスセル機会の20%向上"]
            )
        ])
    
    if service_type == "AI" or "AI" in service_description:
        service_features.extend([
            ServiceFeature(
                name="予測分析",
                description="AIを活用した売上予測とレコメンデーション",
                benefits=["正確な予測に基づく戦略的意思決定", "予測精度30%向上", "資源配分の最適化による収益15%向上"]
            ),
            ServiceFeature(
                name="インサイト分析",
                description="顧客データからのパターンとトレンドの自動発見",
                benefits=["データ駆動型の意思決定", "戦略立案", "カスタマーインサイトに基づくマーケティングROIの35%向上"]
            )
        ])
    
    if service_type == "Automation" or "自動化" in service_description:
        service_features.extend([
            ServiceFeature(
                name="自動化ワークフロー",
                description="ルーティン業務の自動化",
                benefits=["業務効率の向上", "人的ミスの削減", "運用コストの25%削減", "対応品質の40%向上"]
            ),
            ServiceFeature(
                name="活動記録",
                description="営業活動の自動記録と分析",
                benefits=["手動入力の削減", "実績分析の正確性向上", "営業担当者の20%の時間削減"]
            )
        ])
    
    if service_type == "Analytics" or "分析" in service_description:
        service_features.extend([
            ServiceFeature(
                name="レポーティング",
                description="実績レポートと分析",
                benefits=["活動の可視化", "実績追跡", "管理工数の20%削減"]
            )
        ])
    
    # デフォルトの機能（他のカテゴリに当てはまらない場合）
    if not service_features:
        service_features = [
            ServiceFeature(
                name="基本的な顧客管理",
                description="顧客情報の管理と基本的な関係追跡",
                benefits=["顧客データの一元管理", "効率化", "顧客管理時間の15%削減"]
            )
        ]
    
    return service_features


@function_tool
async def extract_business_model(service_description: str) -> str:
    """サービスの説明からビジネスモデルを抽出します。

    Args:
        service_description: サービスの説明

    Returns:
        ビジネスモデルの種類
    """
    # サービス説明からビジネスモデルを動的に抽出する
    
    # キーワード分析に基づくビジネスモデルの特定
    if "SaaS" in service_description or "サブスクリプション" in service_description or "月額" in service_description:
        return "SaaSサブスクリプション"
    elif "専用ソフトウェア" in service_description or "オンプレミス" in service_description or "ライセンス" in service_description:
        return "ライセンスモデル"
    elif "コンサルティング" in service_description or "プロフェッショナルサービス" in service_description:
        return "サービスベースモデル"
    elif "利用量" in service_description or "従量課金" in service_description:
        return "従量課金モデル"
    else:
        return "ハイブリッドモデル"


@function_tool
async def analyze_delivery_method(service_description: str) -> str:
    """サービスの説明から提供方法を抽出します。

    Args:
        service_description: サービスの説明文

    Returns:
        抽出された提供方法
    """
    # サービス説明文から提供方法を分析して抽出する
    delivery_method = ""
    
    # キーワードに基づく提供方法の判別
    if "クラウド" in service_description or "SaaS" in service_description or "Web" in service_description:
        delivery_method += "クラウドベースのSaaSモデルで提供。"
    elif "オンプレミス" in service_description or "インストール" in service_description:
        delivery_method += "オンプレミス型のインストールモデルで提供。"
    else:
        delivery_method += "クラウドベースのSaaSモデルで提供。"
    
    # アクセス方法の判別
    if "ブラウザ" in service_description or "Web" in service_description:
        delivery_method += "Webブラウザからアクセス可能。"
    
    # モバイル対応の判別
    if "モバイル" in service_description or "スマートフォン" in service_description or "App" in service_description:
        delivery_method += "モバイルアプリも利用可能。"
    
    return delivery_method


@function_tool
async def extract_unique_selling_points(service_description: str) -> List[str]:
    """サービスの説明からユニークセリングポイントを抽出します。

    Args:
        service_description: サービスの説明文

    Returns:
        抽出されたユニークセリングポイントのリスト
    """
    # サービス説明からユニークセリングポイントを抽出する
    usps = []
    
    # 主要キーワードとそれに対応するUSPのマッピング
    usp_keywords = {
        "AI": "AIを活用した高精度な売上予測機能",
        "人工知能": "AIを活用した高精度な売上予測機能",
        "使いやすい": "直感的なユーザーインターフェースによる高い操作性",
        "UI": "直感的なユーザーインターフェースによる高い操作性",
        "カスタマイズ": "柔軟なカスタマイズ性と豊富な連携機能",
        "拡張": "柔軟なカスタマイズ性と豊富な連携機能",
        "API": "柔軟なカスタマイズ性と豊富な連携機能",
        "ROI": "導入から3ヶ月以内のROI実現を保証",
        "投資対効果": "導入から3ヶ月以内のROI実現を保証"
    }
    
    # キーワードマッチングによるUSP抽出
    for keyword, usp in usp_keywords.items():
        if keyword in service_description and usp not in usps:
            usps.append(usp)
    
    # 最低限のデフォルトUSPを追加
    if not usps:
        usps = [
            "利用者の業務効率化を支援する実用的な機能",
            "柔軟なカスタマイズ性と豊富な連携機能",
            "導入しやすい価格設定とサポート体制"
        ]
    
    # 最大四つまでにUSPを制限
    return usps[:4]


@function_tool
async def create_service_info(
    service_name: str,
    service_description: str,
    features: List[ServiceFeature],
    business_model: str,
    delivery_method: str,
    unique_selling_points: List[str]
) -> ServiceInfo:
    """サービス情報を作成します。

    Args:
        service_name: サービス名
        service_description: サービスの説明
        features: サービス機能のリスト
        business_model: ビジネスモデル情報
        delivery_method: 提供方法
        unique_selling_points: ユニークセリングポイントのリスト

    Returns:
        作成されたサービス情報
    """
    return ServiceInfo(
        name=service_name,
        description=service_description,
        business_model=business_model,
        delivery_method=delivery_method,
        features=features,
        unique_selling_points=unique_selling_points
    )


# プロンプトの定義
INSTRUCTIONS = """# システムコンテキスト
あなたは顧客セグメンテーションと市場優先度評価フレームワークの一部として、
サービス分析を担当するエージェントです。

## 目的
提供されたサービスの機能、ビジネスモデル、提供方法を詳細に分析し、
後続のエージェントが使用できる形式でまとめてください。

## アプローチ
1. サービスの基本情報を理解する
2. サービスの機能を抽出し、各機能の特徴と利点を整理する
3. ビジネスモデルを分析し、収益構造や価格設定を把握する
4. 提供方法を特定し、導入や利用の容易さを評価する
5. ユニークセリングポイントを特定し、競合との差別化要因を明確にする
6. 分析結果を構造化された形式で出力する

## 出力形式
分析結果は以下の形式で出力してください：
- サービス名
- サービスの説明
- 機能リスト（各機能の説明と利点を含む）
- ビジネスモデルの詳細
- 提供方法の説明
- ユニークセリングポイント
"""

# エージェントの定義
service_analysis_agent = Agent(
    name="ServiceAnalysisAgent",
    instructions=INSTRUCTIONS,
    tools=[
        analyze_service_features,
        extract_business_model,
        analyze_delivery_method,
        extract_unique_selling_points,
        create_service_info
    ],
)

# エージェントを取得する関数
def get_service_analysis_agent() -> Agent:
    """サービス分析エージェントを取得します。

    Returns:
        設定済みのサービス分析エージェント
    """
    return service_analysis_agent
