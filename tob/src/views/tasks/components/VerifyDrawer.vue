<!--
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗重写：任务核验抽屉，旧主观题批阅/grades体系已删除]
-->
<template>
  <el-drawer
    :model-value="visible"
    :title="`任务核验 — ${taskTitle || ''}`"
    size="640px"
    destroy-on-close
    @close="handleClose"
  >
    <div v-loading="loading" class="drawer-body">
      <div v-if="total > 0" class="progress-bar">
        <span class="progress-text">第 {{ currentIndex + 1 }} / {{ total }} 份</span>
        <el-progress :percentage="Math.round(((currentIndex + 1) / total) * 100)" :show-text="false" style="flex: 1" />
      </div>

      <el-alert v-if="detail?.ai_result?.error" type="error" :closable="false" show-icon style="margin-bottom: 12px"
                :title="`AI 核验异常：${detail.ai_result.error}`" description="可人工定分确认，或点击「重新触发 AI」。">
        <template #default />
      </el-alert>

      <div v-if="detail" class="objective-summary">
        <span>成员ID：<strong>{{ detail.user_id }}</strong></span>
        <span style="margin-left: 16px">任务：{{ detail.task_title }}</span>
        <span style="margin-left: 16px">提交：{{ submitTime }}</span>
      </div>

      <div v-if="detail?.ai_result?.suggested_score != null" class="ai-suggest">
        🤖 AI 核验建议分：{{ detail.ai_result.suggested_score }} 分
        <span v-if="detail.ai_result.comments"> | 理由：{{ detail.ai_result.comments }}</span>
        <el-button text size="small" type="primary" @click="applyAi">采用 AI 分</el-button>
      </div>

      <div v-for="(it, idx) in answerItems" :key="idx" class="grade-item">
        <div class="grade-head">
          <span class="grade-index">作答 {{ idx + 1 }}</span>
          <span style="font-size: 12px; color: #94a3b8">条目 #{{ it.resource_id }}</span>
        </div>
        <div v-if="it.content" class="grade-title">{{ it.content }}</div>
        <div class="grade-row student">
          <span class="grade-label">成员作答</span>
          <div class="student-answer">{{ fmtAnswer(it.answer) }}</div>
        </div>
      </div>

      <div class="grade-row score-row" v-if="detail">
        <span class="grade-label">最终得分</span>
        <el-input-number v-model="finalScore" :min="0" :max="1000" size="small" />
      </div>

      <el-empty v-if="!loading && total === 0" description="该任务暂无待核验提交" />
    </div>

    <template #footer>
      <div class="drawer-footer">
        <el-button
          v-if="detail"
          type="warning"
          plain
          :loading="retrying"
          @click="retryAi"
        >
          重新触发 AI
        </el-button>
        <el-button type="primary" size="large" :loading="publishing" :disabled="!detail" @click="publishAndNext">
          ✔ 确认定分
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
  taskId: number | null;
  taskTitle: string;
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
const finalScore = ref(0);

const total = computed(() => records.value.length);
const answerItems = computed(() => detail.value?.items || []);
const submitTime = computed(() => {
  const rec = records.value[currentIndex.value];
  return rec?.submit_time || '';
});

const fmtAnswer = (a: any): string => {
  if (Array.isArray(a)) return a.join('\n') || '（未作答）';
  if (a && typeof a === 'object') return JSON.stringify(a);
  return String(a ?? '') || '（未作答）';
};

const loadPendingList = async (): Promise<void> => {
  if (!props.taskId) return;
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/verifications/pending', {
      params: { task_id: props.taskId }
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
  const res: any = await request.get(`/api/v1/admin/verifications/${recordId}`);
  detail.value = res;
  finalScore.value = res.ai_result?.suggested_score ?? res.score ?? 0;
};

const applyAi = (): void => {
  if (detail.value?.ai_result?.suggested_score != null) {
    finalScore.value = detail.value.ai_result.suggested_score;
  }
};

const publishAndNext = async (): Promise<void> => {
  if (!detail.value) return;
  publishing.value = true;
  try {
    const res: any = await request.post(
      `/api/v1/admin/verifications/${detail.value.record_id}/confirm`,
      { accept_ai_suggestion: true, final_score: finalScore.value, comments: detail.value?.ai_result?.comments || '' }
    );
    ElMessage.success(res.message || '核验完成');
    emit('graded');
    await moveNext();
  } finally {
    publishing.value = false;
  }
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
    await request.post(`/api/v1/admin/ai/verify/${detail.value.record_id}`);
    ElMessage.success('已重新触发 AI 核验，请稍后刷新查看');
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
