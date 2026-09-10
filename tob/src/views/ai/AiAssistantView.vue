<!--
 * [变更日志]
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
          <div class="welcome-badge">
            <el-icon style="vertical-align: middle; margin-right: 4px;"><MagicStick /></el-icon>
            智能出题与教务数字助手
          </div>
          <h2>你好，{{ userStore.username }}！有什么我可以帮你的？</h2>
          <div class="presets-grid">
            <div class="preset-card" @click="usePreset('帮我生成一份包含5道单选题3道判断的消防安全测试卷，难度中等')">
              <div class="card-icon">📝</div>
              <div class="card-title">一键智能组卷</div>
              <div class="card-sub">生成包含指定题型构成的消防测试卷</div>
            </div>
            <div class="preset-card" @click="usePreset('帮我出5道关于金融风险控制的单选题，难度偏难，带解析')">
              <div class="card-icon">🎯</div>
              <div class="card-title">快速生成题目</div>
              <div class="card-sub">出5道金融风控单选题并附带参考解析</div>
            </div>
            <div class="preset-card" @click="usePreset('我今天有哪些待办工作？有哪些需要批改的试卷？')">
              <div class="card-icon">📊</div>
              <div class="card-title">查询工作状态</div>
              <div class="card-sub">分析当前试卷待批改与管理状态</div>
            </div>
            <div class="preset-card" @click="usePreset('帮我查看当前企业的知识库里有哪些文档')">
              <div class="card-icon">📚</div>
              <div class="card-title">知识库检索</div>
              <div class="card-sub">查询企业知识库中的文档资料</div>
            </div>
            <div class="preset-card" @click="usePreset('帮我创建一个关于安全生产的考试，包含单选和多选题')">
              <div class="card-icon">✅</div>
              <div class="card-title">创建新考试</div>
              <div class="card-sub">基于材料智能生成安全生产考试试卷</div>
            </div>
            <div class="preset-card" @click="usePreset('查询工作上帝视角')">
              <div class="card-icon">🔍</div>
              <div class="card-title">查询工作上帝视角</div>
              <div class="card-sub">分析当前试卷待批改与管理状态</div>
            </div>
          </div>
        </div>

        <template v-for="(m, idx) in currentMessages" :key="idx">
          <!-- 普通消息气泡 -->
          <MessageBubble
            v-if="!m.actionRequired && !m.actionCard && !m.actionList && !m.examCard"
            :role="m.role"
            :content="m.content"
            :username="userStore.username"
            :quote="m.quote"
            :is-thinking="m.isThinking"
            :rag-sources="m.ai_rag_sources || []"
            @show-source="showSource"
            @feedback="submitFeedback"
          />

          <!-- 工具调用确认卡 -->
          <ToolCallCard
            v-else-if="m.actionRequired || m.actionCard || m.actionList"
            :message="m"
            :categories="examCategories"
            @confirm="confirmToolCall"
            @cancel="cancelToolCall"
          />

          <!-- 试卷导出卡 -->
          <ExamCard
            v-else-if="m.examCard"
            :card="m.examCard"
            :active="false"
            @download="downloadExamCard"
          />
        </template>

        <div v-if="sending" class="thinking-indicator">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          <span style="margin-left: 8px; color: #64748b; font-size: 13px;">AI 正在思考...</span>
        </div>
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
import { ref, computed, nextTick, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { MagicStick } from '@element-plus/icons-vue';
import { useUserStore } from '../../store/user';
import request from '../../utils/request';
import SessionSidebar from './components/SessionSidebar.vue';
import MessageBubble from './components/MessageBubble.vue';
import ToolCallCard from './components/ToolCallCard.vue';
import ExamCard from './components/ExamCard.vue';
import TraceDrawer from '../resources/components/TraceDrawer.vue';
import GradingDrawer from '../exams/components/GradingDrawer.vue';

interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  isThinking?: boolean;
  quote?: string;
  actionRequired?: boolean;
  toolName?: string;
  toolCallId?: string;
  arguments?: any;
  riskLevel?: string;
  actionResolved?: boolean;
  actionCard?: any;
  actionList?: any[];
  examCard?: ExamCardData | null;
  ai_rag_sources?: any[];
}

interface ExamCardData {
  type: string;
  exam_id: number;
  title: string;
  total_score: number;
  question_count: number;
  download_url: string;
  created_at?: string;
}

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

const currentMessages = computed(() => messages.value);

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
  await refreshSessions();
  if (sessions.value.length === 0) {
    await startNewSession();
    return;
  }
  activeSessionId.value = sessions.value[0].id;
  await loadMessages(activeSessionId.value as number);
  scrollToBottom();
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
    const res: any = await request.get('/api/v1/admin/categories', { params: { target_type: 'exam' } });
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
    isThinking: true
  };
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
    const preamble = await buildPreamble(text);
    const token = localStorage.getItem('tiku_tob_token') || '';

    const resp = await fetch(`${import.meta.env.VITE_API_BASE_URL || '/api'}/v1/admin/ai/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message: preamble,
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
          // 移除 thinking 消息，插入工具确认卡
          const idx = messages.value.indexOf(streamingMsg);
          if (idx !== -1) messages.value.splice(idx, 1);

          messages.value.push({
            role: 'assistant',
            content: ev.message || '',
            quote,
            actionRequired: true,
            toolName: ev.tool_name,
            toolCallId: ev.tool_call_id,
            arguments: ev.arguments,
            riskLevel: ev.risk_level || 'medium',
            actionResolved: false,
            ai_rag_sources: []
          });
          followScroll();
        } else if (ev.type === 'done') {
          streamingMsg.isThinking = false;
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

const confirmToolCall = async (msg: ChatMessage): Promise<void> => {
  if (msg.actionResolved || sending.value) return;
  sending.value = true;
  try {
    const res: any = await request.post('/api/v1/admin/ai/chat/execute_tool', {
      tool_name: msg.toolName,
      arguments: msg.arguments,
      tool_call_id: msg.toolCallId,
      message_id: msg.id ?? null
    });

    msg.actionResolved = true;

    if (msg.toolName === 'create_exam_draft' && res.data?.exam_id) {
      ElMessage.success(`试卷草稿创建成功，ID: ${res.data.exam_id}`);
    } else if (msg.toolName === 'create_question_draft' && res.data?.question_ids) {
      ElMessage.success(`已成功生成 ${res.data.count} 道题目草稿`);
    } else if (msg.toolName === 'delete_exam' && res.data?.deleted_id) {
      ElMessage.success(`试卷已删除: ${res.data.title}`);
    } else {
      ElMessage.success('操作已执行');
    }

    // 发送系统回执给 AI
    const systemMsg = `[系统消息]: 我已批准并执行了操作 ${msg.toolName}，后端返回的结果是：${JSON.stringify(res.data || res)}`;
    await send(systemMsg);

  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '执行失败');
  } finally {
    sending.value = false;
  }
};

const cancelToolCall = async (msg: ChatMessage): Promise<void> => {
  msg.actionResolved = true;
  const systemMsg = `[系统消息]: 我拒绝了操作 ${msg.toolName} 的执行。`;
  await send(systemMsg);
};

const downloadExamCard = async (card: ExamCardData): Promise<void> => {
  try {
    const token = localStorage.getItem('tiku_tob_token') || '';
    const res = await fetch(card.download_url, {
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
