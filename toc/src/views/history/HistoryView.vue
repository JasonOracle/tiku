<!--
 * [变更日志]
 * 修改时间：2026-09-04 00:08:00
 * AI模型：Gemini 底层
 * 修改内容：[1. 实现 C 端历史答题记录列表: 点击卡片跳转至 /report 错题分析报告]
-->
<template>
  <div class="history-container">
    <div class="header">
      <button class="back-btn" @click="router.back()">‹ 返回</button>
      <h2>历史答题记录</h2>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <div v-else-if="records.length === 0" class="empty-state">
      <p>暂无历史答题记录</p>
      <button class="go-btn" @click="router.push('/')">去刷题测评</button>
    </div>

    <div v-else class="record-list">
      <div
        v-for="r in records"
        :key="r.record_id"
        class="record-card glass-panel"
        @click="goToReport(r.record_id)"
      >
        <div class="card-top">
          <h3 class="exam-title">{{ r.exam_title || '在线知识测评' }}</h3>
          <span :class="['pass-tag', r.passed ? 'pass' : 'fail']">
            {{ r.passed ? '及格' : '未及格' }}
          </span>
        </div>

        <div class="card-body">
          <div class="score-info">
            <span class="score-val">{{ r.score }}</span>
            <span class="score-label">最终得分</span>
          </div>
          <div class="meta-info">
            <div class="meta-item">⏱ 耗时：{{ Math.floor((r.time_spent || 0) / 60) }}分{{ (r.time_spent || 0) % 60 }}秒</div>
            <div class="meta-item">📅 提交：{{ new Date(r.submit_time || r.start_time).toLocaleString() }}</div>
          </div>
        </div>

        <div class="card-footer">
          <span>查看错题解析与答题明细</span>
          <span class="arrow">›</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import http from '../../utils/http';

const router = useRouter();
const loading = ref(false);
const records = ref<any[]>([]);

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
  min-height: 100vh;
  background: linear-gradient(180deg, #e0f2fe 0%, #f8fafc 100%);
  padding: 16px;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.back-btn {
  background: transparent;
  border: none;
  font-size: 16px;
  color: #0284c7;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  margin-right: 12px;
}

.header h2 {
  margin: 0;
  font-size: 18px;
  color: #0f172a;
  font-weight: 700;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(2, 132, 199, 0.06);
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-card {
  padding: 16px;
  cursor: pointer;

}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.exam-title {
  margin: 0;
  font-size: 16px;
  color: #0f172a;
  font-weight: 700;
}

.pass-tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 10px;
  font-weight: 700;
}

.pass-tag.pass {
  background: #dcfce7;
  color: #15803d;
}

.pass-tag.fail {
  background: #fee2e2;
  color: #b91c1c;
}

.card-body {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 12px;
  border-bottom: 1px dashed rgba(226, 232, 240, 0.9);
}

.score-val {
  font-size: 28px;
  font-weight: 800;
  color: #0284c7;
  display: block;
  line-height: 1;
}

.score-label {
  font-size: 11px;
  color: #64748b;
}

.meta-info {
  font-size: 12px;
  color: #64748b;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  font-size: 12px;
  color: #0284c7;
  font-weight: 600;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 60px 0;
  color: #64748b;
}

.go-btn {
  margin-top: 12px;
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  font-weight: 600;
}
</style>
