import { ServiceAnalysisAgent } from './agents/serviceAnalysisAgent';
import { CustomerSegmentExtractionAgent } from './agents/customerSegmentExtractionAgent';
import { ServiceAnalysis, SegmentInfo } from './types';

/**
 * メインアプリケーション
 * 
 * エージェントシステムを実行し、結果を出力する
 */
async function main() {
  try {
    console.log("NexaSalesエージェントシステムを開始します...");
    
    // サービス名
    const serviceName = "NexaSales";
    
    // ServiceAnalysisAgentの実行
    console.log("\n1. サービス分析を開始します...");
    const serviceAnalysisAgent = new ServiceAnalysisAgent();
    const serviceAnalysis: ServiceAnalysis = await serviceAnalysisAgent.analyzeService(serviceName);
    
    console.log("\nサービス分析結果:");
    console.log(JSON.stringify(serviceAnalysis, null, 2));
    
    // CustomerSegmentExtractionAgentの実行
    console.log("\n2. 顧客セグメント抽出を開始します...");
    const customerSegmentExtractionAgent = new CustomerSegmentExtractionAgent();
    const segmentInfo: SegmentInfo[] = await customerSegmentExtractionAgent.extractCustomerSegments(
      serviceName,
      `${serviceName}は${serviceAnalysis.serviceDescription}`
    );
    
    console.log("\n顧客セグメント抽出結果:");
    console.log(JSON.stringify(segmentInfo, null, 2));
    
    // 今後、他のエージェントも追加予定
    
    console.log("\nNexaSalesエージェントシステムが正常に完了しました。");
  } catch (error) {
    console.error("エラーが発生しました:", error);
  }
}

// アプリケーションの実行
main();
