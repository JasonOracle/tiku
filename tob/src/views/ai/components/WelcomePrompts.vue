<!--
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：Agnes-2.5-Flash
 * 修改内容：[新建欢迎 Prompt 胶囊组件 - 对标 Ant Design X 迎宾卡]
-->
<template>
  <div class="welcome-container">
    <div class="welcome-brand">
      <div class="welcome-icon">
        <el-icon :size="32"><MagicStick /></el-icon>
      </div>
      <h2>企业培训 AI 智能助管</h2>
      <p>我可以帮您基于知识库一键组卷、批量出题，或进行试卷全量批阅。</p>
    </div>
    <div class="prompts-grid">
      <div
        v-for="(p, index) in promptList"
        :key="index"
        class="prompt-card"
        @click="$emit('select-prompt', p.prompt)"
      >
        <div class="prompt-header">
          <el-icon class="prompt-icon"><DocumentAdd /></el-icon>
          <span class="prompt-title">{{ p.title }}</span>
        </div>
        <p class="prompt-desc">{{ p.desc }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MagicStick, DocumentAdd } from '@element-plus/icons-vue';

defineEmits<{
  (e: 'select-prompt', prompt: string): void;
}>();

const promptList = [
  {
    title: '智能知识库组卷',
    desc: '根据指定知识库，自动生成一套包含 10 道单选题的标准测试卷',
    prompt: '请根据我们的企业规章知识库，帮我生成一套包含 10 道单选的测试卷。'
  },
  {
    title: '批量试题草稿生成',
    desc: '围绕特定业务技能，批量设计 5 道带解析的案例实操多选题',
    prompt: '请围绕新员工入职培训，帮我批量出 5 道考查服务意识的多选试题。'
  },
  {
    title: '试卷自动批阅快照',
    desc: '查看当前所有待批阅的主观题试卷并汇总批阅进度',
    prompt: '帮我检查目前系统中有哪些待批阅的试卷，并给出当前批阅快照。'
  }
];
</script>

<style scoped>
.welcome-container {
  max-width: 680px;
  margin: 40px auto 0;
  text-align: center;
}

.welcome-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  color: #3b82f6;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.welcome-brand h2 {
  font-size: 22px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 8px;
}

.welcome-brand p {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 28px;
}

.prompts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  text-align: left;
}

.prompt-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.prompt-card:hover {
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.08);
}

.prompt-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 6px;
}

.prompt-icon {
  color: #3b82f6;
}

.prompt-desc {
  font-size: 12px;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}
</style>
