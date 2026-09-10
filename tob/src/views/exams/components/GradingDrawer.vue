<!--
 * [变更日志]
 * 修改时间：2026-09-07
 * AI模型：Muse Spark
 * 修改内容：[v1.2 Step3 新建: 主观题批阅抽屉 GradingDrawer (行内待办下钻/进度/简答题作答+标准答案+采分点/AI初评建议/打分微调/确认发布+下一份)]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[适配 SaaS 租户隔离：所有接口经 X-Tenant-ID 透传]
-->
<template>
  <el-drawer
    :model-value="visible"
    :title="`主观题批阅 — ${examTitle || ''}`"
    size="640px"
    destroy-on-close
    @close="handleClose"
  >
    <div v-loading="loading" class="drawer-body">
      <div v-if="total > 0" class="progress-bar">
        <span class="progress-text">第 {{ currentIndex + 1 }} / {{ total }} 份</span>
        <el-progress :percentage="Math.round(((currentIndex + 1) / total) * 100)" :show-text="false" style="flex: 1" />
      </div>

      <el-alert v-if="detail?.ai_error" type="error" :closable="false" show-icon style="margin-bottom: 12px"
                :title="`AI 批阅异常：${detail.ai_error}`" description="可人工逐题定分发布，或点击「重新触发 AI」。">
        <template #default />
      </el-alert>

      <div v-if="detail" class="objective-summary">
        <span>考生：<strong>{{ detail.nickname || detail.username }}</strong></span>
        <span style="margin-left: 16px">客观题得分：<strong style="color: #0284c7">{{ detail.objective_score }}</strong> 分</span>
        <span style="margin-left: 16px">交卷：{{ submitTime }}</span>
      </div>

      <div v-for="(q, idx) in shortQuestions" :key="q.question_id" class="grade-item">
        <div class="grade-head">
          <span class="grade-index">简答题 {{ idx + 1 }}</span>
          <el-tag size="small" type="primary">{{ q.eq_score }} 分</el-tag>
        </div>
        <div class="grade-title">{{ q.title }}</div>
        <div class="grade-row"><span class="grade-label">标准答案</span><span>{{ q.reference_answer || '—' }}</span></div>
        <div class="grade-row">
          <span class="grade-label">采分点</span>
          <div class="points-wrap">
            <el-tag v-for="(p, pi) in q.grading_points" :key="pi" size="small" type="success" effect="plain">{{ p }}</el-tag>
            <span v-if="!q.grading_points || !q.grading_points.length" class="muted">未配置采分点</span>
          </div>
        </div>
        <div class="grade-row student">
          <span class="grade-label">学生作答</span>
          <div class="student-answer">{{ firstAnswer(q) }}</div>
        </div>
        <div v-if="q.ai_suggested_score != null" class="ai-suggest">
          AI 初评建议分：{{ q.ai_suggested_score }} 分 (满分 {{ q.eq_score }} 分)
          <span v-if="q.ai_comment"> | 理由：{{ q.ai_comment }}</span>
        </div>
        <div class="grade-row score-row">
          <span class="grade-label">本题打分</span>
          <el-slider v-model="scoreMap[q.question_id]" :min="0" :max="q.eq_score" :step="1" show-input
                     style="flex: 1" input-size="small" />
          <el-button v-if="q.ai_suggested_score != null" text size="small" type="primary"
                     @click="scoreMap[q.question_id] = q.ai_suggested_score">采用 AI 分</el-button>
        </div>
      </div>

      <el-empty v-if="!loading && total === 0" description="该试卷暂无待批阅答卷" />
      <el-empty v-if="detail && shortQuestions.length === 0" description="该答卷没有简答题" />
    </div>

    <template #footer>
      <div class="drawer-footer">
        <el-button
          v-if="detail && (detail.ai_error || !hasAiSuggestion)"
          type="warning"
          plain
          :loading="retrying"
          @click="retryAi"
        >
          重新触发 AI
        </el-button>
        <el-button
          v-if="hasAiSuggestion"
          type="warning"
          plain
          :loading="publishing"
          :disabled="!detail"
          @click="confirmAcceptAi"
        >
          一键采信 AI
        </el-button>
        <el-button type="primary" size="large" :loading="publishing" :disabled="!detail" @click="publishAndNext">
          确认发布成绩
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';
import request from '../../../utils/request';

const props = defineProps<{
  visible: boolean;
  examId: number | null;
  examTitle: string;
}>();

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void;
  (e: 'graded'): void;
}>();

const loading = ref(false);
const publishing = ref(false);
const retrying = ref(false);
const records = ref<any[]>([]);
const currentIndex = ref(0);
const detail = ref<any>(null);
const scoreMap = ref<Record<number, number>>({});

const total = computed(() => records.value.length);
const shortQuestions = computed(() =>
  (detail.value?.questions || []).filter((q: any) => q.type === 'short')
);
const hasAiSuggestion = computed(() =>
  shortQuestions.value.some((q: any) => q.ai_suggested_score != null)
);
const submitTime = computed(() => {
  const rec = records.value[currentIndex.value];
  return rec?.submit_time || '';
});

const firstAnswer = (q: any): string => {
  const ans = q.user_answer;
  if (Array.isArray(ans)) return ans.join('\n') || '（未作答）';
  return ans || '（未作答）';
};

const loadPendingList = async (): Promise<void> => {
  if (!props.examId) return;
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/grading/records', {
      params: { exam_id: props.examId, page: 1, size: 100 }
    });
    records.value = res.items || [];
    if (currentIndex.value >= records.value.length) currentIndex.value = 0;
    if (records.value.length > 0) {
      await loadDetail(records.value[currentIndex.value].record_id);
    } else {
      detail.value = null;
    }
  } finally {
    loading.value = false;
  }
};

const loadDetail = async (recordId: number): Promise<void> => {
  const res: any = await request.get(`/api/v1/admin/grading/records/${recordId}`);
  detail.value = res;
  scoreMap.value = {};
  for (const q of res.questions || []) {
    if (q.type === 'short') {
      scoreMap.value[q.question_id] = q.ai_suggested_score != null ? q.ai_suggested_score : (q.final_score ?? 0);
    }
  }
};

const publishScores = async (acceptAi: boolean): Promise<boolean> => {
  if (!detail.value) return false;
  publishing.value = true;
  try {
    const payload = acceptAi
      ? { accept_ai: true }
      : {
          accept_ai: false,
          scores: Object.fromEntries(
            shortQuestions.value.map((q: any) => [String(q.question_id), scoreMap.value[q.question_id] ?? 0])
          )
        };
    const res: any = await request.post(
      `/api/v1/admin/grading/records/${detail.value.record_id}/confirm`,
      payload
    );
    ElMessage.success(res.message || '成绩已发布');
    emit('graded');
    return true;
  } finally {
    publishing.value = false;
  }
};

const confirmAcceptAi = async (): Promise<void> => {
  await publishScores(true);
  await moveNext();
};

const publishAndNext = async (): Promise<void> => {
  const ok = await publishScores(false);
  if (ok) await moveNext();
};

const moveNext = async (): Promise<void> => {
  records.value.splice(currentIndex.value, 1);
  if (records.value.length === 0) {
    detail.value = null;
    handleClose();
    return;
  }
  if (currentIndex.value >= records.value.length) currentIndex.value = 0;
  loading.value = true;
  try {
    await loadDetail(records.value[currentIndex.value].record_id);
  } finally {
    loading.value = false;
  }
};

const retryAi = async (): Promise<void> => {
  if (!detail.value) return;
  retrying.value = true;
  try {
    await request.post(`/api/v1/admin/grading/records/${detail.value.record_id}/retry-ai`);
    ElMessage.success('已重新触发 AI 批改，请稍后刷新查看');
    setTimeout(async () => {
      try {
        await loadDetail(detail.value.record_id);
      } catch (e) { /* 拦截器已提示 */ }
    }, 1500);
  } finally {
    retrying.value = false;
  }
};

const handleClose = (): void => {
  emit('update:visible', false);
};

watch(
  () => props.visible,
  (v: boolean) => {
    if (v) {
      currentIndex.value = 0;
      loadPendingList();
    }
  }
);
</script>

<style scoped>
.drawer-body {
  padding-bottom: 12px;
}
.progress-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.progress-text {
  font-weight: 800;
  color: #0f172a;
  white-space: nowrap;
}
.objective-summary {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  color: #0369a1;
  border-radius: 10px;
  padding: 10px 16px;
  font-size: 13px;
  margin-bottom: 14px;
}
.grade-item {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 14px;
  background: #f8fafc;
}
.grade-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.grade-index {
  font-weight: 800;
  color: #0f172a;
}
.grade-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: #0f172a;
}
.grade-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  margin-bottom: 8px;
}
.grade-label {
  width: 70px;
  flex-shrink: 0;
  color: #64748b;
  font-weight: 600;
}
.points-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.muted {
  color: #94a3b8;
  font-size: 12px;
}
.student {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 8px;
  padding: 8px 10px;
}
.student-answer {
  white-space: pre-wrap;
  color: #7c2d12;
  line-height: 1.6;
}
.ai-suggest {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1d4ed8;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  margin-bottom: 8px;
}
.score-row {
  align-items: center;
}
.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 0 4px;
}
</style>
