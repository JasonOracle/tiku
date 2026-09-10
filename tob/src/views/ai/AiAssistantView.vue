<!--
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[修正试卷分类加载参数 target_type 为 task，解决分类下拉列表为空的Bug]
 * 修改时间：2026-09-10
 * AI模型：Gemini 系列
 * 修改内容：[1. 精简前端请求流，移除客户端臃肿的临时上下文拼接，全面托付后端权威档案与本地 Mem0 长期记忆; 2. onMounted 补充调用 userStore.loadProfile() 确保个人状态实时刷新]
 * 修改时间：2026-09-10
 * AI模型：Gemini 系列
 * 修改内容：[接入 SessionSidebar 的 @renamed 局部状态同步，会话重命名后无刷新实时更新侧边栏标题]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[全面恢复 v1.3 工具调用确认卡片: 接入 ToolCallCard 支持全题目预览/分类选择/考试时长/主观题批阅模式/知识溯源联动]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[修复 execute_tool 工具名映射: 正确兼容 create_exam/create_exam_draft 及其成功提示与后续流转]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[移除底部冗余的全局 thinking-indicator，统一由 MessageBubble 内部的骨架屏呈现单点思考态]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[1. 修复 currentMessages 未声明导致的页面白屏崩溃; 2. 移除重复的 ExamCardData interface 声明; 3. 规范 ActionCard confirm/cancel 事件传参]
 * 修改时间：2026-09-10
 * AI模型：Agnes-2.5-Flash
 * 修改内容：[v1.3 核心业务卡片回补: SSE流式对话 + 试卷卡片 + 工具调用确认 + 溯源抽屉]
-->
<template>
  <div class="ai-tab-container">
    <!-- 左侧会话侧边栏 -->
    <SessionSidebar
      :sessions="sessions"
      :active-id="activeSessionId"
      @new="startNewSession"
      @select="selectSession"
      @delete="handleDeleteSession"
      @renamed="handleRenamedSession"
    />

    <!-- 右侧聊天主区域 -->
    <div class="chat-main">
      <div class="chat-header">
        <div class="model-badge">
          <span class="sparkle"><el-icon><MagicStick /></el-icon></span>
          <span class="model-name">AI 智能助管</span>
        </div>
        <div style="font-size: 13px; color: #64748b;">
          AI 智算引擎 · 私有业务上下文问答
        </div>
      </div>

      <div class="messages-wrap" ref="messagesWrapRef" @scroll="handleScroll">
        <div v-if="loadingMessages" class="history-loader">历史消息加载中...</div>
        <div v-if="currentMessages.length === 0 && !loadingMessages" class="welcome-screen">
          <WelcomePrompts @select-prompt="usePreset" />
        </div>

        <template v-for="item in currentMessages" :key="item.id ?? item._tmpId">
          <!-- 用户消息 -->
          <div v-if="item.role === 'user'" class="message-row user-row">
            <MessageBubble
              :role="item.role"
              :content="item.content"
              :username="userStore.username"
              :is-streaming="item.isStreaming"
            />
          </div>
          <!-- AI 消息 -->
          <div v-else class="message-row assistant-row">
            <!-- 1. 常规 Markdown 气泡（无论有无卡片，回复文本或思考中都正常展示） -->
            <MessageBubble
              v-if="item.content || item.isThinking"
              :role="item.role"
              :content="item.content"
              :username="userStore.username"
              :quote="item.quote"
              :is-thinking="item.isThinking"
              :is-streaming="item.isStreaming"
              :rag-sources="item.ragSources"
              @show-source="showSource"
              @feedback="submitFeedback"
            />
            <!-- 2. 全功能业务操作确认卡 (v1.3 核心工具调用卡，含试题列表/分类/时长/溯源抽屉) -->
            <ToolCallCard
              v-if="item.actionRequired || (item.actionCard && isToolOperation(item))"
              :message="toToolCallMessage(item)"
              :categories="examCategories"
              @confirm="handleToolConfirm"
              @cancel="handleToolCancel"
              @show-source="showSource"
            />
            <!-- 2.1 降级/普通结构化操作卡 -->
            <ActionCard
              v-else-if="item.actionCard && item.actionCard.title"
              :card-data="item.actionCard"
              @confirm="handleActionConfirm(item.actionCard)"
              @cancel="handleActionCancel(item.actionCard)"
            />
            <!-- 3. 试卷生成导出卡 -->
            <ExamCard
              v-if="item.examCard"
              :card-data="item.examCard"
              @download="downloadExamCard"
            />
          </div>
        </template>
      </div>

      <div class="input-container">
        <div class="input-box">
          <el-input
            v-model="input"
            type="textarea"
            :rows="3"
            placeholder="输入问题... (Enter 发送，Shift+Enter 换行)"
            @keydown.enter.exact.prevent="send"
            :disabled="sending"
          />
        </div>
        <div class="input-actions">
          <span class="tip-text">AI 可调用工具：组卷 / 出题 / 删除试卷</span>
          <el-button type="primary" class="send-btn" :loading="sending" :disabled="!input.trim()" @click="send">
            发送
          </el-button>
        </div>
      </div>
    </div>

    <!-- 溯源抽屉 -->
    <TraceDrawer
      :visible="srcVisible"
      :resource="activeSource"
      @update:visible="srcVisible = $event"
    />

    <!-- 批阅抽屉（由 action_list 唤起） -->
    <GradingDrawer
      :visible="gradingVisible"
      :exam-id="gradingExamId"
      :exam-title="gradingExamTitle"
      @update:visible="gradingVisible = $event"
      @graded="handleDrawerGraded"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { MagicStick } from '@element-plus/icons-vue';
import { useUserStore } from '../../store/user';
import request from '../../utils/request';
import SessionSidebar from './components/SessionSidebar.vue';
import MessageBubble from './components/MessageBubble.vue';
import ToolCallCard from './components/ToolCallCard.vue';
import ActionCard from './components/ActionCard.vue';
import ExamCard from './components/ExamCard.vue';
import WelcomePrompts from './components/WelcomePrompts.vue';
import TraceDrawer from '../resources/components/TraceDrawer.vue';
import GradingDrawer from '../exams/components/GradingDrawer.vue';
import type { ChatMessage, ActionCardPayload, ExamCardData } from './types';

interface CloudSession {
  id: number;
  title: string;
}

const userStore = useUserStore();
const input = ref('');
const sending = ref(false);
const messagesWrapRef = ref<HTMLElement | null>(null);
const sessions = ref<CloudSession[]>([]);
const activeSessionId = ref<number | null>(null);
const messages = ref<ChatMessage[]>([]);
const currentMessages = computed(() => messages.value);
const hasMore = ref(true);
const loadingHistory = ref(false);
const loadingMessages = ref(false);
const minMessageId = ref<number | null>(null);
const examCategories = ref<any[]>([]);
const srcVisible = ref(false);
const activeSource = ref<any>({});
const gradingVisible = ref(false);
const gradingExamId = ref<number | null>(null);
const gradingExamTitle = ref('');

const stripActionBlocks = (t: string): string =>
  (t || '')
    .replace(/```action_card\s*[\s\S]*?```/g, '')
    .replace(/```action_list\s*[\s\S]*?```/g, '')
    .replace(/```exam_card\s*[\s\S]*?```/g, '')
    .trim();

const normalizeServerMessage = (item: any): ChatMessage => {
  const msg: ChatMessage = {
    id: item.id,
    role: item.role,
    content: item.content || '',
    quote: item.quote || undefined
  };
  const cardData = item.action_card_data;
  if (cardData && typeof cardData === 'object') {
    if (cardData.kind === 'tool') {
      msg.actionRequired = true;
      msg.toolName = cardData.tool_name;
      msg.toolCallId = cardData.tool_call_id;
      msg.arguments = cardData.arguments;
      msg.riskLevel = cardData.risk_level || 'medium';
      msg.actionResolved = cardData.status === 'executed';
      if (!msg.content) msg.content = cardData.message || '';
    } else {
      msg.actionCard = { ...(cardData as object), resolved: (cardData.status as any) || 'pending' };
      msg.content = stripActionBlocks(msg.content) || msg.content;
    }
  }
  if (Array.isArray(item.action_list_data)) {
    msg.actionList = item.action_list_data;
    msg.content = stripActionBlocks(msg.content) || msg.content;
  }
  if (msg.role === 'assistant' && !msg.actionCard && !msg.actionList && !msg.actionRequired) {
    const parsed = extractActionBlocks(msg.content);
    msg.content = parsed.text || msg.content;
    msg.actionCard = parsed.card;
    msg.actionList = parsed.list;
    msg.examCard = parsed.examCard;
  }
  return msg;
};

const extractActionBlocks = (text: string): {
  text: string;
  card: any;
  list: any[];
  examCard: ExamCardData | null;
} => {
  let clean = text || '';
  let card: any = null;
  let list: any[] = [];
  let examCard: ExamCardData | null = null;

  const cardMatch = clean.match(/```action_card\s*([\s\S]*?)```/);
  if (cardMatch) {
    try {
      card = JSON.parse(cardMatch[1]);
    } catch (e) { /* 降级 */ }
    clean = clean.replace(cardMatch[0], '').trim();
  }

  const listMatch = clean.match(/```action_list\s*([\s\S]*?)```/);
  if (listMatch) {
    try {
      const parsed = JSON.parse(listMatch[1]);
      if (Array.isArray(parsed)) list = parsed;
    } catch (e) { /* 降级 */ }
    clean = clean.replace(listMatch[0], '').trim();
  }

  const examMatch = clean.match(/```exam_card\s*([\s\S]*?)```/);
  if (examMatch) {
    try {
      const parsed = JSON.parse(examMatch[1]);
      if (parsed && parsed.exam_id) examCard = parsed;
    } catch (e) { /* 降级 */ }
    clean = clean.replace(examMatch[0], '').trim();
  }

  return { text: clean, card, list, examCard };
};

const refreshSessions = async (): Promise<void> => {
  try {
    const res: any = await request.get('/api/v1/admin/ai/sessions');
    sessions.value = res.items || [];
  } catch (e) {
    sessions.value = [];
  }
};

const loadMessages = async (sessionId: number): Promise<void> => {
  loadingMessages.value = true;
  try {
    const res: any = await request.get(`/api/v1/admin/ai/sessions/${sessionId}/messages`, {
      params: { limit: 20 }
    });
    messages.value = (res.items || []).map(normalizeServerMessage);
    hasMore.value = !!res.has_more;
    minMessageId.value = res.next_cursor ?? null;
  } finally {
    loadingMessages.value = false;
  }
};

const initCloud = async (): Promise<void> => {
  try {
    await refreshSessions();
    if (sessions.value.length === 0) {
      await startNewSession();
      return;
    }
    activeSessionId.value = sessions.value[0].id;
    await loadMessages(activeSessionId.value as number);
    scrollToBottom();
  } catch (e) {
    /* 初始化失败时静默，显示空状态 */
  }
};

const startNewSession = async (): Promise<void> => {
  try {
    const res: any = await request.post('/api/v1/admin/ai/sessions');
    await refreshSessions();
    activeSessionId.value = res.id;
    messages.value = [];
    hasMore.value = false;
    minMessageId.value = null;
  } catch (e) {
    /* 拦截器已提示 */
  }
};

const selectSession = async (id: number): Promise<void> => {
  if (sending.value || id === activeSessionId.value) return;
  activeSessionId.value = id;
  hasMore.value = true;
  await loadMessages(id);
  scrollToBottom();
};

const handleDeleteSession = async (id: number): Promise<void> => {
  await refreshSessions();
  if (activeSessionId.value === id) {
    if (sessions.value.length > 0) {
      activeSessionId.value = sessions.value[0].id;
      await loadMessages(sessions.value[0].id);
      scrollToBottom();
    } else {
      await startNewSession();
    }
  }
};

const handleRenamedSession = (id: number, newTitle: string): void => {
  const item = sessions.value.find(s => s.id === id);
  if (item) {
    item.title = newTitle;
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesWrapRef.value) {
    messagesWrapRef.value.scrollTop = messagesWrapRef.value.scrollHeight;
  }
};

const isNearBottom = (): boolean => {
  const box = messagesWrapRef.value;
  if (!box) return true;
  return box.scrollHeight - box.scrollTop - box.clientHeight < 120;
};

const followScroll = (): void => {
  if (isNearBottom()) scrollToBottom();
};

const handleScroll = async (): Promise<void> => {
  const chatBox = messagesWrapRef.value;
  if (!chatBox || chatBox.scrollTop >= 60 || !hasMore.value || loadingHistory.value) return;
  if (activeSessionId.value == null || minMessageId.value == null) {
    hasMore.value = false;
    return;
  }
  loadingHistory.value = true;
  const oldHeight = chatBox.scrollHeight;
  const oldTop = chatBox.scrollTop;
  try {
    const res: any = await request.get(
      `/api/v1/admin/ai/sessions/${activeSessionId.value}/messages`,
      { params: { before_id: minMessageId.value, limit: 20 } }
    );
    const items = (res.items || []).map(normalizeServerMessage);
    if (items.length > 0) {
      messages.value.unshift(...items);
      hasMore.value = !!res.has_more;
      minMessageId.value = res.next_cursor ?? null;
      await nextTick();
      chatBox.scrollTop = chatBox.scrollHeight - oldHeight + oldTop;
    } else {
      hasMore.value = false;
    }
  } catch (e) {
    /* 静默 */
  } finally {
    loadingHistory.value = false;
  }
};

const examCategoriesLoaded = ref(false);
const loadExamCategories = async (): Promise<void> => {
  if (examCategoriesLoaded.value) return;
  try {
    const res: any = await request.get('/api/v1/admin/categories', { params: { target_type: 'task' } });
    examCategories.value = Array.isArray(res) ? res : (res.items || []);
  } catch (e) {
    examCategories.value = [];
  }
  examCategoriesLoaded.value = true;
};

const getPendingSnapshot = async (): Promise<string> => {
  try {
    const res: any = await request.get('/api/v1/admin/tasks', { params: { size: 100, status: 'published' } });
    const items = res.items || [];
    const lines: string[] = [];
    for (const t of items.slice(0, 10)) {
      const pending = t.pending_count || 0;
      if (pending > 0) {
        lines.push(`- 《${t.title?.substring(0, 40) || '未命名'}》(id=${t.id}) 待批 ${pending} 份`);
      }
    }
    return lines.join('\n') || '暂无';
  } catch (e) {
    return '暂无';
  }
};

const buildPreamble = async (userText: string): Promise<string> => {
  const roleText = userStore.isSuper() ? '超级管理员' : (userStore.role === 'admin' ? '管理员' : '出题人');
  const pending = await getPendingSnapshot();
  const profileParts: string[] = [];
  if (userStore.name) profileParts.push(`真实姓名=${userStore.name}`);
  if (userStore.position) profileParts.push(`职务=${userStore.position}`);
  if (userStore.bio) profileParts.push(`背景与学科介绍=${userStore.bio}`);

  return [
    `[系统隐藏上下文 | 用户不可见]:`,
    `当前用户=${userStore.username}(${roleText})${profileParts.length ? '，个人画像=[' + profileParts.join(', ') + ']' : ''},`,
    `当前待阅试卷：${pending}`,
    `当前页面=AI助理全屏工作台。`,
    `请基于以上身份、用户背景与业务上下文回答老师的提问，称呼亲切自然，保持专业、扁平、无废话。`,
    '',
    `老师提问: ${userText}`
  ].join('\n');
};

const usePreset = (text: string) => {
  input.value = text;
  send();
};

const send = async (customText?: string): Promise<void> => {
  const isCustom = typeof customText === 'string';
  const text = (isCustom ? customText : input.value).trim();
  if (!text || sending.value) return;

  if (activeSessionId.value == null) {
    await startNewSession();
    if (activeSessionId.value == null) return;
  }
  const sessionId = activeSessionId.value as number;

  if (!isCustom) {
    input.value = '';
  }

  // 添加用户消息
  messages.value.push({ role: 'user', content: text });
  followScroll();

  // 添加 thinking 状态消息
  const streamingMsg: ChatMessage = {
    role: 'assistant',
    content: '',
    quote: text.length > 30 ? text.substring(0, 30) + '...' : text,
    isThinking: true,
    isStreaming: true
  };
  streamingMsg.id = `tmp_${Date.now()}`;
  messages.value.push(streamingMsg);
  followScroll();

  sending.value = true;
  const quote = streamingMsg.quote as string;

  try {
    const history = messages.value
      .filter(m => !m.isThinking && m.role !== 'system' && m !== streamingMsg)
      .slice(-6)
      .map(m => ({ role: m.role, content: m.content }));

    await loadExamCategories();
    const token = localStorage.getItem('tiku_tob_token') || '';

    const resp = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api'}/v1/admin/ai/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'X-Tenant-ID': userStore.tenantId || ''
      },
      body: JSON.stringify({
        message: text,
        display_text: text,
        history,
        session_id: sessionId
      })
    });

    if (!resp.ok) {
      if (resp.status === 401) {
        localStorage.removeItem('tiku_tob_token');
        window.location.href = '/admin/login';
        return;
      }
      throw new Error(`HTTP ${resp.status}`);
    }

    const reader = resp.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder('utf-8');
    let buf = '';
    let streamFailed = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buf += decoder.decode(value, { stream: true });
      const frames = buf.split('\n\n');
      buf = frames.pop() || '';

      for (const frame of frames) {
        const line = frame.trim();
        if (!line.startsWith('data:')) continue;

        let ev: any;
        try {
          ev = JSON.parse(line.slice(5).trim());
        } catch (e) {
          continue;
        }

        if (ev.type === 'delta' && ev.text) {
          streamingMsg.isThinking = false;
          streamingMsg.content += ev.text;
          followScroll();
        } else if (ev.type === 'action_required') {
          // 移除 thinking 消息，插入 actionCard 消息
          const idx = messages.value.indexOf(streamingMsg);
          if (idx !== -1) messages.value.splice(idx, 1);

          // 构建结构化 ActionCardPayload
          const actionTypeMap: Record<string, string> = {
            create_exam_draft: 'create_exam',
            create_question_draft: 'batch_questions',
            delete_exam: 'delete_exam'
          };
          const riskLevelMap: Record<string, 'low' | 'medium' | 'high'> = {
            high: 'high', medium: 'medium', low: 'low'
          };
          const toolName = ev.tool_name || 'unknown';
          const actionType = actionTypeMap[toolName] || 'sensitive_operation';
          const riskLevel = riskLevelMap[ev.risk_level] || 'medium';

          // 根据工具名构建 displayFields
          let displayFields: Array<{ label: string; value: string | number }> = [];
          const args = ev.arguments || {};
          if (toolName === 'create_exam_draft') {
            displayFields = [
              { label: '试卷标题', value: args.title || '—' },
              { label: '题型数量', value: `${(args.specs || []).reduce((s: number, sp: any) => s + (sp.count || 0), 0)} 题` },
              { label: '风险等级', value: riskLevel }
            ];
          } else if (toolName === 'create_question_draft') {
            displayFields = [
              { label: '出题材料', value: String(args.material || '').substring(0, 50) + (String(args.material || '').length > 50 ? '...' : '') },
              { label: '题目数量', value: args.count || 5 },
              { label: '风险等级', value: riskLevel }
            ];
          } else if (toolName === 'delete_exam') {
            displayFields = [
              { label: '操作类型', value: '删除试卷' },
              { label: '试卷ID', value: args.exam_id || '—' },
              { label: '风险等级', value: 'high' }
            ];
          }

          const actionCard: ActionCardPayload = {
            actionId: ev.tool_call_id || `action_${Date.now()}`,
            actionType,
            title: `确认：${riskLevel === 'high' ? '高' : riskLevel === 'medium' ? '中' : '低'}风险业务操作`,
            summary: ev.message || `请确认是否执行 ${toolName}`,
            riskLevel,
            displayFields,
            rawParams: args,
            status: 'pending'
          };

          messages.value.push({
            role: 'assistant',
            content: ev.message || '',
            quote,
            actionCard,
            actionRequired: true,
            toolName,
            toolCallId: ev.tool_call_id || `action_${Date.now()}`,
            arguments: args,
            riskLevel,
            actionResolved: false,
            ragSources: []
          } as ChatMessage);
          followScroll();
        } else if (ev.type === 'done') {
          streamingMsg.isThinking = false;
          streamingMsg.isStreaming = false;
          if (ev.assistant_message_id) streamingMsg.id = ev.assistant_message_id;
          if (ev.user_message_id) {
            const um = [...messages.value].reverse().find(m => m.role === 'user' && !m.id);
            if (um) um.id = ev.user_message_id;
          }
          // 解析可能的卡片
          const parsed = extractActionBlocks(streamingMsg.content || '');
          streamingMsg.content = parsed.text || '(无回复)';
          streamingMsg.actionCard = parsed.card;
          streamingMsg.actionList = parsed.list;
          streamingMsg.examCard = parsed.examCard;
          followScroll();
        } else if (ev.type === 'error') {
          streamFailed = true;
          streamingMsg.isThinking = false;
          streamingMsg.isStreaming = false;
          streamingMsg.content = `AI 服务响应超时或未开启，请稍后再试${ev.message ? '：' + ev.message : ''}`;
        }
      }

      if (streamFailed) break;
    }

    if (!streamFailed) {
      const parsed = extractActionBlocks(streamingMsg.content || '');
      streamingMsg.content = parsed.text || '(无回复)';
      streamingMsg.actionCard = parsed.card;
      streamingMsg.actionList = parsed.list;
      streamingMsg.examCard = parsed.examCard;
    }

    // 刷新会话列表
    await refreshSessions();
    followScroll();

  } catch (e: any) {
    const idx = messages.value.indexOf(streamingMsg);
    if (idx !== -1) messages.value.splice(idx, 1);

    const detail = e?.response?.data?.detail || e?.message || '';
    if (String(detail).includes('额度')) {
      messages.value.push({ role: 'assistant', content: '今日 AI 额度已用尽，请联系管理员分配或补充。' });
    } else {
      messages.value.push({ role: 'assistant', content: 'AI 服务响应超时或未开启，请稍后再试。' });
    }
  } finally {
    sending.value = false;
    followScroll();
  }
};

const isToolOperation = (msg: ChatMessage): boolean => {
  if (msg.actionRequired) return true;
  const toolName = msg.toolName || msg.actionCard?.actionType || '';
  return ['create_exam', 'create_exam_draft', 'batch_questions', 'create_question_draft', 'delete_exam', 'delete_question'].includes(toolName);
};

const toToolCallMessage = (msg: ChatMessage): any => {
  const toolName = msg.toolName || (msg.actionCard?.actionType === 'create_exam' ? 'create_exam_draft' : (msg.actionCard?.actionType === 'batch_questions' ? 'create_question_draft' : msg.actionCard?.actionType)) || 'create_exam_draft';
  const args = msg.arguments || msg.actionCard?.rawParams || {};
  return {
    id: msg.id,
    role: 'assistant',
    actionRequired: true,
    toolName,
    toolCallId: msg.toolCallId || msg.actionCard?.actionId || '',
    arguments: args,
    riskLevel: msg.riskLevel || msg.actionCard?.riskLevel || 'medium',
    actionResolved: msg.actionResolved || msg.actionCard?.status === 'confirmed',
    content: msg.content || msg.actionCard?.summary || ''
  };
};

const handleToolConfirm = async (toolMsg: any): Promise<void> => {
  const targetMsg = messages.value.find(m => m.id === toolMsg.id || m.toolCallId === toolMsg.toolCallId || m.actionCard?.actionId === toolMsg.toolCallId);
  const toolName = toolMsg.toolName || 'create_exam_draft';
  const args = toolMsg.arguments || {};
  if (sending.value) return;
  sending.value = true;
  try {
    const res: any = await request.post('/api/v1/admin/ai/chat/execute_tool', {
      tool_name: toolName,
      arguments: args,
      tool_call_id: String(toolMsg.toolCallId || ''),
      message_id: toolMsg.id ?? null
    });

    if (targetMsg) {
      targetMsg.actionResolved = true;
      if (targetMsg.actionCard) targetMsg.actionCard.status = 'confirmed';
    }

    if ((toolName === 'create_exam_draft' || toolName === 'create_exam') && res.data?.exam_id) {
      ElMessage.success(`试卷草稿创建成功，ID: ${res.data.exam_id}`);
    } else if ((toolName === 'create_question_draft' || toolName === 'batch_questions') && res.data?.question_ids) {
      ElMessage.success(`已成功生成 ${res.data.count} 道题目草稿`);
    } else if (toolName === 'delete_exam' && res.data?.deleted_id) {
      ElMessage.success(`试卷已删除: ${res.data.title}`);
    } else if (toolName === 'delete_question' && res.data?.deleted_question_id) {
      ElMessage.success(`题目已删除: #${res.data.deleted_question_id}`);
    } else {
      ElMessage.success('操作已执行');
    }

    const systemMsg = `[系统消息]: 我已批准并执行了操作 ${toolName}，后端返回的结果是：${JSON.stringify(res.data || res)}`;
    await send(systemMsg);
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '执行失败');
  } finally {
    sending.value = false;
  }
};

const handleToolCancel = async (toolMsg: any): Promise<void> => {
  const targetMsg = messages.value.find(m => m.id === toolMsg.id || m.toolCallId === toolMsg.toolCallId || m.actionCard?.actionId === toolMsg.toolCallId);
  if (targetMsg) {
    targetMsg.actionResolved = true;
    if (targetMsg.actionCard) targetMsg.actionCard.status = 'cancelled';
  }
  const toolName = toolMsg.toolName || '未知操作';
  const systemMsg = `[系统消息]: 我拒绝了操作 ${toolName} 的执行。`;
  await send(systemMsg);
};

const confirmToolCall = async (msg: ChatMessage): Promise<void> => {
  if (msg.actionCard?.status !== 'pending' || sending.value) return;
  sending.value = true;
  try {
    const toolName = msg.actionCard?.actionType || '';
    const res: any = await request.post('/api/v1/admin/ai/chat/execute_tool', {
      tool_name: toolName,
      arguments: msg.actionCard?.rawParams || {},
      tool_call_id: msg.id?.toString() || '',
      message_id: msg.id ?? null
    });

    if (msg.actionCard) msg.actionCard.status = 'confirmed';

    if ((toolName === 'create_exam_draft' || toolName === 'create_exam') && res.data?.exam_id) {
      ElMessage.success(`试卷草稿创建成功，ID: ${res.data.exam_id}`);
    } else if ((toolName === 'create_question_draft' || toolName === 'batch_questions') && res.data?.question_ids) {
      ElMessage.success(`已成功生成 ${res.data.count} 道题目草稿`);
    } else if (toolName === 'delete_exam' && res.data?.deleted_id) {
      ElMessage.success(`试卷已删除: ${res.data.title}`);
    } else {
      ElMessage.success('操作已执行');
    }

    const systemMsg = `[系统消息]: 我已批准并执行了操作 ${toolName}，后端返回的结果是：${JSON.stringify(res.data || res)}`;
    await send(systemMsg);

  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '执行失败');
  } finally {
    sending.value = false;
  }
};

const cancelToolCall = async (msg: ChatMessage): Promise<void> => {
  if (msg.actionCard) msg.actionCard.status = 'cancelled';
  const toolName = msg.actionCard?.actionType || '未知操作';
  const systemMsg = `[系统消息]: 我拒绝了操作 ${toolName} 的执行。`;
  await send(systemMsg);
};

// 新的统一处理器（替代旧的 confirmToolCall / cancelToolCall）
const handleActionConfirm = async (card: ActionCardPayload): Promise<void> => {
  // 找到对应的消息
  const msg = messages.value.find(m => m.actionCard === card);
  if (!msg) return;
  await confirmToolCall(msg);
};

const handleActionCancel = (card: ActionCardPayload): void => {
  const msg = messages.value.find(m => m.actionCard === card);
  if (msg) cancelToolCall(msg);
};

const downloadExamCard = async (card: ExamCardData): Promise<void> => {
  try {
    const token = localStorage.getItem('tiku_tob_token') || '';
    const res = await fetch(card.downloadUrl, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('下载失败');

    let finalFileName = `${card.title || '试卷'}.docx`;
    const disposition = res.headers.get('Content-Disposition') || '';
    if (disposition) {
      const fnMatchStar = disposition.match(/filename\*=UTF-8''([^;]+)/i);
      if (fnMatchStar && fnMatchStar[1]) {
        try {
          finalFileName = decodeURIComponent(fnMatchStar[1]);
        } catch (e) { /* 保留默认 */ }
      } else {
        const fnMatch = disposition.match(/filename="?([^";]+)"?/i);
        if (fnMatch && fnMatch[1]) {
          finalFileName = fnMatch[1];
        }
      }
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = finalFileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    ElMessage.success(`《${card.title}》已成功下载为 Word 试卷文档`);
  } catch (e: any) {
    ElMessage.error(e?.message || '试卷导出失败，请重试');
  }
};

const showSource = (source: any): void => {
  activeSource.value = source;
  srcVisible.value = true;
};

const submitFeedback = async (rating: 'up' | 'down'): Promise<void> => {
  try {
    await request.post('/api/v1/admin/ai/chat/feedback', {
      rating
    });
    ElMessage.success('感谢您的反馈');
  } catch (e) {
    ElMessage.error('反馈提交失败');
  }
};

const handleDrawerGraded = (): void => {
  // 刷新待阅快照
};

onMounted(() => {
  userStore.loadProfile();
  initCloud();
});
</script>

<style scoped>
.ai-tab-container {
  display: flex;
  height: calc(100vh - 100px);
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  overflow: hidden;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.chat-header {
  height: 56px;
  padding: 0 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.model-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
  color: #1e293b;
}

.sparkle {
  color: #7c3aed;
}

.messages-wrap {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
}

.history-loader {
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
  padding: 8px 0 12px;
}

.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.welcome-badge {
  background: #eff6ff;
  color: #1d4ed8;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 12px;
}

.welcome-screen h2 {
  font-size: 20px;
  color: #0f172a;
  margin-bottom: 28px;
}

.presets-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  max-width: 720px;
}

.preset-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-card:hover {
  border-color: #0284c7;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.08);
}

.card-icon {
  font-size: 20px;
  margin-bottom: 8px;
}

.card-title {
  font-weight: 700;
  color: #1e293b;
  font-size: 14px;
  margin-bottom: 4px;
}

.card-sub {
  font-size: 12px;
  color: #64748b;
}

.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  max-width: 85%;
  margin-bottom: 20px;
}

.thinking-indicator .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #0284c7;
  animation: bounce 1.4s infinite ease-in-out both;
}

.thinking-indicator .dot:nth-child(1) { animation-delay: -0.32s; }
.thinking-indicator .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.input-container {
  padding: 16px 32px 24px;
  border-top: 1px solid #e2e8f0;
}

.input-box {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 8px 12px;
  margin-bottom: 8px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tip-text {
  font-size: 12px;
  color: #94a3b8;
}

.send-btn {
  width: 80px;
  border-radius: 8px;
}
</style>
