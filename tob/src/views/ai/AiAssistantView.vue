<!--
 * [变更日志]
 * 修改时间：2026-09-07 01:10:00
 * AI模型：Gemini 系列
 * 修改内容：[新建独立 Tab 页 AI 助理组件 (类 DeepSeek / ChatGPT 极简工作台风格): 支持多会话切换/新建对话/前端状态快照注入/Markdown 风格回复与快捷复制]
-->
<template>
  <div class="ai-tab-container">
    <!-- 左侧会话历史侧边栏 -->
    <div class="session-sidebar">
      <div class="new-chat-btn" @click="startNewSession">
        <el-icon><Plus /></el-icon>
        <span>新建对话</span>
      </div>

      <div class="session-list">
        <div
          v-for="s in sessions"
          :key="s.id"
          class="session-item"
          :class="{ active: s.id === activeSessionId }"
          @click="selectSession(s.id)"
        >
          <el-icon class="item-icon"><ChatDotRound /></el-icon>
          <span class="session-title">{{ s.title || '新对话' }}</span>
          <el-icon class="del-icon" @click.stop="deleteSession(s.id)"><Delete /></el-icon>
        </div>
      </div>

      <div class="quota-footer">
        <div class="quota-card">
          <span>🔋 今日 AI 额度余额</span>
          <strong style="color: #0284c7; font-size: 16px">{{ userStore.quotaRemaining }} 次</strong>
        </div>
      </div>
    </div>

    <!-- 右侧聊天工作台主区域 -->
    <div class="chat-main">
      <div class="chat-header">
        <div class="model-badge">
          <span class="sparkle"><el-icon><MagicStick /></el-icon></span>
          <span class="model-name">TiKu AI Copilot 智能助管</span>
        </div>
        <div style="font-size: 13px; color: #64748b">
          已连接算法模型：Agnes 2.5 Flash / SenseNova
        </div>
      </div>

      <!-- 消息会话区域 -->
      <div class="messages-wrap" ref="messagesWrapRef">
        <div v-if="currentMessages.length === 0" class="welcome-screen">
          <div class="welcome-badge"><el-icon style="vertical-align: middle; margin-right: 4px;"><MagicStick /></el-icon>智能出题与教务数字助理</div>
          <h2>你好，{{ userStore.username }}！有什么我可以帮你的？</h2>
          <div class="presets-grid">
            <div class="preset-card" @click="usePreset('帮我生成一份包含3道单选、2道判断的消防安全测试卷，难度中等')">
              <div class="card-icon">📝</div>
              <div class="card-title">一键智能组卷</div>
              <div class="card-sub">生成包含指定题型构成的消防测试卷</div>
            </div>
            <div class="preset-card" @click="usePreset('帮我出 5 道关于金融风险控制的单选题，难度偏难，带解析')">
              <div class="card-icon">🎯</div>
              <div class="card-title">快速生成题目</div>
              <div class="card-sub">出 5 道金融风控单选题并附带参考解析</div>
            </div>
            <div class="preset-card" @click="usePreset('我今天有哪些待办工作？有哪些需要批改的试卷？')">
              <div class="card-icon">📊</div>
              <div class="card-title">查询工作上帝视角</div>
              <div class="card-sub">分析当前试卷待批改与管理状态</div>
            </div>
          </div>
        </div>

        <template v-else>
          <div v-for="(m, idx) in currentMessages" :key="idx" class="message-row" :class="m.role">
            <div class="avatar-cell">
              <div v-if="m.role === 'user'" class="user-avatar">
                {{ userStore.username.substring(0, 1).toUpperCase() }}
              </div>
              <div v-else class="ai-avatar"><el-icon><MagicStick /></el-icon></div>
            </div>
            <div class="content-cell">
              <div class="sender-name">{{ m.role === 'user' ? userStore.username : 'AI 助理' }}</div>
              <div class="bubble-content markdown-body" v-if="!m.actionRequired || m.content">
                <template v-if="m.isThinking">
                  <div class="thinking-spinner">
                    <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                    <span style="margin-left: 8px; color: #64748b; font-size: 13px;">正在思考中...</span>
                  </div>
                </template>
                <template v-else>
                  <div v-html="renderMarkdown(m.content)"></div>
                  
                  <!-- 操作栏 (只有真正的 AI 回复才显示) -->
                  <div class="message-actions" v-if="m.role === 'assistant' && !m.isThinking">
                    <el-tooltip content="复制内容" placement="top">
                      <span class="action-icon" @click="copyToClipboard(m.content)"><el-icon><DocumentCopy /></el-icon></span>
                    </el-tooltip>
                    <el-tooltip content="重新生成" placement="top">
                      <span class="action-icon" @click="regenerateMessage(session)"><el-icon><Refresh /></el-icon></span>
                    </el-tooltip>
                    <el-divider direction="vertical" />
                    <el-tooltip content="有用" placement="top">
                      <span class="action-icon" @click="submitFeedback(m.content, 'up')" style="font-size: 14px;">
                        <svg viewBox="0 0 24 24" width="1em" height="1em" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
                      </span>
                    </el-tooltip>
                    <el-tooltip content="无用" placement="top">
                      <span class="action-icon" @click="submitFeedback(m.content, 'down')" style="font-size: 14px;">
                        <svg viewBox="0 0 24 24" width="1em" height="1em" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"></path></svg>
                      </span>
                    </el-tooltip>
                  </div>
                </template>
              </div>
              
              <div class="action-card" v-if="m.actionRequired">
                <div class="action-header" :class="[m.actionResolved ? 'resolved' : '', m.riskLevel === 'high' ? 'high-risk' : 'low-risk']">
                  <span class="header-icon"><el-icon><MagicStick /></el-icon></span> 
                  <span class="header-title">确认: {{ m.riskLevel === 'high' ? '高' : '低' }}风险业务操作</span> 
                  <span class="header-badge" v-if="!m.actionResolved">待确认</span>
                  <span class="header-badge resolved" v-else>已处理</span>
                </div>
                <div class="action-body">
                  <div class="action-desc" v-if="!m.content">
                    请确认是否执行刚才的操作 ({{ m.toolName }})。
                  </div>
                  <div class="action-desc" v-else>
                    风险等级: <span style="font-weight:600;" :style="{ color: m.riskLevel === 'high' ? '#ef4444' : '#3b82f6' }">{{ m.riskLevel || 'unknown' }}</span><br/>
                    有效期: 5 分钟内
                  </div>
                  <div class="action-code">
                    <pre>{{ JSON.stringify(m.arguments, null, 2) }}</pre>
                  </div>
                  <div class="action-footer" v-if="!m.actionResolved">
                    <button class="btn-confirm" @click="executeAction(m, session)">确认执行</button>
                    <button class="btn-cancel" @click="cancelAction(m, session)">取消</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 底部输入框区域 -->
      <div class="input-container">
        <div class="input-box">
          <el-input
            v-model="input"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 6 }"
            placeholder="给 AI 助理发送消息... (Enter 发送，Shift + Enter 换行)"
            @keydown.enter.exact.prevent="send"
            :disabled="sending"
          />
          <div class="input-actions">
            <span class="tip-text">按 Enter 发送</span>
            <el-button type="primary" class="send-btn" :loading="sending" :disabled="!input.trim()" @click="send">
              发送
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Plus, ChatDotRound, Delete, MagicStick, DocumentCopy, Refresh } from '@element-plus/icons-vue';
import { marked } from 'marked';
import request from '../../utils/request';
import { useUserStore } from '../../store/user';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  isThinking?: boolean;
  actionRequired?: boolean;
  toolName?: string;
  toolCallId?: string;
  arguments?: any;
  riskLevel?: string;
  actionResolved?: boolean;
}

interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  updatedAt: number;
}

const route = useRoute();
const userStore = useUserStore();
const input = ref('');
const sending = ref(false);
const messagesWrapRef = ref<HTMLElement | null>(null);

const sessions = ref<ChatSession[]>([]);
const activeSessionId = ref<string>('');

const currentSession = computed(() =>
  sessions.value.find((s) => s.id === activeSessionId.value)
);

const currentMessages = computed(() =>
  currentSession.value ? currentSession.value.messages : []
);

const saveSessions = () => {
  localStorage.setItem('tiku_ai_sessions', JSON.stringify(sessions.value));
};

const loadSessions = () => {
  try {
    const raw = localStorage.getItem('tiku_ai_sessions');
    if (raw) {
      sessions.value = JSON.parse(raw);
    }
  } catch (e) {
    sessions.value = [];
  }
  if (sessions.value.length === 0) {
    startNewSession();
  } else {
    activeSessionId.value = sessions.value[0].id;
  }
};

const startNewSession = () => {
  const newId = 'session_' + Date.now();
  const newSession: ChatSession = {
    id: newId,
    title: '新对话',
    messages: [],
    updatedAt: Date.now()
  };
  sessions.value.unshift(newSession);
  activeSessionId.value = newId;
  saveSessions();
};

const selectSession = (id: string) => {
  activeSessionId.value = id;
};

const deleteSession = (id: string) => {
  sessions.value = sessions.value.filter((s) => s.id !== id);
  if (activeSessionId.value === id) {
    if (sessions.value.length > 0) {
      activeSessionId.value = sessions.value[0].id;
    } else {
      startNewSession();
    }
  }
  saveSessions();
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesWrapRef.value) {
    messagesWrapRef.value.scrollTop = messagesWrapRef.value.scrollHeight;
  }
};

// 极简轻量 Markdown / HTML 转义渲染
const renderMarkdown = (text: string) => {
  if (!text) return '';
  return marked.parse(text) as string;
};

const buildPreamble = (userText: string) => {
  const roleText = userStore.role === 'super_admin' ? '超级管理员' : (userStore.role === 'admin' ? '管理员' : '出题人');
  return [
    `[系统隐藏上下文 | 用户不可见]:`,
    `当前用户=${userStore.username}(${roleText}), 剩余AI额度=${userStore.quotaRemaining}次,`,
    `当前页面=AI助理全屏工作台。`,
    `请基于以上身份与业务上下文回答老师的问题; 回答保持专业、扁平、无废话。`,
    ``
  ].join('\n') + `\n老师提问: ${userText}`;
};

const usePreset = (text: string) => {
  input.value = text;
  send();
};

const send = async () => {
  const text = input.value.trim();
  if (!text || sending.value || !currentSession.value) return;

  const session = currentSession.value;
  input.value = '';
  session.messages.push({ role: 'user', content: text });

  if (session.messages.length === 1 || session.title === '新对话') {
    session.title = text.substring(0, 16);
  }
  session.updatedAt = Date.now();
  saveSessions();
  scrollToBottom();

  sending.value = true;
  try {
    const history = session.messages
      .filter(m => !m.isThinking && !m.actionRequired && m.role !== 'system')
      .slice(-6, -1)
      .map((m) => ({ role: m.role, content: m.content }));
      
    // 增加一条思考中的假消息
    const thinkingMsg: ChatMessage = { role: 'assistant', content: '', isThinking: true };
    session.messages.push(thinkingMsg);
    scrollToBottom();
    
    const res: any = await request.post('/api/v1/admin/ai/chat', {
      message: buildPreamble(text),
      history
    }, { timeout: 120000 });

    // 移除所有假消息 (处理 proxy 对象无法 === 比较的问题)
    session.messages = session.messages.filter(m => !m.isThinking);

    userStore.quotaRemaining = res.quota_remaining ?? userStore.quotaRemaining;
    if (res.type === 'action_required') {
      session.messages.push({
        role: 'assistant',
        content: res.message,
        actionRequired: true,
        toolName: res.tool_name,
        toolCallId: res.tool_call_id,
        arguments: res.arguments,
        riskLevel: res.risk_level || 'high',
        actionResolved: false
      });
    } else {
      session.messages.push({ role: 'assistant', content: res.reply || '(无回复)' });
    }
    saveSessions();
    scrollToBottom();
  } catch (e: any) {
    // 移除假消息确保安全
    session.messages = session.messages.filter(m => !m.isThinking);
    
    const detail = e?.response?.data?.detail || '';
    if (String(detail).includes('额度')) {
      session.messages.push({ role: 'assistant', content: '今日 AI 额度已用尽，请联系管理员分配或补充。' });
    } else {
      session.messages.push({ role: 'assistant', content: 'AI 服务响应超时或未开启，请稍后再试。' });
    }
  } finally {
    sending.value = false;
  }
};

const executeAction = async (m: ChatMessage, session: ChatSession) => {
  if (sending.value || m.actionResolved) return;
  sending.value = true;
  try {
    const res: any = await request.post('/api/v1/admin/ai/chat/execute_tool', {
      tool_name: m.toolName,
      arguments: m.arguments,
      tool_call_id: m.toolCallId
    });
    m.actionResolved = true;
    ElMessage.success('操作已执行');
    
    // 把结果当做一条隐形的系统提示再次发给 AI 让他知道结果
    input.value = `[系统消息]: 我已批准并执行了操作 ${m.toolName}，后端返回的结果是：${JSON.stringify(res)}`;
    await send();
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '执行失败');
  } finally {
    sending.value = false;
  }
};

const cancelAction = async (m: ChatMessage, session: ChatSession) => {
  m.actionResolved = true;
  saveSessions();
  
  input.value = `[系统消息]: 我拒绝了操作 ${m.toolName} 的执行。`;
  await send();
};

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success('已复制到剪贴板');
  } catch (err) {
    ElMessage.error('复制失败');
  }
};

const regenerateMessage = async (session: ChatSession) => {
  if (sending.value) return;
  // 找到倒数第一个 user 消息
  const lastUserIndex = [...session.messages].reverse().findIndex(m => m.role === 'user');
  if (lastUserIndex === -1) return;
  const realIndex = session.messages.length - 1 - lastUserIndex;
  
  const userMessage = session.messages[realIndex].content;
  // 截断该消息之后的所有记录
  session.messages = session.messages.slice(0, realIndex);
  
  input.value = userMessage;
  await send();
};

const submitFeedback = async (content: string, rating: 'up' | 'down') => {
  try {
    await request.post('/api/v1/admin/ai/chat/feedback', {
      message_content: content,
      rating: rating
    });
    ElMessage.success('感谢您的反馈！');
  } catch (err) {
    ElMessage.error('反馈提交失败');
  }
};

onMounted(() => {
  loadSessions();
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

.session-sidebar {
  width: 240px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: white;
  padding: 10px 16px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.new-chat-btn:hover {
  opacity: 0.9;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  margin-top: 16px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  color: #475569;
  cursor: pointer;
  margin-bottom: 4px;
  font-size: 13px;
  transition: all 0.15s;
}

.session-item:hover {
  background: #e2e8f0;
}

.session-item.active {
  background: #e0f2fe;
  color: #0369a1;
  font-weight: 600;
}

.session-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.del-icon {
  display: none;
  color: #94a3b8;
}

.session-item:hover .del-icon {
  display: block;
}

.del-icon:hover {
  color: #ef4444;
}

.quota-footer {
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.quota-card {
  background: #ffffff;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-size: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.send-btn {
  width: 80px;
  border-radius: 8px;
}

.action-card {
  margin-top: 12px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #fee2e2;
  width: 100%;
  max-width: 400px;
}

.action-header.high-risk {
  background: linear-gradient(135deg, #fecaca 0%, #fff1f2 100%);
  border-bottom: 1px solid #fee2e2;
}

.action-header.low-risk {
  background: linear-gradient(135deg, #bfdbfe 0%, #eff6ff 100%);
  border-bottom: 1px solid #dbeafe;
}

.action-header {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-header.resolved {
  background: linear-gradient(135deg, #d1fae5 0%, #ecfdf5 100%);
  border-bottom-color: #d1fae5;
}

.header-icon {
  font-size: 16px;
}

.header-title {
  font-weight: 700;
  color: #1e293b;
  font-size: 14px;
}

.header-badge {
  background: #f87171;
  color: #fff;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  margin-left: auto;
}

.header-badge.resolved {
  background: #10b981;
}

.action-body {
  padding: 16px;
}

.action-desc {
  font-size: 13px;
  color: #334155;
  line-height: 1.6;
  margin-bottom: 12px;
}

.action-code pre {
  margin: 0 0 16px 0;
  padding: 10px;
  background: #f8fafc;
  border-radius: 6px;
  font-size: 12px;
  color: #475569;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.action-footer {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-confirm {
  width: 100%;
  padding: 10px;
  background: #ef4444;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-confirm:hover {
  background: #dc2626;
}

.btn-cancel {
  width: 100%;
  padding: 10px;
  background: #fff;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #f8fafc;
  border-color: #94a3b8;
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

.messages-wrap {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
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

.message-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #0284c7;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.ai-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.content-cell {
  flex: 1;
}

.sender-name {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 4px;
}

.bubble-content {
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  color: #1e293b;
  font-size: 14px;
  max-width: 85%;
  border: 1px solid #f1f5f9;
}

.message-row.user .bubble-content {
  background: #e0f2fe;
  border-color: #bae6fd;
  color: #0369a1;
}

.input-container {
  padding: 16px 32px 24px;
}

.input-box {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 8px 12px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.tip-text {
  font-size: 12px;
  color: #94a3b8;
}

.send-btn {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  border: none;
}
</style>
