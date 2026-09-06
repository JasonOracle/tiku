<!--
 * [变更日志]
 * 修改时间：2026-09-06 20:30:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.2 新增阅卷大厅: 待批阅列表(异常红点)/批阅详情(踩分点+学生原文+AI建议)/一键采信AI/人工定分发布/重新触发AI]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="filters">
        <el-select v-model="examId" placeholder="全部试卷" clearable style="width: 220px" @change="loadRecords">
          <el-option v-for="e in myExams" :key="e.id" :label="e.title" :value="e.id" />
        </el-select>
        <el-checkbox v-model="onlyError" @change="loadRecords">仅看 AI 异常</el-checkbox>
      </div>
      <el-button text type="primary" @click="loadRecords">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <el-table :data="records" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
      <el-table-column prop="record_id" label="答卷ID" width="90" />
      <el-table-column prop="exam_title" label="试卷" min-width="180" show-overflow-tooltip />
      <el-table-column prop="username" label="考生" width="130" />
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
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="openGrading(row)">批阅</el-button>
          <el-button v-if="row.ai_error || !row.has_ai_suggestion" type="warning" text size="small" @click="retryAi(row)">
            重新触发AI
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="page"
        :page-size="size"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadRecords"
      />
    </div>

    <!-- 批阅弹窗 -->
    <el-dialog v-model="dialogVisible" :title="`批阅答卷 #${detail?.record_id} — ${detail?.exam_title || ''}（${detail?.username}）`"
               width="860px" top="30px" destroy-on-close>
      <div v-loading="detailLoading">
        <el-alert v-if="detail?.ai_error" type="error" :closable="false" show-icon style="margin-bottom: 12px"
                  :title="`AI 批阅失败：${detail.ai_error}`" description="可人工逐题定分发布，或关闭弹窗后点击「重新触发AI」。" />

        <div class="objective-summary" v-if="detail">
          <span>客观题自动判卷得分：<strong style="color: #0284c7">{{ detail.objective_score }}</strong> 分</span>
          <span style="margin-left: 24px">试卷总分：{{ detail.total_score }} 分（及格 {{ detail.pass_score }} 分）</span>
        </div>

        <div v-for="(q, idx) in shortQuestions" :key="q.question_id" class="grade-item">
          <div class="grade-head">
            <span class="grade-index">简答题 {{ idx + 1 }}</span>
            <el-tag size="small" type="primary">{{ q.eq_score }} 分</el-tag>
            <span style="font-size: 12px; color: #94a3b8">题目ID #{{ q.question_id }}</span>
          </div>
          <div class="grade-title">{{ q.title }}</div>
          <div class="grade-row"><span class="grade-label">标准答案</span><span>{{ q.reference_answer }}</span></div>
          <div class="grade-row">
            <span class="grade-label">踩分点</span>
            <div class="points-wrap">
              <el-tag v-for="(p, pi) in q.grading_points" :key="pi" size="small" type="success" effect="plain">{{ p }}</el-tag>
              <span v-if="!q.grading_points || !q.grading_points.length" style="color: #94a3b8; font-size: 12px">未配置踩分点</span>
            </div>
          </div>
          <div class="grade-row student"><span class="grade-label">学生作答</span><div class="student-answer">{{ q.user_answer[0] || '（未作答）' }}</div></div>
          <div class="grade-row" v-if="q.ai_comment">
            <span class="grade-label">AI 评语</span>
            <span style="color: #9a3412">{{ q.ai_comment }}</span>
          </div>
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

        <el-empty v-if="detail && shortQuestions.length === 0" description="该答卷没有简答题" />
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="warning" plain :disabled="!hasAiSuggestion || !detail || detail.status !== 'pending_grading'"
                   @click="confirmAcceptAi" :loading="publishing">
          一键采信全部 AI 评分
        </el-button>
        <el-button type="primary" :disabled="!detail || detail.status !== 'pending_grading'" @click="confirmManual" :loading="publishing">
          定分并发布成绩
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Refresh } from '@element-plus/icons-vue';
import request from '../../utils/request';

const loading = ref(false);
const records = ref<any[]>([]);
const myExams = ref<any[]>([]);
const examId = ref<number | null>(null);
const onlyError = ref(false);
const page = ref(1);
const size = 10;
const total = ref(0);

const dialogVisible = ref(false);
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

const loadExams = async () => {
  try {
    const res: any = await request.get('/api/v1/admin/exams', { params: { size: 100 } });
    myExams.value = res.items || [];
  } catch (e) {
    myExams.value = [];
  }
};

const loadRecords = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/grading/records', {
      params: { exam_id: examId.value || undefined, page: page.value, size }
    });
    records.value = onlyError.value ? (res.items || []).filter((r: any) => r.ai_error) : res.items || [];
    total.value = onlyError.value ? records.value.length : res.total || 0;
  } finally {
    loading.value = false;
  }
};

const openGrading = async (row: any) => {
  dialogVisible.value = true;
  detailLoading.value = true;
  detail.value = null;
  try {
    const res: any = await request.get(`/api/v1/admin/grading/records/${row.record_id}`);
    detail.value = res;
    scoreMap.value = {};
    for (const q of res.questions || []) {
      if (q.type === 'short') {
        // 默认预填 AI 建议分，无建议则给 0
        scoreMap.value[q.question_id] = q.ai_suggested_score != null ? q.ai_suggested_score : (q.final_score ?? 0);
      }
    }
  } finally {
    detailLoading.value = false;
  }
};

const confirmAcceptAi = async () => {
  publishing.value = true;
  try {
    const res: any = await request.post(`/api/v1/admin/grading/records/${detail.value.record_id}/confirm`, { accept_ai: true });
    ElMessage.success(res.message || '成绩已发布');
    dialogVisible.value = false;
    loadRecords();
  } finally {
    publishing.value = false;
  }
};

const confirmManual = async () => {
  publishing.value = true;
  try {
    const scores: Record<string, number> = {};
    for (const q of shortQuestions.value) scores[String(q.question_id)] = scoreMap.value[q.question_id] ?? 0;
    const res: any = await request.post(`/api/v1/admin/grading/records/${detail.value.record_id}/confirm`, { accept_ai: false, scores });
    ElMessage.success(res.message || '成绩已发布');
    dialogVisible.value = false;
    loadRecords();
  } finally {
    publishing.value = false;
  }
};

const retryAi = async (row: any) => {
  try {
    const res: any = await request.post(`/api/v1/admin/grading/records/${row.record_id}/retry-ai`);
    ElMessage.success(res.message || '已重新触发');
    setTimeout(loadRecords, 1200);
  } catch (e) { /* 拦截器已提示 */ }
};

onMounted(() => {
  loadExams();
  loadRecords();
});
</script>

<style scoped>
.page-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  display: flex;
  gap: 16px;
  align-items: center;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
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

.score-row {
  align-items: center;
}
</style>
