import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';

// .envファイルを読み込む
dotenv.config();

// 環境変数の取得と検証を行う関数
export function getEnvVariable(key: string, defaultValue?: string): string {
  const value = process.env[key] || defaultValue;
  if (value === undefined) {
    throw new Error(`環境変数 ${key} が設定されていません。`);
  }
  return value;
}

// OpenAI API設定
export const OPENAI_API_KEY = getEnvVariable('OPENAI_API_KEY');
export const AGENT_MODEL = getEnvVariable('AGENT_MODEL', 'gpt-4-turbo');

// ビジネスドキュメントのパス
export const BUSINESS_DOC_PATH = path.resolve(__dirname, '../../docs/business.md');

// ビジネスドキュメントの内容を読み込む関数
export function getBusinessDocument(): string {
  try {
    return fs.readFileSync(BUSINESS_DOC_PATH, 'utf-8');
  } catch (error) {
    console.error('ビジネスドキュメントの読み込みに失敗しました:', error);
    return '';
  }
}
