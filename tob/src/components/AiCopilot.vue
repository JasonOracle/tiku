<!--
 * [变更日志]
 * 修改时间：2026-09-08
 * AI模型：Gemini 系列
 * 修改内容：[前端隐藏上下文 buildPreamble 注入用户个人资料画像(姓名/职务/背景)，使抽屉式AI助手同步具备个性化认知]
 * 修改时间：2026-09-06 21:00:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.2 新增 AI Copilot 助手抽屉: 前端状态快照注入(Frontend State Preamble)——把当前老师身份/
 *          停留页面/待批阅数/剩余额度硬拼进 Prompt 前导, 后端纯透传大模型, 零 RAG 成本]
-->
<template>
  <el-drawer v-model="visible" title="✨ AI 助手" size="420px" :append-to-body="true">
    <div class="copilot-wrap">
      <div class="quota-line">
        <span>🔋 今日剩余 AI 额度：<strong>{{ userStore.quotaRemaining }}</strong> 次</span>
        <span v-if="!aiAvailable" class="warn">AI 未配置</span>
      </div>

      <div class="chat-area" ref="chatAreaRef">
        <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role">
          <div class="bubble">{{ m.content }}</div>
        </div>
        <div v-if="messages.length === 0" class="empty-tip">
          <p>你好，{{ userStore.username }}！我是你的 AI 数字员工。</p>
          <p>试试问我：「我今天该做什么？」、「怎么组一份期末卷？」</p>
        </div>
      </div>

      <div class="input-area">
        <el-input v-model="input" type="textarea" :rows="2" placeholder="输入问题... (Enter 发送, Shift+Enter 换行)"
                  @keydown.enter.exact.prevent="send" :disabled="sending" />
        <el-button type="primary" :loading="sending" @click="send" :disabled="!input.trim()">发送</el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '../utils/request';
import { useUserStore } from '../store/user';

const visible = ref(false);
const visibleRef = visible;
defineExpose({ visibleRef, open: () => (visible.value = true) });

const route = useRoute();
const userStore = useUserStore();
const messages = ref<Array<{ role: 'user' | 'assistant'; content: string }>>([]);
const input = ref('');
const sending = ref(false);
const aiAvailable = ref(true);
const chatAreaRef = ref<HTMLElement | null>(null);

const pageName = (path: string) =>
  ({ '/questions': '题海管理', '/exams': '试卷与组卷', '/grading': '阅卷大厅', '/categories': '分类配置',
    '/users': '用户与明细', '/banners': 'Banner设置', '/messages': '消息中心', '/members': '成员与额度',
    '/audit': '审计日志' } as any)[path] || '工作台';

// 前端状态快照注入: 拼装隐藏上下文前导, 让 AI 零成本获得"上帝视角"
const buildPreamble = (userText: string) => {
  const roleText = userStore.role === 'super_admin' ? '超级管理员' : '普通教师(老师)';
  const profileParts: string[] = [];
  if (userStore.name) profileParts.push(`真实姓名=${userStore.name}`);
  if (userStore.position) profileParts.push(`职务=${userStore.position}`);
  if (userStore.bio) profileParts.push(`背景与学科介绍=${userStore.bio}`);

  return [
    `[系统隐藏上下文 | 用户不可见]:`,
    `当前用户=${userStore.username}(${roleText})${profileParts.length ? '，个人画像=[' + profileParts.join(', ') + ']' : ''}, 剩余AI额度=${userStore.quotaRemaining}次,`,
    `当前停留页面=${pageName(route.path)}。`,
    `请基于以上身份、用户背景与页面上下文回答老师的问题; 称呼亲切自然，保持简洁、可执行。`,
    ``
  ].join('\n') + `\n老师提问: ${userText}`;
};

const scrollBottom = async () => {
  await nextTick();
  if (chatAreaRef.value) chatAreaRef.value.scrollTop = chatAreaRef.value.scrollHeight;
};

const send = async () => {
  const text = input.value.trim();
  if (!text || sending.value) return;
  input.value = '';
  messages.value.push({ role: 'user', content: text });
  scrollBottom();
  sending.value = true;
  try {
    const history = messages.value.slice(-6, -1).map((m) => ({ role: m.role, content: m.content }));
    const res: any = await request.post('/api/v1/admin/ai/chat', {
      message: buildPreamble(text),
      history
    }, { timeout: 120000 }); // 大模型回复较慢, 覆盖全局 10s 超时
    userStore.quotaRemaining = res.quota_remaining ?? userStore.quotaRemaining;
    messages.value.push({ role: 'assistant', content: res.reply || '(空回复)' });
  } catch (e: any) {
    const detail = e?.response?.data?.detail || '';
    if (String(detail).includes('额度')) {
      messages.value.push({ role: 'assistant', content: '今日 AI 额度已用尽，请联系超级管理员在「成员与AI额度」中分配或补充。' });
    } else {
      aiAvailable.value = false;
      messages.value.push({ role: 'assistant', content: 'AI 服务暂时不可用，请稍后再试。' });
    }
  } finally {
    sending.value = false;
    scrollBottom();
  }
};
</script>

<style scoped>
.copilot-wrap {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.quota-line {
  font-size: 13px;
  color: #475569;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 10px;
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
}

.warn {
  color: #ef4444;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 12px 4px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.msg {
  display: flex;
}

.msg.user {
  justify-content: flex-end;
}

.msg.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 85%;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.msg.user .bubble {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: white;
  border-bottom-right-radius: 4px;
}

.msg.assistant .bubble {
  background: #f1f5f9;
  color: #0f172a;
  border-bottom-left-radius: 4px;
}

.empty-tip {
  color: #94a3b8;
  font-size: 13px;
  line-height: 2;
  text-align: center;
  margin-top: 40%;
}

.input-area {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
}
</style>
