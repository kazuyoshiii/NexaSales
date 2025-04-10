import { OpenAI } from 'openai';
import { OPENAI_API_KEY, AGENT_MODEL, getBusinessDocument } from '../utils/config';
import { ServiceAnalysis } from '../types';

/**
 * ServiceAnalysisAgent
 * 
 * 内部ドキュメントや公開情報からサービスの機能、ビジネスモデル、提供方法を抽出し、
 * サービスの特徴、ユニークセリングポイント、機能一覧を含むサービス概要レポートを作成するエージェント
 */
export class ServiceAnalysisAgent {
  private openai: OpenAI;
  private businessDocument: string;

  constructor() {
    this.openai = new OpenAI({
      apiKey: OPENAI_API_KEY,
    });
    this.businessDocument = getBusinessDocument();
  }

  /**
   * サービス分析を実行する
   * @param serviceName サービス名
   * @returns サービス分析結果
   */
  public async analyzeService(serviceName: string): Promise<ServiceAnalysis> {
    try {
      // アシスタントの作成
      const assistant = await this.openai.beta.assistants.create({
        name: "ServiceAnalysisAgent",
        instructions: this.getAgentInstructions(serviceName),
        model: AGENT_MODEL,
        tools: [{ type: "retrieval" }],
      });

      // スレッドの作成
      const thread = await this.openai.beta.threads.create();

      // メッセージの追加
      await this.openai.beta.threads.messages.create(thread.id, {
        role: "user",
        content: `${serviceName}の詳細な分析を行い、サービス概要レポートを作成してください。以下のビジネスドキュメントを参考にしてください：\n\n${this.businessDocument}`,
      });

      // 実行の開始
      const run = await this.openai.beta.threads.runs.create(thread.id, {
        assistant_id: assistant.id,
      });

      // 実行の完了を待機
      let runStatus = await this.openai.beta.threads.runs.retrieve(thread.id, run.id);
      while (runStatus.status !== "completed") {
        await new Promise(resolve => setTimeout(resolve, 1000));
        runStatus = await this.openai.beta.threads.runs.retrieve(thread.id, run.id);
        
        if (["failed", "cancelled", "expired"].includes(runStatus.status)) {
          throw new Error(`アシスタントの実行に失敗しました: ${runStatus.status}`);
        }
      }

      // 結果の取得
      const messages = await this.openai.beta.threads.messages.list(thread.id);
      const assistantMessages = messages.data.filter(msg => msg.role === "assistant");
      const latestMessage = assistantMessages[0];
      
      if (!latestMessage || !latestMessage.content || latestMessage.content.length === 0) {
        throw new Error("アシスタントからの応答がありません");
      }

      const content = latestMessage.content[0];
      if (content.type !== "text") {
        throw new Error("テキスト以外の応答は処理できません");
      }

      // JSONとして解析
      const analysisResult = this.parseAnalysisResult(content.text.value);

      // リソースのクリーンアップ
      await this.openai.beta.assistants.del(assistant.id);

      return analysisResult;
    } catch (error) {
      console.error("サービス分析中にエラーが発生しました:", error);
      throw error;
    }
  }

  /**
   * エージェントの指示を生成する
   * @param serviceName サービス名
   * @returns エージェントの指示
   */
  private getAgentInstructions(serviceName: string): string {
    return `
あなたは${serviceName}の詳細な分析を行うエキスパートエージェントです。
提供された情報から以下の項目を抽出し、構造化されたサービス概要レポートを作成してください。

分析項目:
1. サービス名
2. サービス概要: サービスの目的と主な機能を簡潔に説明
3. 主要機能: 箇条書きで5-7つの主要機能をリストアップ
4. ユニークセリングポイント: 競合と差別化できる3-5つの特徴
5. ビジネスモデル: 収益構造や課金方法
6. ターゲット市場: 主なターゲット顧客層

出力形式:
JSONフォーマットで以下の構造に従って出力してください。
{
  "serviceName": "サービス名",
  "serviceDescription": "サービス概要の説明",
  "keyFeatures": ["機能1", "機能2", ...],
  "uniqueSellingPoints": ["特徴1", "特徴2", ...],
  "businessModel": "ビジネスモデルの説明",
  "targetMarket": "ターゲット市場の説明"
}

注意事項:
- 情報が不足している場合は、ビジネスドキュメントの文脈から合理的に推測してください
- 出力は必ず有効なJSON形式にしてください
- 日本語で出力してください
`;
  }

  /**
   * 分析結果をパースする
   * @param responseText アシスタントからの応答テキスト
   * @returns パースされたサービス分析結果
   */
  private parseAnalysisResult(responseText: string): ServiceAnalysis {
    try {
      // JSONブロックを抽出
      const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/) || 
                        responseText.match(/```\n([\s\S]*?)\n```/) ||
                        responseText.match(/{[\s\S]*?}/);
      
      let jsonText = '';
      if (jsonMatch) {
        jsonText = jsonMatch[1] || jsonMatch[0];
      } else {
        jsonText = responseText;
      }

      // JSONをパース
      const analysisResult = JSON.parse(jsonText) as ServiceAnalysis;
      
      // 必須フィールドの検証
      const requiredFields = [
        'serviceName', 
        'serviceDescription', 
        'keyFeatures', 
        'uniqueSellingPoints', 
        'businessModel', 
        'targetMarket'
      ];
      
      for (const field of requiredFields) {
        if (!(field in analysisResult)) {
          throw new Error(`必須フィールド '${field}' が結果に含まれていません`);
        }
      }

      return analysisResult;
    } catch (error) {
      console.error("分析結果のパースに失敗しました:", error);
      console.error("元のテキスト:", responseText);
      
      // エラー時のフォールバック
      return {
        serviceName: "不明",
        serviceDescription: "パースエラーが発生しました",
        keyFeatures: ["パースエラー"],
        uniqueSellingPoints: ["パースエラー"],
        businessModel: "パースエラー",
        targetMarket: "パースエラー"
      };
    }
  }
}
