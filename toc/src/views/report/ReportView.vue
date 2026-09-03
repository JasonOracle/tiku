<!--
 * [变更日志]
 * 修改时间：2026-09-03
 * AI模型：Gemini 底层
 * 修改内容：[1. 实现 C 端考试分析报告组件 (含 SVG 环形得分圈、答对错统计与错题文字解析)]
-->
<template>
  <div class="report-container" v-if="report">
    <!-- Header 区域 -->
    <header class="report-header">
      <button class="home-btn" @click="router.push('/')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
        </svg>
      </button>
      <span class="title">答题报告</span>
    </header>

    <!-- 得分与合格指示卡片 -->
    <section class="score-card">
      <div class="score-circle">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" stroke-width="10" />
          <circle 
            cx="60" 
            cy="60" 
            r="50" 
            fill="none" 
            :stroke="report.passed ? '#10b981' : '#ef4444'" 
            stroke-width="10" 
            stroke-dasharray="314"
            :stroke-dashoffset="314 - (314 * report.score) / 100"
            stroke-linecap="round"
          />
        </svg>
        <div class="score-inner">
          <span class="score-num">{{ report.score }}</span>
          <span class="score-label">分</span>
        </div>
      </div>

      <div class="pass-badge" :class="{ passed: report.passed }">
        {{ report.passed ? '考核通过' : '未达到及格线' }}
      </div>
    </section>

    <!-- 统计三元卡片 -->
    <section class="stats-grid">
      <div class="stat-box">
        <span class="stat-val correct">{{ report.correct_count }}</span>
        <span class="stat-lbl">答对题数</span>
      </div>
      <div class="stat-box">
        <span class="stat-val wrong">{{ report.wrong_count }}</span>
        <span class="stat-lbl">答错题数</span>
      </div>
      <div class="stat-box">
        <span class="stat-val time">{{ formattedTime }}</span>
        <span class="stat-lbl">作答用时</span>
      </div>
    </section>

    <!-- 题目解析明细列表 -->
    <main class="analysis-section">
      <h3 class="sec-title">题目答题明细与解析</h3>

      <div v-for="(item, idx) in report.questions_analysis" :key="idx" class="analysis-card">
        <div class="card-head">
          <span class="q-num">Q{{ Number(idx) + 1 }}</span>
          <span class="status-tag" :class="{ correct: item.is_correct }">
            {{ item.is_correct ? '正确' : '错误' }}
          </span>
        </div>

        <h4 class="q-text">{{ item.question.title }}</h4>

        <div class="ans-comparison">
          <div class="ans-box user">
            <span class="lbl">你的答案：</span>
            <span class="val">{{ item.user_answer.length ? item.user_answer.join(', ') : '未作答' }}</span>
          </div>
          <div class="ans-box correct">
            <span class="lbl">正确答案：</span>
            <span class="val">{{ item.correct_answer.join(', ') }}</span>
          </div>
        </div>

        <div v-if="item.question.explanation" class="explanation-box">
          <span class="exp-title">解析说明：</span>
          <p class="exp-text">{{ item.question.explanation }}</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import http from '../../utils/http';

const route = useRoute();
const router = useRouter();

const report = ref<any>(null);

const formattedTime = computed(() => {
  if (!report.value) return '0秒';
  const sec = report.value.time_spent || 0;
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return m > 0 ? `${m}分${s}秒` : `${s}秒`;
});

onMounted(async () => {
  const recordId = route.query.record_id;
  if (!recordId) {
    router.push('/');
    return;
  }
  try {
    const res: any = await http.get(`/api/v1/records/${recordId}/report`);
    report.value = res;
  } catch (e) {
    router.push('/');
  }
});
</script>

<style scoped>
.report-container {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: #f8fafc;
  padding-bottom: 40px;
}

.report-header {
  padding: 16px 20px;
  background: white;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.home-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #0284c7;
}

.title {
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
}

.score-card {
  background: white;
  margin: 16px 20px;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
}

.score-circle {
  position: relative;
  width: 120px;
  height: 120px;
}

.score-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: baseline;
}

.score-num {
  font-size: 36px;
  font-weight: 800;
  color: #0f172a;
}

.score-label {
  font-size: 14px;
  color: #64748b;
  margin-left: 2px;
}

.pass-badge {
  margin-top: 16px;
  padding: 6px 16px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
  background: #fee2e2;
  color: #ef4444;
}

.pass-badge.passed {
  background: #d1fae5;
  color: #10b981;
}

.stats-grid {
  display: flex;
  gap: 12px;
  padding: 0 20px;
}

.stat-box {
  flex: 1;
  background: white;
  border-radius: 16px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-val {
  font-size: 20px;
  font-weight: 800;
}

.stat-val.correct { color: #10b981; }
.stat-val.wrong { color: #ef4444; }
.stat-val.time { color: #0284c7; }

.stat-lbl {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

.analysis-section {
  padding: 20px;
}

.sec-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 14px;
}

.analysis-card {
  background: white;
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 12px;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.q-num {
  font-size: 13px;
  font-weight: 700;
  color: #0284c7;
}

.status-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
  background: #fee2e2;
  color: #ef4444;
}

.status-tag.correct {
  background: #d1fae5;
  color: #10b981;
}

.q-text {
  margin: 8px 0 14px;
  font-size: 15px;
  color: #1e293b;
}

.ans-comparison {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.ans-box {
  flex: 1;
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 12px;
}

.ans-box.user { background: #f1f5f9; color: #475569; }
.ans-box.correct { background: #e0f2fe; color: #0284c7; }

.explanation-box {
  background: #f8fafc;
  border-left: 3px solid #0284c7;
  padding: 10px 12px;
  border-radius: 0 8px 8px 0;
  font-size: 12px;
}

.exp-title { font-weight: 700; color: #0f172a; }
.exp-text { margin: 4px 0 0; color: #475569; }
</style>
