<!--
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Agnes-3.0-flash (ZCode)
 * 修改内容：[1. 状态文案「待核验」统一改为「审核中」; 2. 「继续测试」入口收窄并净化卡片：仅当后端 can_continue（人工审核 + 含简答题 + 审核中未出成绩 + 未过截止）为真时显示，且此时只显示「继续测试」按钮，不再并列展示分数与查看成绩；3. 继续测试语义改为保留作答续答（提示文案同步改为可修改后重新交卷、成绩仍待人工核验），接口改为 POST /tasks/{id}/continue；4. 清理已废弃的 retake/link-btn 样式]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[1. 修复点击已参加试卷跳转白屏Bug：已提交任务通过 record_id 直接定向至成绩报告页 /report?record_id=...，不再错误调用开考作答接口; 2. 补齐已参加列表中的 record_id 映射透传]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[1. 顶部标题由我的任务改为我的测试; 2. 升级三态Tab: 进行中、未开始、已参加及动态计数统计; 3. 列表卡片重构为首页同款圆角阴影卡片并展示真实分类、限时标签、题目/总分/及格指标; 4. 优化不同状态下的按钮引导]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗重写：待办/已提交两态，直接对接成员任务接口，旧三态/解析锁体系已删除]
-->
<template>
  <div class="page">
    <NavBar title="我的测试" />
    
    <div class="content">
      <!-- 三态 Tabs 切换 -->
      <div class="tabs">
        <button
          v-for="t in tabs"
          :key="t.key"
          class="tab"
          :class="{ active: activeTab === t.key }"
          @click="activeTab = t.key"
        >
          {{ t.label }}
          <span class="count">{{ grouped[t.key].length }}</span>
        </button>
      </div>

      <!-- 加载与空状态 -->
      <div v-if="loading" class="state-tip">
        <div class="loading-spinner"></div>
        <p>数据加载中...</p>
      </div>
      
      <div v-else-if="grouped[activeTab].length === 0" class="state-tip">
        <div class="empty-icon-wrap">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="4" width="20" height="16" rx="2"/>
            <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
          </svg>
        </div>
        <p class="empty-text">{{ emptyText[activeTab] }}</p>
      </div>

      <!-- 试卷卡片列表（参考首页精美卡片样式） -->
      <div v-else class="exam-list">
        <div
          v-for="exam in grouped[activeTab]"
          :key="exam.task_id"
          class="exam-card"
        >
          <div class="card-info">
            <!-- 标签行：所属分类 + 限时标签 + 审核/完成状态 -->
            <div class="card-badge-row">
              <span v-if="exam.category_name" class="cat-badge">
                {{ exam.category_name }}
              </span>
              <span v-if="exam.is_timed && exam.time_limit" class="mode-tag timed">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                {{ exam.time_limit }}分钟限时
              </span>
              <span v-if="exam.status && exam.status !== 'pending'" class="status-pill" :class="exam.status">
                {{ statusLabel(exam.status) }}
              </span>
            </div>

            <!-- 试卷标题 -->
            <h3 class="exam-title">{{ exam.title }}</h3>

            <!-- 指标徽章：题目 | 总分 | 及格分 -->
            <div class="meta-chips">
              <span class="chip">
                <span class="chip-label">题目</span>
                <span class="chip-val">{{ exam.question_count }}题</span>
              </span>
              <span class="chip-dot">•</span>
              <span class="chip">
                <span class="chip-label">总分</span>
                <span class="chip-val">{{ exam.total_score }}分</span>
              </span>
              <span class="chip-dot">•</span>
              <span class="chip">
                <span class="chip-label">及格</span>
                <span class="chip-val">{{ exam.pass_score }}分</span>
              </span>
            </div>

            <!-- 时间元数据行 -->
            <div v-if="activeTab === 'upcoming' && exam.start_time" class="time-meta">
              开考时间：{{ fmt(exam.start_time) }}
            </div>
            <div v-else-if="activeTab === 'ongoing' && exam.deadline" class="time-meta">
              截止时间：{{ fmt(exam.deadline) }}
            </div>
            <div v-else-if="activeTab === 'completed' && exam.submit_time" class="time-meta">
              提交时间：{{ exam.submit_time }}
            </div>
          </div>

          <!-- 右侧行动区 -->
          <div class="card-action">
            <template v-if="activeTab === 'ongoing'">
              <button class="action-btn" @click.stop="handleCardClick(exam)">
                <span>开始</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
              </button>
            </template>
            <template v-else-if="activeTab === 'upcoming'">
              <button class="action-btn locked" disabled>
                <span>未开始</span>
              </button>
            </template>
            <template v-else>
              <div class="result-action">
                <!-- 审核中（含简答的人工审核卷、成绩未出）：仅提供「继续测试」回考场续答，
                     此时不显示分数、也不提供查看成绩入口，避免「已出分」与「待续答」自相矛盾 -->
                <template v-if="exam.can_continue">
                  <button class="action-btn" :disabled="continuing" @click.stop="askContinue(exam)">
                    {{ continuing ? '进入中...' : '继续测试' }}
                  </button>
                </template>
                <template v-else>
                  <span v-if="exam.score !== null && exam.score !== undefined" class="score-display">
                    <span class="score-num">{{ exam.score }}</span>
                    <span class="score-unit">分</span>
                  </span>
                  <button class="action-btn completed-btn" @click.stop="handleCardClick(exam)">
                    <span>查看</span>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
                  </button>
                </template>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <AppModal
      v-model="continueModalVisible"
      title="继续测试"
      :message="`将带着《${pendingContinue?.title || ''}》上次的作答回到考场，可修改后重新交卷，成绩仍待人工核验。确定继续吗？`"
      type="warning"
      confirm-text="继续作答"
      @confirm="onConfirmContinue"
    />
    <AppModal
      v-model="continueErrorVisible"
      title="无法继续测试"
      :message="continueErrorMsg"
      type="danger"
      :show-cancel="false"
      confirm-text="知道了"
    />

    <TabBar active="mytasks" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import NavBar from '../../components/NavBar.vue';
import TabBar from '../../components/TabBar.vue';
import AppModal from '../../components/AppModal.vue';
import http from '../../utils/http';

const router = useRouter();
const loading = ref(true);

// 继续测试交互状态
const continuing = ref(false);
const continueModalVisible = ref(false);
const continueErrorVisible = ref(false);
const continueErrorMsg = ref('');
const pendingContinue = ref<any>(null);

// 三态定义：进行中、未开始、已参加
const tabs = [
  { key: 'ongoing', label: '进行中' },
  { key: 'upcoming', label: '未开始' },
  { key: 'completed', label: '已参加' }
] as const;

type TabKey = typeof tabs[number]['key'];
const activeTab = ref<TabKey>('ongoing');

const emptyText: Record<TabKey, string> = {
  ongoing: '当前没有正在进行中的测试',
  upcoming: '暂无未开始的计划测试',
  completed: '暂无已参加的测试记录'
};

const grouped = reactive<Record<TabKey, any[]>>({
  ongoing: [],
  upcoming: [],
  completed: []
});

const fmt = (s?: string | null) => (s ? String(s).replace('T', ' ').slice(0, 16) : '');

const statusLabel = (s: string) => {
  if (s === 'verified') return '已核验';
  if (s === 'pending_verification') return '审核中';
  if (s === 'submitted') return '已交卷';
  return '未完成';
};

const load = async () => {
  loading.value = true;
  try {
    const res: any = await http.get('/api/v1/member/member-tasks');
    const items = res.items || [];
    const now = new Date();

    const ongoingList: any[] = [];
    const upcomingList: any[] = [];
    const completedList: any[] = [];

    for (const item of items) {
      const isDone = ['submitted', 'verified', 'pending_verification'].includes(item.status);
      if (isDone) {
        completedList.push(item);
        continue;
      }

      // 未提交情况下，根据 start_time 判断是否尚未开始
      if (item.start_time) {
        const startTime = new Date(item.start_time);
        if (now < startTime) {
          upcomingList.push(item);
          continue;
        }
      }

      // 其余均为进行中
      ongoingList.push(item);
    }

    grouped.ongoing = ongoingList;
    grouped.upcoming = upcomingList;
    grouped.completed = completedList;
  } finally {
    loading.value = false;
  }
};

const handleCardClick = async (exam: any) => {
  if (activeTab.value === 'upcoming') {
    return;
  }
  // 已参加状态：直接查看成绩与答题报告，杜绝重新请求开考接口导致的拦截或白屏
  if (activeTab.value === 'completed' || ['submitted', 'verified', 'pending_verification'].includes(exam.status)) {
    if (exam.record_id) {
      router.push({ path: '/report', query: { record_id: exam.record_id } });
      return;
    }
    // 兜底查一次历史记录定位 record_id
    try {
      const res: any = await http.get('/api/v1/member/task-records');
      const hit = (res.items || []).find((r: any) => r.task_id === exam.task_id);
      if (hit && hit.record_id) {
        router.push({ path: '/report', query: { record_id: hit.record_id } });
        return;
      }
    } catch {}
  }
  // 进行中状态：进入考场作答
  router.push({ path: '/task', query: { task_id: exam.task_id } });
};

const askContinue = (exam: any) => {
  pendingContinue.value = exam;
  continueModalVisible.value = true;
};

// 继续测试：后端把本人该卷从「审核中」退回「进行中」并保留上次作答，成功后进考场续答
const onConfirmContinue = async () => {
  const exam = pendingContinue.value;
  if (!exam || continuing.value) return;
  continuing.value = true;
  try {
    await http.post(`/api/v1/member/tasks/${exam.task_id}/continue`, {});
    router.push({ path: '/task', query: { task_id: exam.task_id } });
  } catch (err: any) {
    const detail = err?.response?.data?.detail;
    continueErrorMsg.value = typeof detail === 'string' ? detail : '继续测试失败，请稍后重试';
    continueErrorVisible.value = true;
  } finally {
    continuing.value = false;
  }
};

onMounted(load);
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, #eef4ff 0%, #f8fafc 40%);
  padding-bottom: 140px;
  box-sizing: border-box;
  font-family: 'Plus Jakarta Sans', 'Outfit', system-ui, sans-serif;
}

.content {
  padding: 12px 16px;
  max-width: 480px;
  margin: 0 auto;
}

.tabs {
  display: flex;
  background: #ffffff;
  border-radius: 16px;
  padding: 5px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
  margin-bottom: 16px;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.tab {
  flex: 1;
  border: none;
  background: transparent;
  padding: 9px 0;
  font-size: 13px;
  color: #64748b;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.tab.active {
  background: linear-gradient(135deg, #0284c7, #6366f1);
  color: #fff;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
}

.count {
  font-size: 11px;
  background: rgba(0, 0, 0, 0.06);
  padding: 1px 6px;
  border-radius: 99px;
}

.tab.active .count {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

.state-tip {
  text-align: center;
  color: #94a3b8;
  padding: 60px 0;
  font-size: 14px;
}

.empty-icon-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
  opacity: 0.8;
}

.empty-text {
  font-size: 14px;
  color: #94a3b8;
}

.exam-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.exam-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.04), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.exam-card:active {
  transform: scale(0.985);
  box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.03);
}

.card-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.card-badge-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.cat-badge {
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
  background: #f1f5f9;
  color: #475569;
}

.mode-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
}

.mode-tag.timed {
  background: #fff1f2;
  color: #e11d48;
}

.status-pill {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
}

.status-pill.verified {
  background: #ecfdf5;
  color: #059669;
}

.status-pill.pending_verification {
  background: #fffbeb;
  color: #d97706;
}

.status-pill.submitted {
  background: #eff6ff;
  color: #2563eb;
}

.exam-title {
  margin: 3px 0 2px;
  font-size: 15px;
  color: #0f172a;
  font-weight: 800;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta-chips {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.chip-label {
  color: #94a3b8;
  font-size: 11px;
}

.chip-val {
  color: #334155;
  font-weight: 700;
  font-size: 12px;
}

.chip-dot {
  color: #cbd5e1;
  font-size: 10px;
}

.time-meta {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.card-action {
  flex-shrink: 0;
  align-self: center;
}

.action-btn {
  background: linear-gradient(135deg, #0284c7 0%, #6366f1 100%);
  color: #ffffff;
  border: none;
  padding: 8px 14px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.28);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.action-btn:active {
  transform: scale(0.95);
}

.action-btn.locked {
  background: #e2e8f0;
  color: #94a3b8;
  box-shadow: none;
  cursor: not-allowed;
}

.action-btn.completed-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.28);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result-action {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.score-display {
  display: inline-flex;
  align-items: baseline;
  gap: 1px;
}

.score-num {
  font-size: 16px;
  font-weight: 900;
  color: #0f172a;
}

.score-unit {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
}
</style>
