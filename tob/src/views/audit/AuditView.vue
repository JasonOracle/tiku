<!--
 * [变更日志]
 * 修改时间：2026-09-06 20:40:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.2 新增审计日志查询 (仅超管): 双域留痕(人类/AI)全量检索与详情展开]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="filters">
        <el-select v-model="filters.operator_type" placeholder="全部操作者" clearable style="width: 150px" @change="loadLogs">
          <el-option label="人类操作" value="admin" />
          <el-option label="AI 员工" value="ai" />
        </el-select>
        <el-select v-model="filters.target_type" placeholder="全部对象" clearable style="width: 150px" @change="loadLogs">
          <el-option label="条目" value="resource" />
          <el-option label="任务" value="exam" />
          <el-option label="提交" value="record" />
          <el-option label="成员" value="admin" />
        </el-select>
        <el-input v-model="filters.keyword" placeholder="搜索动作摘要..." clearable style="width: 220px" @change="loadLogs" />
      </div>
    </div>

    <el-table :data="logs" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="audit-detail">
            <div class="detail-block" v-if="row.before_data">
              <strong>操作前快照</strong>
              <pre>{{ JSON.stringify(row.before_data, null, 2) }}</pre>
            </div>
            <div class="detail-block" v-if="row.after_data">
              <strong>操作后数据</strong>
              <pre>{{ JSON.stringify(row.after_data, null, 2) }}</pre>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="操作者" width="150">
        <template #default="{ row }">
          <el-tag :type="row.operator_type === 'ai' ? 'warning' : 'primary'" size="small">
            {{ row.operator_type === 'ai' ? '🤖 AI员工' : '👤 ' + (row.operator_name || '未知') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="action_type" label="动作" width="120" />
      <el-table-column prop="target_type" label="对象" width="90" />
      <el-table-column prop="summary" label="摘要" min-width="280" show-overflow-tooltip />
      <el-table-column prop="created_at" label="时间" width="170" />
    </el-table>

    <div class="pagination-bar">
      <el-pagination v-model:current-page="page" :page-size="size" :total="total"
                     layout="total, prev, pager, next" @current-change="loadLogs" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import request from '../../utils/request';

const logs = ref<any[]>([]);
const loading = ref(false);
const filters = reactive({ operator_type: '', target_type: '', keyword: '' });
const page = ref(1);
const size = 20;
const total = ref(0);

const loadLogs = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/audit', {
      params: {
        operator_type: filters.operator_type || undefined,
        target_type: filters.target_type || undefined,
        keyword: filters.keyword || undefined,
        page: page.value,
        size
      }
    });
    logs.value = res.items || [];
    total.value = res.total || 0;
  } finally {
    loading.value = false;
  }
};

onMounted(loadLogs);
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
  gap: 12px;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.audit-detail {
  padding: 8px 16px;
  display: flex;
  gap: 24px;
}

.detail-block {
  flex: 1;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px 14px;
}

.detail-block pre {
  margin: 6px 0 0;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  color: #334155;
}
</style>
