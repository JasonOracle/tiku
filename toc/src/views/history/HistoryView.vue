<!--
 * [变更日志]
 * 修改时间：2026-09-04
 * AI模型：Gemini 系列
 * 修改内容：[1. 现代扁平拟物风格重构历史记录列表：消除 NavBar 与第一项卡片黏连问题，引入分数大号高亮、细节 Pill 芯片与蓝紫渐变跳转箭头; 2. 优化时间与耗时格式化逻辑]
 -->
<template>
  <div class="history-container">
    <NavBar title="历史答题记录" />

    <main class="history-body">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="records.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>暂无历史答题记录</p>
        <button class="go-btn" @click="router.push('/')">去刷题测评</button>
      </div>

      <div v-else class="record-list">
        <div
          v-for="r in records"
          :key="r.record_id"
          class="record-card"
          @click="goToReport(r.record_id)"
        >
          <div class="card-top">
            <h3 class="exam-title">{{ r.exam_title || '在线知识测评' }}</h3>
            <span :class="['pass-tag', r.passed ? 'pass' : 'fail']">
              {{ r.passed ? '考核通过' : '未达及格线' }}
            </span>
          </div>

          <div class="card-body">
            <div class="score-box" :class="{ passed: r.passed }">
              <span class="score-val">{{ r.score }}</span>
              <span class="score-label">最终得分</span>
            </div>

            <div class="meta-info">
              <div class="meta-row">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                <span>耗时：{{ formatTimeSpent(r.time_spent) }}</span>
              </div>
              <div class="meta-row">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                <span>提交：{{ formatDate(r.submit_time || r.start_time) }}</span>
              </div>
            </div>
          </div>

          <div class="card-divider"></div>

          <div class="card-footer">
            <span class="cta-text">查看错题解析与答题明细</span>
            <span class="arrow-btn">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import http from '../../utils/http';
import NavBar from '../../components/NavBar.vue';

const router = useRouter();
const loading = ref(false);
const records = ref<any[]>([]);

const formatTimeSpent = (sec?: number) => {
  const s = sec || 0;
  const m = Math.floor(s / 60);
  const r = s % 60;
  return m > 0 ? `${m}分${r}秒` : `${r}秒`;
};

const formatDate = (timeStr?: string) => {
  if (!timeStr) return '未知时间';
  const d = new Date(timeStr.replace(' ', 'T'));
  if (isNaN(d.getTime())) return timeStr;
  const month = d.getMonth() + 1;
  const day = d.getDate();
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  return `${d.getFullYear()}/${month}/${day} ${hours}:${minutes}`;
};

const loadHistory = async () => {
  loading.value = true;
  try {
    const res: any = await http.get('/api/v1/records/history');
    records.value = res.data?.items || res.items || [];
  } finally {
    loading.value = false;
  }
};

const goToReport = (recordId: number) => {
  router.push(`/report?record_id=${recordId}`);
};

onMounted(() => {
  loadHistory();
});
</script>

<style scoped>
.history-container {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(180deg, #eef4ff 0%, #f8fafc 40%);
  padding-bottom: 30px;
  font-family: 'Plus Jakarta Sans', 'Outfit', system-ui, sans-serif;
}

.history-body {
  padding: 16px;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.record-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 18px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.04), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.record-card:active {
  transform: scale(0.985);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.exam-title {
  margin: 0;
  font-size: 16px;
  color: #0f172a;
  font-weight: 800;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 8px;
}

.pass-tag {
  font-size: 11px;
  padding: 3px 9px;
  border-radius: 6px;
  font-weight: 800;
  flex-shrink: 0;
}

.pass-tag.pass {
  background: #dcfce7;
  color: #15803d;
}

.pass-tag.fail {
  background: #ffe4e6;
  color: #e11d48;
}

.card-body {
  display: flex;
  align-items: center;
  gap: 20px;
}

.score-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #fff1f2;
  padding: 8px 14px;
  border-radius: 14px;
  min-width: 64px;
}

.score-box.passed {
  background: #f0fdf4;
}

.score-val {
  font-size: 28px;
  font-weight: 800;
  color: #e11d48;
  line-height: 1;
}

.score-box.passed .score-val {
  color: #15803d;
}

.score-label {
  font-size: 10px;
  color: #94a3b8;
  font-weight: 700;
  margin-top: 4px;
}

.meta-info {
  font-size: 12px;
  color: #64748b;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #64748b;
}

.meta-row svg {
  color: #0284c7;
}

.card-divider {
  border-bottom: 1px dashed #e2e8f0;
  margin: 14px 0 12px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cta-text {
  font-size: 13px;
  color: #6366f1;
  font-weight: 700;
}

.arrow-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0284c7, #6366f1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);
}

.loading-state, .empty-state {
  text-align: center;
  padding: 80px 0;
  color: #64748b;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.go-btn {
  margin-top: 12px;
  background: linear-gradient(135deg, #0284c7, #6366f1);
  color: white;
  border: none;
  padding: 9px 22px;
  border-radius: 18px;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3);
  cursor: pointer;
}
</style>
