<!--
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗重写：待核验队列+AI核验触发+确认定分，旧阅卷体系已删除]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="title">待核验任务提交</div>
      <el-button text type="primary" @click="loadRecords">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <el-table :data="records" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
      <el-table-column prop="record_id" label="记录ID" width="90" />
      <el-table-column prop="task_id" label="任务ID" width="90" />
      <el-table-column prop="user_id" label="成员ID" width="90" />
      <el-table-column label="作答" min-width="220" show-overflow-tooltip>
        <template #default="{ row }">
          <span style="font-size: 12px">{{ JSON.stringify(row.answers || []).slice(0, 120) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="AI 建议" min-width="160">
        <template #default="{ row }">
          <span v-if="row.ai_result" style="font-size: 12px">{{ JSON.stringify(row.ai_result).slice(0, 100) }}</span>
          <el-tag v-else type="info" size="small">未核验</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button type="warning" text size="small" :loading="aiLoading === row.record_id" @click="triggerAi(row)">AI 核验</el-button>
          <el-button type="primary" text size="small" @click="openConfirm(row)">确认定分</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="`核验记录 #${confirming?.record_id}`" width="460px" destroy-on-close>
      <el-form label-width="90px">
        <el-form-item label="最终得分">
          <el-input-number v-model="confirmForm.final_score" :min="0" :max="1000" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="confirmForm.comments" type="textarea" :rows="3" placeholder="核验意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="doConfirm">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Refresh } from '@element-plus/icons-vue';
import request from '../../utils/request';

const loading = ref(false);
const saving = ref(false);
const aiLoading = ref<number | null>(null);
const records = ref<any[]>([]);
const dialogVisible = ref(false);
const confirming = ref<any>(null);
const confirmForm = reactive({ final_score: 0, comments: '' });

const loadRecords = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/verifications/pending');
    records.value = res.items || [];
  } finally {
    loading.value = false;
  }
};

const triggerAi = async (row: any) => {
  aiLoading.value = row.record_id;
  try {
    const res: any = await request.post(`/api/v1/admin/ai/verify/${row.record_id}`);
    ElMessage.success(res.message || 'AI 核验完成');
    loadRecords();
  } finally {
    aiLoading.value = null;
  }
};

const openConfirm = (row: any) => {
  confirming.value = row;
  confirmForm.final_score = row.ai_result?.suggested_score ?? 0;
  confirmForm.comments = row.ai_result?.comments ?? '';
  dialogVisible.value = true;
};

const doConfirm = async () => {
  saving.value = true;
  try {
    await request.post(`/api/v1/admin/verifications/${confirming.value.record_id}/confirm`, {
      accept_ai_suggestion: true,
      final_score: confirmForm.final_score,
      comments: confirmForm.comments
    });
    ElMessage.success('核验完成');
    dialogVisible.value = false;
    loadRecords();
  } finally {
    saving.value = false;
  }
};

onMounted(loadRecords);
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

.title {
  font-size: 16px;
  font-weight: 800;
  color: #0f172a;
}
</style>
