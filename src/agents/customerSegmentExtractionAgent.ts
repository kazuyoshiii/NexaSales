import { OpenAI } from 'openai';
import { OPENAI_API_KEY, AGENT_MODEL, getBusinessDocument } from '../utils/config';
import { CustomerSegment, SegmentInfo } from '../types';

/**
 * CustomerSegmentExtractionAgent
 * 
 * 公開市場調査データ、業界レポート、専門家インタビューに基づいて
 * 「価値創出ポテンシャル」と「実現容易性」の2軸でセグメントを分類するエージェント
 */
export class CustomerSegmentExtractionAgent {
  private openai: OpenAI;
  private businessDocument: string;

  constructor() {
    this.openai = new OpenAI({
      apiKey: OPENAI_API_KEY,
    });
    this.businessDocument = getBusinessDocument();
  }

  /**
   * 顧客セグメントの抽出を実行する
   * @param serviceName サービス名
   * @param industryContext 業界コンテキスト（任意）
   * @returns 顧客セグメント情報の配列
   */
  public async extractCustomerSegments(
    serviceName: string, 
    industryContext?: string
  ): Promise<SegmentInfo[]> {
    try {
      // アシスタントの作成
      const assistant = await this.openai.beta.assistants.create({
        name: "CustomerSegmentExtractionAgent",
        instructions: this.getAgentInstructions(serviceName),
        model: AGENT_MODEL,
        tools: [{ type: "retrieval" }],
      });

      // スレッドの作成
      const thread = await this.openai.beta.threads.create();

      // メッセージの追加
      let prompt = `${serviceName}の顧客セグメント分析を行い、「価値創出ポテンシャル」と「実現容易性」の2軸で4つのセグメントに分類してください。以下のビジネスドキュメントを参考にしてください：\n\n${this.businessDocument}`;
      
      if (industryContext) {
        prompt += `\n\n業界コンテキスト：\n${industryContext}`;
      }
      
      await this.openai.beta.threads.messages.create(thread.id, {
        role: "user",
        content: prompt,
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
      const segmentResults = this.parseSegmentResults(content.text.value);

      // リソースのクリーンアップ
      await this.openai.beta.assistants.del(assistant.id);

      return segmentResults;
    } catch (error) {
      console.error("顧客セグメント抽出中にエラーが発生しました:", error);
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
あなたは${serviceName}の顧客セグメント分析を行うエキスパートエージェントです。
提供された情報から「価値創出ポテンシャル」と「実現容易性」の2軸で4つのセグメントに分類し、
各セグメントの特徴、課題、価値ドライバーを分析してください。

分析対象の4つのセグメント:
1. 高価値・低障壁セグメント：高い価値をすぐに実現できる顧客
2. 高価値・高障壁セグメント：高い価値だが実現に障壁がある顧客
3. 低価値・低障壁セグメント：中程度の価値をすぐに実現できる顧客
4. 低価値・高障壁セグメント：現時点では価値も実現も限定的な顧客

分析項目:
1. セグメント名: 上記4つのセグメントのいずれか
2. セグメント説明: そのセグメントの特徴を簡潔に説明
3. 特徴: 箇条書きで3-5つの特徴をリストアップ
4. 課題: 箇条書きで3-5つの課題をリストアップ
5. 価値ドライバー: 箇条書きで3-5つの価値ドライバーをリストアップ

出力形式:
JSONフォーマットで以下の構造に従って出力してください。4つのセグメントすべてを含む配列形式で出力してください。
[
  {
    "segment": "高価値・低障壁",
    "description": "セグメント説明",
    "characteristics": ["特徴1", "特徴2", ...],
    "painPoints": ["課題1", "課題2", ...],
    "valueDrivers": ["価値ドライバー1", "価値ドライバー2", ...]
  },
  {
    "segment": "高価値・高障壁",
    "description": "セグメント説明",
    "characteristics": ["特徴1", "特徴2", ...],
    "painPoints": ["課題1", "課題2", ...],
    "valueDrivers": ["価値ドライバー1", "価値ドライバー2", ...]
  },
  ...
]

注意事項:
- 情報が不足している場合は、ビジネスドキュメントの文脈から合理的に推測してください
- 出力は必ず有効なJSON形式にしてください
- 日本語で出力してください
- 4つのセグメントすべてについて分析を行ってください
`;
  }

  /**
   * セグメント結果をパースする
   * @param responseText アシスタントからの応答テキスト
   * @returns パースされた顧客セグメント情報の配列
   */
  private parseSegmentResults(responseText: string): SegmentInfo[] {
    try {
      // JSONブロックを抽出
      const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/) || 
                        responseText.match(/```\n([\s\S]*?)\n```/) ||
                        responseText.match(/\[([\s\S]*?)\]/);
      
      let jsonText = '';
      if (jsonMatch) {
        jsonText = jsonMatch[1] || jsonMatch[0];
      } else {
        jsonText = responseText;
      }

      // JSONをパース
      const segmentResults = JSON.parse(jsonText) as SegmentInfo[];
      
      // 結果の検証
      if (!Array.isArray(segmentResults) || segmentResults.length === 0) {
        throw new Error("セグメント結果が配列ではないか、空の配列です");
      }
      
      // 各セグメントの必須フィールドを検証
      for (const segment of segmentResults) {
        const requiredFields = ['segment', 'description', 'characteristics', 'painPoints', 'valueDrivers'];
        for (const field of requiredFields) {
          if (!(field in segment)) {
            throw new Error(`セグメント '${segment.segment}' に必須フィールド '${field}' がありません`);
          }
        }
        
        // セグメント名が有効かチェック
        if (!Object.values(CustomerSegment).includes(segment.segment as CustomerSegment)) {
          throw new Error(`無効なセグメント名: ${segment.segment}`);
        }
      }

      return segmentResults;
    } catch (error) {
      console.error("セグメント結果のパースに失敗しました:", error);
      console.error("元のテキスト:", responseText);
      
      // エラー時のフォールバック
      return Object.values(CustomerSegment).map(segment => ({
        segment,
        description: "パースエラーが発生しました",
        characteristics: ["パースエラー"],
        painPoints: ["パースエラー"],
        valueDrivers: ["パースエラー"]
      }));
    }
  }
}
