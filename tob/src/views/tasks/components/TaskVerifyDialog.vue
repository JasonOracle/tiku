<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 底层
 * 修改内容：[核验列表表格对齐现代企业级 SaaS 统一设计规范，接入 saas-modern-table 与首行专属底色]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗重写：任务行级核验大厅全屏弹窗，旧阅卷大厅体系已删除]
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="`阅卷管理 — ${taskTitle || ''}`"
    fullscreen
    destroy-on-close
    @close="handleClose"
  >
    <div v-loading="loading">
      <el-table
        :data="records"
        class="saas-modern-table"
        style="width: 100%"
        :header-cell-style="{
          backgroundColor: '#f1f5f9',
          color: '#475569',
          fontWeight: '700',
          fontSize: '13px',
          padding: '14px 16px',
          borderBottom: '1px solid #e2e8f0',
          whiteSpace: 'nowrap'
        }"
        :cell-style="{
          padding: '16px 16px',
          borderBottom: '1px solid #f1f5f9'
        }"
      >
        <el-table-column prop="record_id" label="记录ID" width="90" />
        <el-table-column prop="user_id" label="成员ID" width="100" />
        <el-table-column label="作答" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="font-size: 12px">{{ JSON.stringify(row.answers || []).slice(0, 120) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="AI 状态" width="130">
          <template #default="{ row }">
            <el-tag v-if="row.ai_result?.error" type="danger" size="small">AI 异常</el-tag>
            <el-tag v-else-if="row.ai_result" type="warning" size="small">AI 已核验</el-tag>
            <el-tag v-else type="info" size="small">待核验</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submit_time" label="提交时间" width="170" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="openDetail(row)">核验</el-button>
            <el-button type="warning" text size="small" @click="retryAi(row)">
              重新触发AI
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!records.length" description="该任务暂无待核验提交" />
    </div>

    <el-dialog v-model="detailVisible" :title="`核验记录 #${detail?.record_id || ''}`" width="860px" top="30px" destroy-on-close append-to-body>
      <div v-loading="detailLoading">
        <el-alert v-if="detail?.ai_result?.error" type="error" :closable="false" show-icon style="margin-bottom: 12px"
                  :title="`AI 核验失败：${detail.ai_result.error}`" />
        <div v-if="detail?.ai_result?.suggested_score != null" class="objective-summary">
          AI 建议分：<strong style="color: #0284c7">{{ detail.ai_result.suggested_score }}</strong> 分
          <span v-if="detail.ai_result.comments">（{{ detail.ai_result.comments }}）</span>
        </div>
        <div v-for="(it, idx) in detail?.items || []" :key="idx" class="grade-item">
          <div class="grade-head">
            <span class="grade-index">作答 {{ idx + 1 }}</span>
            <span style="font-size: 12px; color: #94a3b8">条目 #{{ it.resource_id }}</span>
          </div>
          <div v-if="it.content" class="grade-title">{{ it.content }}</div>
          <div class="grade-row student"><span class="grade-label">成员作答</span><div class="student-answer">{{ fmtAnswer(it.answer) }}</div></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">取消</el-button>
        <el-button type="primary" :loading="publishing" @click="confirmManual">定分并确认</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
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
const records = ref<any[]>([]);
const detailVisible = ref(false);
const detailLoading = ref(false);
const publishing = ref(false);
const detail = ref<any>(null);

const fmtAnswer = (a: any): string => {
  if (Array.isArray(a)) return a.join('\n') || '（未作答）';
  if (a && typeof a === 'object') return JSON.stringify(a);
  return String(a ?? '') || '（未作答）';
};

const loadRecords = async (): Promise<void> => {
  if (!props.taskId) return;
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/verifications/pending', {
      params: { task_id: props.taskId }
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
    detail.value = await request.get(`/api/v1/admin/verifications/${row.record_id}`);
  } finally {
    detailLoading.value = false;
  }
};

const confirmManual = async (): Promise<void> => {
  if (!detail.value) return;
  publishing.value = true;
  try {
    const res: any = await request.post(`/api/v1/admin/verifications/${detail.value.record_id}/confirm`, {
      accept_ai_suggestion: true,
      final_score: detail.value.ai_result?.suggested_score ?? 0,
      comments: detail.value.ai_result?.comments ?? ''
    });
    ElMessage.success(res.message || '核验完成');
    detailVisible.value = false;
    emit('graded');
    loadRecords();
  } finally {
    publishing.value = false;
  }
};

const retryAi = async (row: any): Promise<void> => {
  await request.post(`/api/v1/admin/ai/verify/${row.record_id}`);
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
</style>
