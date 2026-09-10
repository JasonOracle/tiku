<!--
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗：对接新溯源对话接口并展示引用，旧额度/ sessions 体系已删除]
-->
<template>
  <el-drawer v-model="visible" title="✨ AI 助手" size="420px" :append-to-body="true">
    <div class="copilot-wrap">
      <div class="quota-line">
        <span>📚 基于企业公共知识库回答，自动附带参考溯源</span>
        <span v-if="!aiAvailable" class="warn">AI 未配置</span>
      </div>

      <div class="chat-area" ref="chatAreaRef">
        <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role">
          <div class="bubble">{{ m.content }}</div>
        </div>
        <div v-if="messages.length === 0" class="empty-tip">
          <p>你好，{{ userStore.username }}！我是你的 AI 助手。</p>
          <p>试试问我：「报销标准是什么？」、「帮我创建一组安全培训条目？」</p>
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
  ({ '/resources': '题目管理', '/tasks': '试卷管理', '/verification': '阅卷管理', '/categories': '分类配置',
    '/members': '成员管理', '/banners': 'Banner设置', '/messages': '消息中心', '/kb': 'AI知识库',
    '/audit': '审计日志', '/dashboard': '数据看板' } as any)[path] || '工作台';

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
      message: text,
      history
    }, { timeout: 120000 }); // 大模型回复较慢, 覆盖全局 10s 超时
    const reply = res.content || res.reply || '(空回复)';
    const sources = res.ai_rag_sources || [];
    messages.value.push({ role: 'assistant', content: reply });
    if (sources.length) {
      messages.value.push({
        role: 'assistant',
        content: '📚 参考溯源：' + sources.map((s: any) => s.document_name || s.file_name || '').filter(Boolean).join('、')
      });
    }
  } catch (e: any) {
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
