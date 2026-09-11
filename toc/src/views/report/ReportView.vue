<!--
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Agnes-3.0-flash (ZCode)
 * 修改内容：[「我的作答明细」每题补题型标签徽章 + 选项/填空对照渲染：客观题选项列出并按用户所选高亮蓝、与标准答案一致绿、不一致红；判断题无选项时自动补「正确/错误」；填空题保留题干下划线占位并逐空对照我的填写与标准答案；简答题不显示选项区；新增 time_spent 格式化兜底，修复用时恒为 0秒 问题（接口未返回时隐藏该统计块而非显示 0秒）]
 * 修改时间：2026-09-11
 * AI模型：Codex 3
 * 修改内容：[每题作答明细恢复「标准答案 + 答案解析」对照展示：新增 correct-answer 与 explanation 区块，绿/琥珀双色卡片；无解析数据时显示"暂无解析"占位；核验中/已提交/已核验三态均可查看]
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
      <div v-if="hasTime" class="stat-box">
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
          <span v-if="item.type" class="type-badge">{{ getTypeLabel(item.type) }}</span>
        </div>
        <h4 class="q-text" v-if="!isFill(item.type)">{{ item.content }}</h4>
        <h4 v-else-if="isFill(item.type)" class="q-text" v-html="renderContent(item.content)"></h4>
        <div v-if="isObjective(item.type)" class="opt-compare">
          <div
            v-for="opt in normOptions(item)"
            :key="opt.key"
            class="opt-item"
            :class="{
              'opt-mine': isUserPicked(item, opt.key),
              'opt-correct': isCorrectPick(item, opt.key),
              'opt-wrong': isWrongPick(item, opt.key)
            }"
          >
            <span class="opt-prefix">{{ opt.key }}</span>
            <span class="opt-content">{{ opt.text }}</span>
            <span v-if="isUserPicked(item, opt.key)" class="opt-tag mine">我选了</span>
            <span v-if="isCorrectPick(item, opt.key)" class="opt-tag correct">正确答案</span>
            <span v-if="isWrongPick(item, opt.key)" class="opt-tag wrong">错误</span>
          </div>
        </div>
        <div v-else-if="isFill(item.type)" class="fill-compare">
          <div
            v-for="(pair, k) in fillPairs(item)"
            :key="k"
            class="fill-pair"
          >
            <span class="fill-blank">第 {{ Number(k) + 1 }} 空</span>
            <span class="fill-mine">我填：{{ pair.mine || '未作答' }}</span>
            <span class="fill-answer">标准：{{ pair.answer || '暂无标准答案' }}</span>
          </div>
        </div>
        <div class="ans-comparison">
          <div class="ans-box user">
            <span class="lbl">我的答案</span>
            <span class="val">{{ fmtAnswer(item.user_answer) }}</span>
          </div>
          <div v-if="item.correct_answer != null || item.explanation" class="ans-stack">
            <div v-if="item.correct_answer != null" class="ans-box correct">
              <span class="lbl">标准答案</span>
              <span class="val">{{ fmtAnswer(item.correct_answer) }}</span>
            </div>
            <div v-if="item.explanation" class="ans-box explanation">
              <span class="lbl">答案解析</span>
              <span class="val">{{ item.explanation }}</span>
            </div>
          </div>
          <div v-else class="no-explanation">暂无解析</div>
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

// 题型徽章文案（兼容 single_choice/multiple/fill/short/judge/true_false 等枚举）
const getTypeLabel = (type?: string): string => {
  if (!type) return '';
  if (['single', 'single_choice'].includes(type)) return '单选题';
  if (['multiple', 'multiple_choice'].includes(type)) return '多选题';
  if (['fill', 'fill_in'].includes(type)) return '填空题';
  if (['short', 'short_answer'].includes(type)) return '简答题';
  if (['judge', 'true_false'].includes(type)) return '判断题';
  return '选择题';
};

const isObjective = (type?: string): boolean =>
  ['single', 'single_choice', 'multiple', 'multiple_choice', 'judge', 'true_false'].includes(type || '');
const isFill = (type?: string): boolean => ['fill', 'fill_in'].includes(type || '');
const isShort = (type?: string): boolean => ['short', 'short_answer'].includes(type || '');

// 规范化选项列表：兼容对象数组 [{key,text}]、字符串数组 ['A. 莫奈']、JSON 字符串；判断题无选项时自动补「正确/错误」
const normOptions = (item: any): Array<{ key: string; text: string }> => {
  const qType: string = item?.type || '';
  let raw = item?.options;
  if ((!raw || (Array.isArray(raw) && raw.length === 0)) && ['judge', 'true_false'].includes(qType)) {
    return [
      { key: 'A', text: '正确' },
      { key: 'B', text: '错误' },
    ];
  }
  if (!raw) return [];
  if (typeof raw === 'string') {
    try {
      raw = JSON.parse(raw);
    } catch {
      return [];
    }
  }
  if (!Array.isArray(raw)) return [];
  const keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
  return raw.map((o: any, idx: number) => {
    if (o && typeof o === 'object') {
      return {
        key: String(o.key || o.label || o.value || keys[idx] || '').trim().toUpperCase(),
        text: String(o.text ?? o.content ?? o.title ?? '').trim(),
      };
    }
    const s = String(o).trim();
    const m = s.match(/^([A-Za-z])[\.、\s\-:]+\s*(.*)$/);
    if (m) return { key: m[1].toUpperCase(), text: m[2].trim() };
    return { key: keys[idx] || `Opt${idx + 1}`, text: s };
  });
};

// 题干中的连续下划线渲染为 <u>，让填空题的「占位」一目了然
const renderContent = (content: any): string =>
  String(content ?? '').replace(/(_{2,})/g, '<u>$1</u>');

// 用户是否选中该选项
const isUserPicked = (item: any, key: string): boolean => {
  const ua = item?.user_answer;
  if (Array.isArray(ua)) return ua.some((v: any) => String(v).toUpperCase() === key);
  return String(ua ?? '').toUpperCase().includes(key);
};

// 该选项是否为标准答案（判断题标准答案可能是 A/正确/B/错误/T/F 等，统一归一化再比对）
const isCorrectPick = (item: any, key: string): boolean => {
  const ca = item?.correct_answer;
  if (ca == null) return false;
  const norm = (v: string): string => {
    const up = String(v).trim().toUpperCase();
    if (['T', 'TRUE', 'YES', '正确', '对', '√'].includes(up)) return 'A';
    if (['F', 'FALSE', 'NO', '错误', '错', '×'].includes(up)) return 'B';
    return up;
  };
  if (Array.isArray(ca)) return ca.some((v: any) => norm(String(v)) === key);
  return norm(String(ca)) === key;
};

// 该选项为「我选了且与标准答案不符」
const isWrongPick = (item: any, key: string): boolean =>
  isUserPicked(item, key) && !isCorrectPick(item, key);

// 填空题逐空对照：把「我填的」按序展开，对照「标准答案」的对应空
const fillPairs = (item: any): Array<{ mine: string; answer: string }> => {
  const rawMine = item?.user_answer;
  let mineArr: string[] = [];
  if (Array.isArray(rawMine)) mineArr = rawMine.map(String);
  else if (typeof rawMine === 'string' && rawMine.trim()) mineArr = rawMine.split(/[,，;；]\s*/).filter(Boolean);
  const rawAns = item?.correct_answer;
  let ansArr: string[] = [];
  if (Array.isArray(rawAns)) ansArr = rawAns.map(String);
  else if (typeof rawAns === 'string' && rawAns.trim()) ansArr = [rawAns];
  const len = Math.max(mineArr.length, ansArr.length, 1);
  return Array.from({ length: len }, (_, i) => ({
    mine: mineArr[i] || '',
    answer: ansArr[i] || '',
  }));
};

const fmtAnswer = (a: any): string => {
  if (Array.isArray(a)) return a.length ? a.join(', ') : '未作答';
  if (a && typeof a === 'object') return JSON.stringify(a);
  return String(a ?? '') || '未作答';
};

const hasTime = computed(() => {
  const t = report.value?.time_spent;
  return t != null && t !== '' && Number(t) > 0;
});

const formattedTime = computed(() => {
  if (!report.value) return '0秒';
  const sec = Number(report.value.time_spent) || 0;
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

.type-badge {
  display: inline-block;
  background: #e0f2fe;
  color: #0284c7;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
}

.opt-compare {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 10px 0;
}

.opt-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 7px 10px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: #475569;
}

.opt-item .opt-prefix {
  font-weight: 800;
  color: #0f172a;
  min-width: 14px;
}

.opt-item .opt-content {
  flex: 1;
  line-height: 1.5;
}

.opt-item .opt-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  white-space: nowrap;
}

.opt-item.opt-mine .opt-tag.mine {
  background: #dbeafe;
  color: #1d4ed8;
}

.opt-item.opt-correct .opt-tag.correct {
  background: #dcfce7;
  color: #15803d;
}

.opt-item.opt-wrong .opt-tag.wrong {
  background: #fee2e2;
  color: #b91c1c;
}

.opt-item.opt-correct {
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.opt-item.opt-wrong {
  border-color: #fecaca;
  background: #fef2f2;
}

.fill-compare {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 10px 0;
}

.fill-pair {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 7px 10px;
  display: grid;
  grid-template-columns: 64px 1fr 1fr;
  gap: 8px;
  font-size: 13px;
}

.fill-blank {
  font-weight: 700;
  color: #6366f1;
}

.fill-mine {
  color: #1d4ed8;
}

.fill-answer {
  color: #15803d;
}

.fill-mine,
.fill-answer {
  line-height: 1.5;
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

.ans-box.correct {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.ans-box.explanation {
  background: #fffbeb;
  border: 1px solid #fde68a;
}

.ans-box.correct .lbl {
  color: #15803d;
}

.ans-box.explanation .lbl {
  color: #b45309;
}

.no-explanation {
  font-size: 12px;
  color: #94a3b8;
  padding: 2px 2px 0;
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
