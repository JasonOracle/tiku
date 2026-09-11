<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[1. 增加 passLabel 计算属性区分 submitted（自动出分）与 verified（人工核验）的成绩徽章文案；2. 修复成绩为 null 时 pass-badge 显示"已核验"的误导问题]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗重写：对接成员成绩接口（核验中/得分/评语/本人作答），旧报告与解析锁体系已删除]
-->
<template>
  <div class="report-container" v-if="report">
    <NavBar title="任务结果" immersive />

    <section class="score-card">
      <template v-if="report.pending">
        <div class="grading-hero">
          <div class="grading-icon">
            <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 20h9"></path>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
          </div>
          <div class="grading-title">核验中</div>
          <div class="grading-desc">
            任务已提交，正在由管理员/AI 核验，核验完成后可查看得分与评语。
          </div>
        </div>
      </template>
      <template v-else>
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
            <div><span class="score-num">{{ report.score ?? '—' }}</span><span class="score-label">分</span></div>
            <span class="score-total">共 {{ report.items.length }} 项作答</span>
          </div>
        </div>

        <div class="pass-badge" :class="{ passed: report.passed }">
          {{ passLabel }}
        </div>
        <div v-if="report.comments || report.ai_comments" class="comment-box">
          <span class="comment-title">核验评语：</span>
          <p class="comment-text">{{ report.comments || report.ai_comments }}</p>
        </div>
      </template>
    </section>

    <section class="stats-grid">
      <div class="stat-box">
        <span class="stat-val time">{{ formattedTime }}</span>
        <span class="stat-lbl">作答用时</span>
      </div>
      <div class="stat-box">
        <span class="stat-val correct">{{ report.items.length }}</span>
        <span class="stat-lbl">作答条目</span>
      </div>
      <div class="stat-box">
        <span class="stat-val">{{ statusLabel }}</span>
        <span class="stat-lbl">当前状态</span>
      </div>
    </section>

    <main class="analysis-section">
      <h3 class="sec-title">我的作答明细</h3>
      <div v-for="(item, idx) in report.items" :key="idx" class="analysis-card">
        <div class="card-head">
          <span class="q-num">Q{{ Number(idx) + 1 }}</span>
        </div>
        <h4 class="q-text">{{ item.content }}</h4>
        <div class="ans-comparison">
          <div class="ans-box user">
            <span class="lbl">我的答案</span>
            <span class="val">{{ fmtAnswer(item.user_answer) }}</span>
          </div>
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

const ringTotal = computed(() => {
  const items = report.value?.items || [];
  const total = items.reduce((a: number, i: any) => a + (i.eq_score || 0), 0);
  return total || 100;
});

const ringOffset = computed(() => {
  if (!report.value || report.value.score == null) return 427;
  const ratio = Math.min(Math.max(report.value.score / ringTotal.value, 0), 1);
  return 427 - 427 * ratio;
});

const statusLabel = computed(() => {
  const s = report.value?.status;
  if (s === 'verified') return '已核验';
  if (s === 'pending_verification') return '核验中';
  if (s === 'submitted') return '已提交';
  return '待办';
});

// 成绩徽章文案：区分已提交（自动出分）与已核验（人工/AI确认）
const passLabel = computed(() => {
  const s = report.value?.status;
  const passed = report.value?.passed;
  if (s === 'verified') return passed ? '已核验通过' : '已核验';
  if (s === 'submitted') return passed ? '恭喜通过' : '未达及格线';
  return '待评定';
});

const fmtAnswer = (a: any): string => {
  if (Array.isArray(a)) return a.length ? a.join(', ') : '未作答';
  if (a && typeof a === 'object') return JSON.stringify(a);
  return String(a ?? '') || '未作答';
};

onMounted(async () => {
  const recordId = route.query.record_id;
  if (!recordId) {
    router.push('/');
    return;
  }
  try {
    const res: any = await http.get(`/api/v1/member/task-records/${recordId}`);
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

.grading-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0 4px;
}

.grading-icon {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #b45309;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  box-shadow: 0 8px 20px rgba(180, 83, 9, 0.15);
}

.grading-title {
  font-size: 24px;
  font-weight: 800;
  color: #92400e;
}

.grading-desc {
  margin-top: 8px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.7;
  text-align: center;
  padding: 0 16px;
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

.stat-val {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
}

.stat-val.correct {
  color: #16a34a;
}

.stat-val.time {
  color: #0284c7;
}

.stat-lbl {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.analysis-section {
  padding: 16px;
}

.sec-title {
  font-size: 15px;
  font-weight: 800;
  color: #0f172a;
  margin: 4px 4px 12px;
}

.analysis-card {
  background: #fff;
  border-radius: 16px;
  padding: 14px 16px;
  margin-bottom: 12px;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.card-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.q-num {
  font-size: 12px;
  font-weight: 800;
  color: #6366f1;
}

.q-text {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 10px;
  line-height: 1.6;
}

.ans-comparison {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ans-box {
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 13px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ans-box.user {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
}

.ans-box .lbl {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 700;
}

.ans-box .val {
  color: #0f172a;
  line-height: 1.6;
  white-space: pre-wrap;
}

.comment-box {
  margin-top: 14px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 10px;
  padding: 10px 14px;
  width: 100%;
  box-sizing: border-box;
}

.comment-title {
  font-size: 12px;
  font-weight: 800;
  color: #b45309;
}

.comment-text {
  font-size: 13px;
  color: #78350f;
  line-height: 1.7;
  margin: 4px 0 0;
}
</style>
