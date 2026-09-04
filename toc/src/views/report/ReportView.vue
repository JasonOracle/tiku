<!--
 * [变更日志]
 * 修改时间：2026-09-04
 * AI模型：Gemini 系列
 * 修改内容：[1. 替换自定义 header 为统一 NavBar 组件，修复返回跳转至首页的 Bug，改为返回上一页]
-->
<template>
  <div class="report-container" v-if="report">
    <!-- Header 区域：使用沉浸式导航栏（向下滚动时动态变白底） -->
    <NavBar title="答题报告" immersive />

    <!-- 得分与合格指示卡片 -->
    <section class="score-card">
      <div class="score-circle">
        <svg width="170" height="170" viewBox="0 0 170 170">
          <defs>
            <linearGradient id="ring-grad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="#34d399" />
              <stop offset="1" stop-color="#10b981" />
            </linearGradient>
          </defs>
          <circle cx="85" cy="85" r="68" fill="none" stroke="#e8f5ef" stroke-width="14" />
          <circle
            cx="85"
            cy="85"
            r="68"
            fill="none"
            :stroke="report.passed ? 'url(#ring-grad)' : '#ef4444'"
            stroke-width="14"
            stroke-dasharray="427"
            :stroke-dashoffset="ringOffset"
            stroke-linecap="round"
            transform="rotate(-90 85 85)"
          />
          <circle cx="85" cy="17" r="7" :fill="report.passed ? '#10b981' : '#ef4444'" />
        </svg>
        <div class="score-inner">
          <div><span class="score-num">{{ report.score }}</span><span class="score-label">分</span></div>
          <span class="score-total">总分 {{ ringTotal }}</span>
        </div>
      </div>

      <div class="pass-badge" :class="{ passed: report.passed }">
        <svg v-if="report.passed" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        {{ report.passed ? '考核通过' : '未达到及格线' }}
      </div>
    </section>

    <!-- 统计三元卡片 -->
    <section class="stats-grid">
      <div class="stat-box">
        <span class="stat-icon ok">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
        </span>
        <span class="stat-val correct">{{ report.correct_count }}</span>
        <span class="stat-lbl">答对题数</span>
      </div>
      <div class="stat-box">
        <span class="stat-icon no">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </span>
        <span class="stat-val wrong">{{ report.wrong_count }}</span>
        <span class="stat-lbl">答错题数</span>
      </div>
      <div class="stat-box">
        <span class="stat-icon time-ic">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </span>
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
          <div class="ans-box user" :class="{ wrong: !item.is_correct }">
            <span class="lbl">你的答案</span>
            <span class="val">{{ item.user_answer.length ? item.user_answer.join(', ') : '未作答' }}</span>
          </div>
          <div class="ans-box correct">
            <span class="lbl">正确答案</span>
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
import NavBar from '../../components/NavBar.vue';

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

const ringTotal = computed(() => report.value?.total_score || 100);
const ringOffset = computed(() => {
  if (!report.value) return 427;
  const ratio = Math.min(Math.max(report.value.score / ringTotal.value, 0), 1);
  return 427 - 427 * ratio;
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
  background: linear-gradient(180deg, #eef4ff 0%, #f8fafc 40%);
  padding-bottom: 40px;
  font-family: 'Plus Jakarta Sans', 'Outfit', system-ui, sans-serif;
}

.score-card {
  background: #ffffff;
  margin: 16px;
  border-radius: 24px;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 10px 30px -4px rgba(15, 23, 42, 0.05);
}

.score-circle {
  position: relative;
  width: 170px;
  height: 170px;
}

.score-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-num {
  font-size: 52px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1;
}

.score-label {
  font-size: 15px;
  color: #64748b;
  margin-left: 4px;
  font-weight: 600;
}

.score-total {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 6px;
  font-weight: 600;
}

.pass-badge {
  margin-top: 18px;
  padding: 7px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 800;
  background: #ffe4e6;
  color: #e11d48;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 12px rgba(225, 29, 72, 0.12);
}

.pass-badge.passed {
  background: #dcfce7;
  color: #15803d;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.18);
}

.stats-grid {
  display: flex;
  gap: 12px;
  padding: 0 16px;
}

.stat-box {
  flex: 1;
  background: #ffffff;
  border-radius: 20px;
  padding: 16px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.04);
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.9);
}

.stat-icon.ok { background: linear-gradient(135deg, #dcfce7, #bbf7d0); color: #166534; }
.stat-icon.no { background: linear-gradient(135deg, #ffe4e6, #fecdd3); color: #be123c; }
.stat-icon.time-ic { background: linear-gradient(135deg, #e0f2fe, #bae6fd); color: #0369a1; }

.stat-val {
  font-size: 18px;
  font-weight: 800;
}

.stat-val.correct { color: #15803d; }
.stat-val.wrong { color: #e11d48; }
.stat-val.time { color: #0284c7; }

.stat-lbl {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
  font-weight: 600;
}

.analysis-section {
  padding: 20px 16px;
}

.sec-title {
  font-size: 16px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 14px;
  padding-left: 10px;
  border-left: 4px solid #6366f1;
}

.analysis-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 18px 20px;
  margin-bottom: 12px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.04);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.q-num {
  font-size: 12px;
  font-weight: 800;
  color: #0284c7;
  background: #f0f9ff;
  padding: 2px 8px;
  border-radius: 6px;
}

.status-tag {
  font-size: 11px;
  font-weight: 800;
  padding: 2px 9px;
  border-radius: 6px;
  background: #ffe4e6;
  color: #e11d48;
}

.status-tag.correct {
  background: #dcfce7;
  color: #15803d;
}

.q-text {
  margin: 10px 0 14px;
  font-size: 15px;
  color: #0f172a;
  font-weight: 800;
  line-height: 1.45;
}

.ans-comparison {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.ans-box {
  flex: 1;
  padding: 10px 12px;
  border-radius: 12px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ans-box .lbl { color: #64748b; flex-shrink: 0; font-size: 12px; }
.ans-box .val { font-weight: 800; font-size: 14px; margin-left: auto; }

.ans-box.user { background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; }
.ans-box.user .val { color: #334155; }
.ans-box.user.wrong { background: #fff1f2; border-color: #fecdd3; }
.ans-box.user.wrong .val { color: #e11d48; }
.ans-box.correct { background: #f0fdf4; border: 1px solid #dcfce7; }
.ans-box.correct .val { color: #15803d; }

.explanation-box {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  padding: 12px 14px;
  border-radius: 14px;
  font-size: 13px;
  margin-top: 12px;
}

.exp-title { font-weight: 800; color: #0284c7; }
.exp-text { margin: 4px 0 0; color: #475569; line-height: 1.55; }
</style>
