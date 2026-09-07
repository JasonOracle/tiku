<!--
  * [变更日志]
  * 修改时间：2026-09-07 01:10:00
  * AI模型：Gemini 系列
  * 修改内容：[新建独立 Tab 页 AI 助理组件 (现代交互工作台风格): 支持多会话切换/新建对话/前端状态快照注入/Markdown 风格回复与快捷复制]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[v1.2 Step5: 全站脱敏(AI智能助管/AI智算引擎)/现代气泡+引用条/action_card 待确认卡片/action_list 路由卡片+权限白名单+批阅抽屉联动]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[SSE 流式对话: /chat/stream 打字机逐字输出，消除整段等待感]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[风险三档卡片: medium 蓝色轻确认 + 新建题目结构化题面预览]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[企业级会话持久化: 云端会话漫游 + 游标分页 + 视口锚定 + 打字吸底锁，彻底移除 localStorage]
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
          <span class="session-title" @dblclick.stop="renameSession(s)">{{ s.title || '新对话' }}</span>
          <el-icon class="del-icon" @click.stop="deleteSession(s.id)"><Delete /></el-icon>
        </div>
      </div>

      <div class="quota-footer">
        <div class="quota-card">
          <span>今日 AI 额度余额</span>
          <strong style="color: #0284c7; font-size: 16px">{{ userStore.quotaRemaining }} 次</strong>
        </div>
      </div>
    </div>

    <!-- 右侧聊天工作台主区域 -->
    <div class="chat-main">
      <div class="chat-header">
        <div class="model-badge">
          <span class="sparkle"><el-icon><MagicStick /></el-icon></span>
          <span class="model-name">AI 智能助管</span>
        </div>
        <div style="font-size: 13px; color: #64748b">
          AI 智算引擎 · 私有业务上下文问答
        </div>
      </div>

      <!-- 消息会话区域 -->
      <div class="messages-wrap" ref="messagesWrapRef" @scroll="handleScroll">
        <div v-if="loadingMessages" class="history-loader">历史消息加载中...</div>
        <div v-if="currentMessages.length === 0 && !loadingMessages" class="welcome-screen">
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
              <div class="sender-name">{{ m.role === 'user' ? userStore.username : 'AI 智能助管' }}</div>
              <div class="bubble-content markdown-body" v-if="m.content && m.content.trim()">
                <div v-if="m.role === 'assistant' && m.quote" class="quote-bar">| 回复 全Ai系统: {{ m.quote }}</div>
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
                <div class="action-header" :class="[m.actionResolved ? 'resolved' : '', riskHeaderClass(m.riskLevel)]">
                  <span class="header-icon"><el-icon><MagicStick /></el-icon></span> 
                  <span class="header-title">确认: {{ riskLabel(m.riskLevel) }}风险业务操作</span> 
                  <span class="header-badge" v-if="!m.actionResolved">待确认</span>
                  <span class="header-badge resolved" v-else>已处理</span>
                </div>
                <div class="action-body">
                  <div class="action-desc" v-if="!m.content">
                    请确认是否执行刚才的操作 ({{ m.toolName }})。
                  </div>
                  <div class="action-desc" v-else>
                    风险等级: <span style="font-weight:600;" :style="{ color: m.riskLevel === 'high' ? '#ef4444' : '#0284c7' }">{{ riskLabel(m.riskLevel) }}风险</span><br/>
                    有效期: 5 分钟内
                  </div>
                  <!-- 组卷确认卡：题目全览 + 参数补全表单 -->
                  <div v-if="m.toolName === 'create_exam_draft'" class="exam-draft-card">
                    <div class="exam-draft-title">✨ AI 智能组卷确认卡</div>
                    <div class="exam-draft-summary">{{ examTypeSummary(m.arguments) }}</div>
                    <el-collapse>
                      <el-collapse-item
                        v-for="(q, qi) in (m.arguments?.questions || [])"
                        :key="qi"
                        :name="qi"
                        :title="`第 ${qi + 1} 题 · ${q.title}`"
                      >
                        <div class="draft-meta" style="margin-bottom: 6px">
                          <el-tag size="small" type="primary">{{ draftPreview(q).typeLabel }}</el-tag>
                          <span>{{ draftPreview(q).score }} 分</span>
                        </div>
                        <div
                          v-for="(opt, oi) in draftPreview(q).options"
                          :key="oi"
                          class="draft-opt"
                          :class="{ correct: opt.correct }"
                        >
                          <span class="draft-opt-key">{{ opt.label }}</span>
                          <span>{{ opt.text }}</span>
                          <span v-if="opt.correct" class="draft-opt-mark">✔</span>
                        </div>
                        <div class="draft-row" style="margin-top: 6px"><span class="draft-label">答案：</span>{{ draftPreview(q).answerText }}</div>
                      </el-collapse-item>
                    </el-collapse>
                    <el-form label-width="90px" size="small" style="margin-top: 12px">
                      <el-form-item label="试卷分类">
                        <el-select v-model="examFormOf(m).category_id" placeholder="选择试卷分类" style="width: 100%">
                          <el-option v-for="c in examCategories" :key="c.id" :label="c.name" :value="c.id" />
                        </el-select>
                      </el-form-item>
                      <el-form-item label="考试时间">
                        <el-date-picker
                          v-model="examFormOf(m).timeRange"
                          type="datetimerange"
                          range-separator="至"
                          start-placeholder="开始时间"
                          end-placeholder="结束时间"
                          format="YYYY-MM-DD HH:mm"
                          value-format="YYYY-MM-DDTHH:mm:ss"
                          style="width: 100%"
                        />
                      </el-form-item>
                      <el-form-item label="考试时长">
                        <div style="display: flex; align-items: center; gap: 12px">
                          <el-switch v-model="examFormOf(m).is_timed" />
                          <div v-if="examFormOf(m).is_timed" style="display: flex; align-items: center; gap: 6px">
                            <el-input-number v-model="examFormOf(m).time_limit" :min="1" :max="600" />
                            <span style="color: #64748b">分钟</span>
                          </div>
                          <span v-else style="color: #94a3b8">不限时长</span>
                        </div>
                      </el-form-item>
                      <el-form-item v-if="examHasShort(m)" label="AI 阅卷模式">
                        <el-radio-group v-model="examFormOf(m).grading_mode">
                          <el-radio label="ai_auto">AI 自动托管</el-radio>
                          <el-radio label="manual">人工全权批阅</el-radio>
                        </el-radio-group>
                      </el-form-item>
                    </el-form>
                    <div class="action-footer" v-if="!m.actionResolved">
                      <button class="btn-confirm-medium" @click="confirmExamDraft(m)">确认创建试卷</button>
                      <button class="btn-cancel" @click="cancelAction(m)">取消</button>
                    </div>
                    <div v-else class="action-desc">试卷草稿已创建，可前往<a class="exam-link" @click="goExams">试卷管理</a>查看。</div>
                  </div>
                  <!-- 新建题目：结构化题面预览（题干/选项/答案/解析），告别生硬 JSON -->
                  <div v-else-if="m.toolName === 'create_question_draft'" class="draft-preview">
                    <div class="draft-title">{{ draftPreview(m.arguments).title }}</div>
                    <div class="draft-meta">
                      <el-tag size="small" type="primary">{{ draftPreview(m.arguments).typeLabel }}</el-tag>
                      <span>难度 {{ draftPreview(m.arguments).difficulty }} · {{ draftPreview(m.arguments).score }} 分</span>
                    </div>
                    <div v-if="draftPreview(m.arguments).options.length" class="draft-opts">
                      <div
                        v-for="(opt, oi) in draftPreview(m.arguments).options"
                        :key="oi"
                        class="draft-opt"
                        :class="{ correct: opt.correct }"
                      >
                        <span class="draft-opt-key">{{ opt.label }}</span>
                        <span>{{ opt.text }}</span>
                        <span v-if="opt.correct" class="draft-opt-mark">✔</span>
                      </div>
                    </div>
                    <div class="draft-row"><span class="draft-label">正确答案：</span>{{ draftPreview(m.arguments).answerText }}</div>
                    <div v-if="draftPreview(m.arguments).explanation" class="draft-row"><span class="draft-label">解析：</span>{{ draftPreview(m.arguments).explanation }}</div>
                  </div>
                  <div v-else class="action-code">
                    <pre>{{ JSON.stringify(m.arguments, null, 2) }}</pre>
                  </div>
                  <div class="action-footer" v-if="!m.actionResolved && m.toolName !== 'create_exam_draft'">
                    <button :class="m.riskLevel === 'high' ? 'btn-confirm' : 'btn-confirm-medium'" @click="executeAction(m)">确认执行</button>
                    <button class="btn-cancel" @click="cancelAction(m)">取消</button>
                  </div>
                </div>
              </div>

              <!-- v1.2 Step5: 人机协同待确认卡片 (action_card 协议) -->
              <div class="action-card" v-if="m.actionCard">
                <div class="action-header" :class="[m.actionCard.resolved === 'done' ? 'resolved' : '', m.actionCard.riskLevel === 'high' ? 'high-risk' : 'low-risk']">
                  <span class="header-title">确认: {{ m.actionCard.title }} [{{ m.actionCard.resolved === 'done' ? '已执行' : '待确认' }}]</span>
                </div>
                <div class="action-body">
                  <div class="action-desc">
                    风险等级: <span style="font-weight:600;" :style="{ color: m.actionCard.riskLevel === 'high' ? '#ef4444' : '#3b82f6' }">{{ m.actionCard.riskLevel || 'medium' }}</span>
                  </div>
                  <div class="action-desc" v-for="(d, di) in m.actionCard.details || []" :key="di">
                    {{ d.label }}：<strong>{{ d.value }}</strong>
                  </div>
                  <div class="action-footer" v-if="m.actionCard.resolved !== 'done' && m.actionCard.resolved !== 'cancelled'">
                    <button class="btn-confirm" @click="confirmActionCard(m)">确认执行</button>
                    <button class="btn-cancel" @click="cancelMarkCard(m)">取消</button>
                  </div>
                  <div v-else-if="m.actionCard.resolved === 'cancelled'" class="action-desc">已取消该操作。</div>
                </div>
              </div>

              <!-- v1.2 Step5: 交互式操作路由卡片 (action_list 协议) -->
              <div class="action-list-card" v-if="m.actionList && m.actionList.length">
                <div v-for="(item, li) in m.actionList" :key="li" class="action-list-row">
                  <div class="action-list-main">
                    <div class="action-list-title">{{ item.title }}</div>
                    <el-tag v-if="item.badge" size="small" type="warning" effect="dark">{{ item.badge }}</el-tag>
                  </div>
                  <el-button
                    v-if="item.action && isActionAllowed(item.action.target)"
                    type="primary"
                    size="small"
                    @click="handleCardAction(item.action)"
                  >
                    {{ item.action.label || '去批改' }}
                  </el-button>
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

    <!-- v1.2 Step5: action_list [去批改] 原地唤出批阅抽屉 -->
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
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Plus, ChatDotRound, Delete, MagicStick, DocumentCopy } from '@element-plus/icons-vue';
import { marked } from 'marked';
import request from '../../utils/request';
import { useUserStore } from '../../store/user';
import GradingDrawer from '../exams/components/GradingDrawer.vue';

interface ActionCard {
  actionType: string;
  title: string;
  riskLevel?: string;
  details?: Array<{ label: string; value: string }>;
  payload?: any;
  resolved?: 'pending' | 'done' | 'cancelled';
}

interface ActionListItem {
  title: string;
  badge?: string;
  action?: { type: string; label: string; target: string; params?: any };
}

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
  actionCard?: ActionCard | null;
  actionList?: ActionListItem[] | null;
}

interface CloudSession {
  id: number;
  title: string;
  updated_at: string;
}

const route = useRoute();
const router = useRouter();

const goExams = (): void => {
  router.push('/exams');
};
const userStore = useUserStore();
const input = ref('');
const sending = ref(false);
const messagesWrapRef = ref<HTMLElement | null>(null);

// ---- 企业级云端会话（跨端漫游，彻底告别 localStorage）----
const sessions = ref<CloudSession[]>([]);
const activeSessionId = ref<number | null>(null);
const messages = ref<ChatMessage[]>([]);
const hasMore = ref(true);
const loadingHistory = ref(false);
const loadingMessages = ref(false);
const minMessageId = ref<number | null>(null);

const currentMessages = computed(() => messages.value);

const stripActionBlocks = (t: string): string =>
  (t || '')
    .replace(/```action_card\s*[\s\S]*?```/g, '')
    .replace(/```action_list\s*[\s\S]*?```/g, '')
    .trim();

// 服务端行 -> 本地消息（含卡片状态还原；无落库卡片时回退解析正文）
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
      msg.riskLevel = cardData.risk_level || 'high';
      msg.actionResolved = cardData.status === 'executed';
      if (!msg.content) msg.content = cardData.message || '';
    } else {
      msg.actionCard = { ...(cardData as object), resolved: (cardData.status as ActionCard['resolved']) || 'pending' } as ActionCard;
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
  }
  return msg;
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

const deleteSession = async (id: number): Promise<void> => {
  try {
    await request.delete(`/api/v1/admin/ai/sessions/${id}`);
  } catch (e) {
    return; /* 拦截器已提示 */
  }
  await refreshSessions();
  if (activeSessionId.value === id) {
    if (sessions.value.length > 0) {
      activeSessionId.value = sessions.value[0].id;
      await loadMessages(activeSessionId.value as number);
      scrollToBottom();
    } else {
      await startNewSession();
    }
  }
};

const renameSession = async (s: CloudSession): Promise<void> => {
  try {
    const { ElMessageBox } = await import('element-plus');
    const { value } = await ElMessageBox.prompt('重命名会话', { inputValue: s.title, inputValidator: (v: string) => !!v?.trim() });
    const title = String(value).trim().slice(0, 120);
    await request.put(`/api/v1/admin/ai/sessions/${s.id}`, { title });
    s.title = title;
  } catch (e) {
    /* 取消或失败时静默 */
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesWrapRef.value) {
    messagesWrapRef.value.scrollTop = messagesWrapRef.value.scrollHeight;
  }
};

// 打字机智能吸底锁：仅用户处于底部附近才跟随，用户上滑读史时视口静止
const isNearBottom = (): boolean => {
  const box = messagesWrapRef.value;
  if (!box) return true;
  return box.scrollHeight - box.scrollTop - box.clientHeight < 120;
};

const followScroll = (): void => {
  if (isNearBottom()) scrollToBottom();
};

// 仿微信向上游标分页：触顶拉更早 20 条 + 视口高度数学补偿，零跳屏
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
    /* 历史拉取失败时静默，保持视口不动 */
  } finally {
    loadingHistory.value = false;
  }
};

// 极简轻量 Markdown / HTML 转义渲染
const renderMarkdown = (text: string) => {
  if (!text) return '';
  return marked.parse(text) as string;
};

// ---- 风险三档展示：high 红 / medium 蓝 / low 灰蓝 ----
const riskLabel = (level?: string): string => {
  if (level === 'high') return '高';
  if (level === 'medium') return '中';
  if (level === 'low') return '低';
  return '未知';
};

const riskHeaderClass = (level?: string): string => {
  if (level === 'high') return 'high-risk';
  if (level === 'medium') return 'med-risk';
  return 'low-risk';
};

// 新建题目参数 → 结构化预览（兼容 {key,text} 与 {content,is_correct} 两种选项形状）
const draftPreview = (args: any): {
  title: string; typeLabel: string; difficulty: string; score: number | string;
  options: Array<{ label: string; text: string; correct: boolean }>;
  answerText: string; explanation: string;
} => {
  const a = args || {};
  const typeMap: Record<string, string> = { single: '单选题', multiple: '多选题', judge: '判断题', fill: '填空题', short: '简答题' };
  const rawAns = Array.isArray(a.answer) ? a.answer.map((x: any) => String(x ?? '').trim()) : [];
  const ansSet = new Set(rawAns.map((s: string) => s.toUpperCase()));
  const rawOpts = Array.isArray(a.options) ? a.options : [];
  const options = rawOpts.map((o: any, i: number) => {
    const label = String(o.key ?? String.fromCharCode(65 + i));
    const text = String(o.text ?? o.content ?? '');
    const correct = ansSet.has(label.toUpperCase()) || ansSet.has(text.toUpperCase()) || o.is_correct === true;
    return { label, text, correct };
  });
  return {
    title: String(a.title || '（无题干）'),
    typeLabel: typeMap[String(a.type)] || String(a.type || '题目'),
    difficulty: String(a.difficulty || 'medium'),
    score: a.score ?? 10,
    options,
    answerText: rawAns.join('、') || '—',
    explanation: String(a.explanation || '')
  };
};

// ---- 组卷确认卡：参数补全表单（分类/时间窗/限时/阅卷模式，内置默认值）----
interface ExamDraftForm {
  category_id: number | null;
  timeRange: [string, string] | [];
  is_timed: boolean;
  time_limit: number;
  grading_mode: string;
}

const examCategories = ref<any[]>([]);

const loadExamCategories = async (): Promise<void> => {
  try {
    const res: any = await request.get('/api/v1/admin/categories', { params: { target_type: 'exam' } });
    examCategories.value = Array.isArray(res) ? res : (res.items || []);
  } catch (e) {
    examCategories.value = [];
  }
};

const fmtLocalDateTime = (d: Date): string => {
  const p = (n: number): string => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}:00`;
};

const defaultExamTimeRange = (): [string, string] => {
  const now = new Date();
  return [fmtLocalDateTime(now), fmtLocalDateTime(new Date(now.getTime() + 7 * 86400000))];
};

const examHasShort = (m: ChatMessage): boolean =>
  ((m.arguments?.questions) || []).some((q: any) => q?.type === 'short');

const examFormOf = (m: ChatMessage): ExamDraftForm => {
  const holder = m as any;
  if (!holder.examForm) {
    holder.examForm = {
      category_id: null as number | null,
      timeRange: defaultExamTimeRange(),
      is_timed: true,
      time_limit: 30,
      grading_mode: examHasShort(m) ? 'ai_auto' : 'manual'
    };
  }
  // 分类列表后加载到达时补默认第一项
  if (holder.examForm.category_id == null && examCategories.value.length > 0) {
    holder.examForm.category_id = examCategories.value[0].id;
  }
  return holder.examForm as ExamDraftForm;
};

const examTypeSummary = (args: any): string => {
  const qs = (args?.questions) || [];
  const label: Record<string, string> = { single: '单选', multiple: '多选', judge: '判断', fill: '填空', short: '简答' };
  const counts: Record<string, number> = {};
  for (const q of qs) counts[String(q?.type)] = (counts[String(q?.type)] || 0) + 1;
  const parts = Object.entries(counts).map(([t, n]) => `${n}道${label[t] || t}`);
  return `共 ${qs.length} 题 · ` + parts.join(' + ');
};

const confirmExamDraft = async (m: ChatMessage): Promise<void> => {
  if (m.actionResolved || sending.value) return;
  const f = examFormOf(m);
  const merged = {
    ...(m.arguments || {}),
    category_id: f.category_id ?? undefined,
    start_time: (f.timeRange as string[])?.[0],
    end_time: (f.timeRange as string[])?.[1],
    is_timed: f.is_timed,
    time_limit: f.is_timed ? f.time_limit : 0,
    grading_mode: f.grading_mode
  };
  sending.value = true;
  try {
    const res: any = await request.post('/api/v1/admin/ai/chat/execute_tool', {
      tool_name: 'create_exam_draft',
      arguments: merged,
      tool_call_id: m.toolCallId,
      message_id: m.id ?? null
    });
    // 服务端已将 action_card_data.status 置 executed，本地同步防回退
    m.actionResolved = true;
    ElMessage.success(`试卷草稿创建成功，ID: ${res.exam_id}`);
  } catch (e) {
    /* 拦截器已提示（400 校验信息等），卡片保持待确认可改后重提 */
  } finally {
    sending.value = false;
  }
};

// ---- v1.2 Step5: Action Card / Action List 协议解析 ----

// 前端动作白名单：出题人仅允许唤起站内批阅抽屉，严禁人员/额度/全局看板动作
const ACTION_WHITELIST: Record<string, string[]> = {
  open_grading_drawer: ['super_admin', 'admin', 'creator', 'teacher'],
  TRANSFER_QUOTA: ['super_admin', 'admin'],
};

const isActionAllowed = (target: string): boolean => {
  const roles = ACTION_WHITELIST[target];
  if (!roles) return false;
  return roles.includes(userStore.role);
};

const extractActionBlocks = (text: string): { text: string; card: ActionCard | null; list: ActionListItem[] | null } => {
  let clean = text || '';
  let card: ActionCard | null = null;
  let list: ActionListItem[] | null = null;
  const cardMatch = clean.match(/```action_card\s*([\s\S]*?)```/);
  if (cardMatch) {
    try {
      const parsed = JSON.parse(cardMatch[1]);
      card = { ...parsed, resolved: 'pending' };
    } catch (e) {
      /* 模型输出非标准 JSON 时降级为纯文本展示 */
    }
    clean = clean.replace(cardMatch[0], '').trim();
  }
  const listMatch = clean.match(/```action_list\s*([\s\S]*?)```/);
  if (listMatch) {
    try {
      const parsed = JSON.parse(listMatch[1]);
      if (Array.isArray(parsed)) list = parsed;
    } catch (e) {
      /* 降级为纯文本展示 */
    }
    clean = clean.replace(listMatch[0], '').trim();
  }
  return { text: clean, card, list };
};

// 批阅抽屉联动（action_list [去批改] 原地唤出）
const gradingVisible = ref(false);
const gradingExamId = ref<number | null>(null);
const gradingExamTitle = ref('');

const handleCardAction = (action: { type: string; label: string; target: string; params?: any }): void => {
  if (!isActionAllowed(action.target)) {
    ElMessage.error('当前角色无权执行该操作');
    return;
  }
  if (action.target === 'open_grading_drawer') {
    gradingExamId.value = action.params?.exam_id ?? null;
    gradingExamTitle.value = '';
    gradingVisible.value = true;
  }
};

const handleDrawerGraded = (): void => {
  refreshPendingSnapshot();
};

const confirmActionCard = async (m: ChatMessage): Promise<void> => {
  const card = m.actionCard;
  if (!card || card.resolved !== 'pending') return;
  if (!isActionAllowed(card.actionType)) {
    ElMessage.error('当前角色无权执行该操作');
    return;
  }
  try {
    if (card.actionType === 'TRANSFER_QUOTA') {
      const payload = card.payload || {};
      const target = payload.target_username || payload.target_email || '';
      const amount = Number(payload.amount || 0);
      if (!target || !amount) {
        ElMessage.error('卡片参数缺失（目标用户/数量），无法执行');
        return;
      }
      const members: any = await request.get('/api/v1/admin/members', { params: { keyword: target, size: 20 } });
      const hit = (members.items || []).find((x: any) => x.username === target);
      if (!hit) {
        ElMessage.error(`未找到用户 ${target}`);
        return;
      }
      await request.post(`/api/v1/admin/members/${hit.id}/refill`, { amount });
      ElMessage.success('额度划拨已执行');
      card.resolved = 'done';
    } else {
      ElMessage.error(`未知操作类型 ${card.actionType}，已拒绝执行`);
    }
  } catch (e) {
    /* 拦截器已提示（越权 403 等），卡片保持待确认 */
  }
};

// 待阅快照（出题人仅注入其私有试卷，后端列表接口已按 creator_id 隔离）
const pendingSnapshotLines = ref<string[]>([]);

const refreshPendingSnapshot = async (): Promise<void> => {
  try {
    const res: any = await request.get('/api/v1/admin/exams', { params: { size: 100 } });
    const items = res.items || [];
    const pending = items.filter((e: any) => (e.pending_count || 0) > 0);
    const totalPending = pending.reduce((s: number, e: any) => s + (e.pending_count || 0), 0);
    pendingSnapshotLines.value = [
      `待阅试卷=${pending.length}套, 待批答卷=${totalPending}份`,
      ...pending.slice(0, 10).map((e: any) => `待批:《${e.title}》(exam_id=${e.id}, ${e.pending_count}份待批改)`),
    ];
  } catch (e) {
    pendingSnapshotLines.value = [];
  }
};

const buildPreamble = (userText: string) => {
  const roleText = userStore.role === 'super_admin' ? '超级管理员' : (userStore.role === 'admin' ? '管理员' : '出题人');
  return [
    `[系统隐藏上下文 | 用户不可见]:`,
    `当前用户=${userStore.username}(${roleText}), 剩余AI额度=${userStore.quotaRemaining}次,`,
    ...pendingSnapshotLines.value,
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
  if (!text || sending.value) return;
  // 无选中会话时先云端新建（换端/首登场景）
  if (activeSessionId.value == null) {
    await startNewSession();
    if (activeSessionId.value == null) return;
  }
  const sessionId = activeSessionId.value as number;

  input.value = '';
  messages.value.push({ role: 'user', content: text });
  followScroll();

  sending.value = true;
  // SSE 流式：先放一条占位消息，delta 到达即打字机追加（吸底锁保护阅读）
  const streamingMsg: ChatMessage = { role: 'assistant', content: '', quote: text.length > 30 ? text.substring(0, 30) + '…' : text };
  messages.value.push(streamingMsg);
  followScroll();
  const quote = streamingMsg.quote as string;

  const finishStreamText = (): void => {
    const parsed = extractActionBlocks(streamingMsg.content || '');
    streamingMsg.content = parsed.text || '(无回复)';
    streamingMsg.actionCard = parsed.card;
    streamingMsg.actionList = parsed.list;
  };

  try {
    const history = messages.value
      .filter(m => !m.isThinking && !m.actionRequired && m.role !== 'system' && m !== streamingMsg)
      .slice(-6, -1)
      .map((m) => ({ role: m.role, content: m.content }));

    // 出题人仅注入其私有试卷快照（后端已隔离），附带待阅清单供 action_list grounding
    await refreshPendingSnapshot();
    const token = localStorage.getItem('tiku_tob_token') || '';
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 180000);
    let resp: Response;
    try {
      resp = await fetch('/api/v1/admin/ai/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message: buildPreamble(text), display_text: text, history, session_id: sessionId }),
        signal: controller.signal
      });
    } finally {
      window.clearTimeout(timer);
    }
    if (resp.status === 401) {
      localStorage.removeItem('tiku_tob_token');
      window.location.href = '/admin/login';
      return;
    }
    if (!resp.ok || !resp.body) {
      let detail = '';
      try {
        const errJson = await resp.json();
        detail = errJson?.detail || '';
      } catch (e) { /* 非 JSON 错误体 */ }
      throw { response: { data: { detail } } };
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buf = '';
    let streamFailed = false;
    for (;;) {
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
          streamingMsg.content += ev.text;
          followScroll();
        } else if (ev.type === 'action_required') {
          finishStreamText();
          // 根除空气泡幽灵：占位消息无文本即彻底剔除，不留空泡外壳
          if (streamingMsg.content.trim() === '') {
            messages.value = messages.value.filter(m => m !== streamingMsg);
          }
          messages.value.push({
            role: 'assistant',
            id: ev.assistant_message_id,
            content: ev.message || '',
            quote,
            actionRequired: true,
            toolName: ev.tool_name,
            toolCallId: ev.tool_call_id,
            arguments: ev.arguments,
            riskLevel: ev.risk_level || 'medium',
            actionResolved: false
          });
          userStore.quotaRemaining = ev.quota_remaining ?? userStore.quotaRemaining;
        } else if (ev.type === 'done') {
          userStore.quotaRemaining = ev.quota_remaining ?? userStore.quotaRemaining;
          if (ev.assistant_message_id) streamingMsg.id = ev.assistant_message_id;
          if (ev.user_message_id) {
            const um = [...messages.value].reverse().find(m => m.role === 'user' && m.id == null);
            if (um) um.id = ev.user_message_id;
          }
        } else if (ev.type === 'error') {
          streamFailed = true;
          streamingMsg.content = `AI 服务响应超时或未开启，请稍后再试。${ev.message ? '（' + ev.message + '）' : ''}`;
        }
      }
      if (streamFailed) break;
    }
    if (!streamFailed) finishStreamText();
    // 服务端已重命名首问标题/刷新排序，此处同步侧边栏
    await refreshSessions();
    followScroll();
  } catch (e: any) {
    // 流中断/失败：移除占位消息并降级为纯文本提示
    messages.value = messages.value.filter(m => m !== streamingMsg);

    const detail = e?.response?.data?.detail || e?.message || '';
    if (String(detail).includes('额度')) {
      messages.value.push({ role: 'assistant', content: '今日 AI 额度已用尽，请联系管理员分配或补充。' });
    } else {
      messages.value.push({ role: 'assistant', content: 'AI 服务响应超时或未开启，请稍后再试。' });
    }
  } finally {
    sending.value = false;
  }
};

const executeAction = async (m: ChatMessage) => {
  if (sending.value || m.actionResolved) return;
  sending.value = true;
  try {
    const res: any = await request.post('/api/v1/admin/ai/chat/execute_tool', {
      tool_name: m.toolName,
      arguments: m.arguments,
      tool_call_id: m.toolCallId,
      message_id: m.id ?? null
    });
    // 服务端已将 action_card_data.status 置 executed，本地同步防回退
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

const cancelAction = async (m: ChatMessage) => {
  m.actionResolved = true;

  input.value = `[系统消息]: 我拒绝了操作 ${m.toolName} 的执行。`;
  await send();
};

const cancelMarkCard = (m: ChatMessage): void => {
  if (m.actionCard) m.actionCard.resolved = 'cancelled';
};

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success('已复制到剪贴板');
  } catch (err) {
    ElMessage.error('复制失败');
  }
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
  initCloud();
  loadExamCategories();
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

.action-header.med-risk {
  background: linear-gradient(135deg, #a5f3fc 0%, #ecfeff 100%);
  border-bottom: 1px solid #cffafe;
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

.btn-confirm-medium {
  width: 100%;
  padding: 10px;
  background: #0284c7;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-confirm-medium:hover {
  background: #0369a1;
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
  border: 1px solid #e2e8f0;
}

.quote-bar {
  font-size: 12px;
  color: #64748b;
  border-left: 3px solid #bae6fd;
  padding-left: 8px;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-list-card {
  margin-top: 12px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  max-width: 440px;
}

.action-list-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  border-bottom: 1px solid #f1f5f9;
}

.action-list-row:last-child {
  border-bottom: none;
}

.action-list-main {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.action-list-title {
  font-weight: 600;
  color: #0f172a;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.draft-preview {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #334155;
}

.draft-title {
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
  line-height: 1.6;
}

.draft-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 12px;
  margin-bottom: 8px;
}

.draft-opts {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
}

.draft-opt {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 6px 10px;
  color: #64748b;
}

.draft-opt.correct {
  background-color: #f0fdf4;
  border-color: #86efac;
  color: #166534;
  font-weight: 600;
}

.draft-opt-key {
  font-weight: 800;
}

.draft-opt-mark {
  margin-left: auto;
}

.draft-row {
  line-height: 1.7;
}

.draft-label {
  font-weight: 700;
  color: #475569;
}

.exam-draft-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #334155;
}

.exam-draft-title {
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 6px;
}

.exam-draft-summary {
  color: #0284c7;
  font-weight: 600;
  margin-bottom: 8px;
}

.exam-link {
  color: #0284c7;
  cursor: pointer;
  font-weight: 600;
}

.exam-link:hover {
  text-decoration: underline;
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
