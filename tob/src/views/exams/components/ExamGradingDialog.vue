<!--
  * [变更日志]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[新建: 试卷行级阅卷大厅全屏弹窗 (待批阅列表 + 逐题定分 + 一键采信 + 重试AI)]
  -->
<template>
  <el-dialog
    :model-value="visible"
    :title="`阅卷大厅 — ${examTitle || ''}`"
    fullscreen
    destroy-on-close
    @close="handleClose"
  >
    <div v-loading="loading">
      <el-table :data="records" stripe style="width: 100%">
        <el-table-column prop="record_id" label="答卷ID" width="90" />
        <el-table-column label="考生" min-width="130">
          <template #default="{ row }">
            <span style="font-weight: 700">{{ row.nickname || row.username }}</span>
            <span v-if="row.nickname" style="font-size: 12px; color: #94a3b8"> ({{ row.username }})</span>
          </template>
        </el-table-column>
        <el-table-column prop="objective_score" label="客观题得分" width="110">
          <template #default="{ row }">
            <span style="font-weight: 700; color: #0284c7">{{ row.objective_score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="short_count" label="简答题数" width="95" align="center" />
        <el-table-column label="AI 状态" width="130">
          <template #default="{ row }">
            <el-tag v-if="row.ai_error" type="danger" size="small">AI 异常</el-tag>
            <el-tag v-else-if="row.has_ai_suggestion" type="warning" size="small">AI 已预批</el-tag>
            <el-tag v-else type="info" size="small">未触发</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submit_time" label="交卷时间" width="170" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="openDetail(row)">批阅</el-button>
            <el-button v-if="row.ai_error || !row.has_ai_suggestion" type="warning" text size="small" @click="retryAi(row)">
              重新触发AI
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!records.length" description="该试卷暂无待批阅答卷" />
    </div>

    <!-- 批阅详情内层弹窗 -->
    <el-dialog v-model="detailVisible" :title="`批阅答卷 #${detail?.record_id || ''}`" width="860px" top="30px" destroy-on-close append-to-body>
      <div v-loading="detailLoading">
        <el-alert v-if="detail?.ai_error" type="error" :closable="false" show-icon style="margin-bottom: 12px"
                  :title="`AI 批阅失败：${detail.ai_error}`" />
        <div class="objective-summary" v-if="detail">
          <span>客观题得分：<strong style="color: #0284c7">{{ detail.objective_score }}</strong> 分</span>
          <span style="margin-left: 24px">试卷总分：{{ detail.total_score }} 分（及格 {{ detail.pass_score }} 分）</span>
        </div>
        <div v-for="(q, idx) in shortQuestions" :key="q.question_id" class="grade-item">
          <div class="grade-head">
            <span class="grade-index">简答题 {{ idx + 1 }}</span>
            <el-tag size="small" type="primary">{{ q.eq_score }} 分</el-tag>
          </div>
          <div class="grade-title">{{ q.title }}</div>
          <div class="grade-row"><span class="grade-label">标准答案</span><span>{{ q.reference_answer }}</span></div>
          <div class="grade-row student"><span class="grade-label">学生作答</span><div class="student-answer">{{ firstAnswer(q) }}</div></div>
          <div class="grade-row score-row">
            <span class="grade-label">本题定分</span>
            <el-input-number v-model="scoreMap[q.question_id]" :min="0" :max="q.eq_score" size="small" />
            <span style="font-size: 12px; color: #94a3b8; margin-left: 8px">
              AI 建议：{{ q.ai_suggested_score ?? '无' }} 分
              <el-button v-if="q.ai_suggested_score != null" text size="small" type="primary"
                         @click="scoreMap[q.question_id] = q.ai_suggested_score">采用</el-button>
            </span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">取消</el-button>
        <el-button type="warning" plain :disabled="!hasAiSuggestion" :loading="publishing" @click="confirmAcceptAi">
          一键采信全部 AI 评分
        </el-button>
        <el-button type="primary" :loading="publishing" @click="confirmManual">定分并发布成绩</el-button>
      </template>
    </el-dialog>
  </el-dialog>
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
const records = ref<any[]>([]);
const detailVisible = ref(false);
const detailLoading = ref(false);
const publishing = ref(false);
const detail = ref<any>(null);
const scoreMap = ref<Record<number, number>>({});

const shortQuestions = computed(() =>
  (detail.value?.questions || []).filter((q: any) => q.type === 'short')
);

const hasAiSuggestion = computed(() =>
  shortQuestions.value.some((q: any) => q.ai_suggested_score != null)
);

const firstAnswer = (q: any): string => {
  const ans = q.user_answer;
  if (Array.isArray(ans)) return ans.join('\n') || '（未作答）';
  return ans || '（未作答）';
};

const loadRecords = async (): Promise<void> => {
  if (!props.examId) return;
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/grading/records', {
      params: { exam_id: props.examId, page: 1, size: 100 }
    });
    records.value = res.items || [];
  } finally {
    loading.value = false;
  }
};

const openDetail = async (row: any): Promise<void> => {
  detailVisible.value = true;
  detailLoading.value = true;
  try {
    const res: any = await request.get(`/api/v1/admin/grading/records/${row.record_id}`);
    detail.value = res;
    scoreMap.value = {};
    for (const q of res.questions || []) {
      if (q.type === 'short') {
        scoreMap.value[q.question_id] = q.ai_suggested_score != null ? q.ai_suggested_score : (q.final_score ?? 0);
      }
    }
  } finally {
    detailLoading.value = false;
  }
};

const confirmAcceptAi = async (): Promise<void> => {
  if (!detail.value) return;
  publishing.value = true;
  try {
    const res: any = await request.post(`/api/v1/admin/grading/records/${detail.value.record_id}/confirm`, { accept_ai: true });
    ElMessage.success(res.message || '成绩已发布');
    detailVisible.value = false;
    emit('graded');
    loadRecords();
  } finally {
    publishing.value = false;
  }
};

const confirmManual = async (): Promise<void> => {
  if (!detail.value) return;
  publishing.value = true;
  try {
    const scores: Record<string, number> = {};
    for (const q of shortQuestions.value) scores[String(q.question_id)] = scoreMap.value[q.question_id] ?? 0;
    const res: any = await request.post(`/api/v1/admin/grading/records/${detail.value.record_id}/confirm`, { accept_ai: false, scores });
    ElMessage.success(res.message || '成绩已发布');
    detailVisible.value = false;
    emit('graded');
    loadRecords();
  } finally {
    publishing.value = false;
  }
};

const retryAi = async (row: any): Promise<void> => {
  await request.post(`/api/v1/admin/grading/records/${row.record_id}/retry-ai`);
  ElMessage.success('已重新触发');
  setTimeout(loadRecords, 1200);
};

const handleClose = (): void => {
  emit('update:visible', false);
};

watch(() => props.visible, (v: boolean) => {
  if (v) loadRecords();
});
</script>

<style scoped>
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

.grade-index { font-weight: 800; color: #0f172a; }
.grade-title { font-weight: 600; margin-bottom: 10px; color: #0f172a; }

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

.score-row { align-items: center; }
</style>
