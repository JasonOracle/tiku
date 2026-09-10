/**
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：Agnes-2.5-Flash
 * 修改内容：[AI 助理消息与卡片类型契约]
 */

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ActionCardPayload {
  actionId: string;
  actionType: 'create_exam' | 'batch_questions' | 'delete_exam' | 'sensitive_operation';
  title: string;
  summary: string;
  riskLevel: 'low' | 'medium' | 'high';
  displayFields: Array<{ label: string; value: string | number }>;
  rawParams?: Record<string, any>;
  status: 'pending' | 'executing' | 'confirmed' | 'cancelled';
}

export interface ExamCardData {
  examId: string | number;
  title: string;
  questionCount: number;
  totalScore?: number;
  downloadUrl: string;
  createdAt?: string;
}

export interface ChatMessage {
  id?: string | number;
  role: MessageRole;
  content: string;
  isStreaming?: boolean;
  isThinking?: boolean;
  quote?: string;
  actionCard?: ActionCardPayload | null;
  examCard?: ExamCardData | null;
  ragSources?: RagSource[];
  createdAt?: string;
}

export interface RagSource {
  document_id?: number;
  file_name?: string;
  document_name?: string;
  chunk_content?: string;
  similarity?: number;
  similarity_score?: number;
}
