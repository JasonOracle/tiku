<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[全面接入全局 SaaS 列表规范 list-layout.css：1. 消除页面和表格硬边框，改用高定立体弥散阴影；2. 表格仅首行赋予淡蓝灰底色，列宽合理扩充杜绝字形折行；3. 升级操作者/动作/对象胶囊体系；4. 快照详情块采用精致内嵌浅灰圆角卡片]
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

    <!-- 审计日志表格 (无硬边框，仅首行背景与微划线) -->
    <el-table
      :data="logs"
      v-loading="loading"
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
      <el-table-column prop="id" label="ID" width="80" align="center">
        <template #default="{ row }">
          <span class="col-id-text">{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作者" width="160" align="center">
        <template #default="{ row }">
          <span class="prop-pill" :style="row.operator_type === 'ai' ? 'background: #fdf4ff; color: #c026d3' : 'background: #eff6ff; color: #1d4ed8'">
            {{ row.operator_type === 'ai' ? '🤖 AI员工' : '👤 ' + (row.operator_name || '人类操作') }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="action_type" label="动作" width="130" align="center">
        <template #default="{ row }">
          <span class="prop-pill">{{ row.action_type }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="target_type" label="对象" width="110" align="center">
        <template #default="{ row }">
          <span class="muted-gray-text">{{ row.target_type }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="summary" label="摘要" min-width="280" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="cell-main-title">{{ row.summary }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="180" align="center">
        <template #default="{ row }">
          <span class="muted-gray-text">{{ row.created_at }}</span>
        </template>
      </el-table-column>
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
