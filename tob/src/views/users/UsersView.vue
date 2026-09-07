<!--
 * [变更日志]
 * 修改时间：2026-09-07 00:42:00
 * AI模型：Gemini 系列
 * 修改内容：[根据需求清理冗余的全站答题明细页标签，精简保留 C 端注册用户管理列表]
-->
<template>
  <div class="page-card">
    <div class="header-bar" style="margin-bottom: 16px; font-weight: 700; font-size: 16px; color: #1e293b">
      注册 C端用户列表
    </div>
    <el-table :data="users" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="昵称" min-width="130">
        <template #default="{ row }">
          <span style="font-weight: 700">{{ row.nickname || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column label="性别" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.gender === 'male'" type="primary" size="small">男</el-tag>
          <el-tag v-else-if="row.gender === 'female'" type="danger" size="small">女</el-tag>
          <span v-else style="color: #cbd5e1">—</span>
        </template>
      </el-table-column>
      <el-table-column label="手机号" width="130">
        <template #default="{ row }">{{ row.phone || '—' }}</template>
      </el-table-column>
      <el-table-column label="职务" width="110">
        <template #default="{ row }">{{ row.position || '—' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status ? 'success' : 'danger'" size="small">
            {{ row.status ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="170">
        <template #default="{ row }">
          {{ new Date(row.created_at).toLocaleString() }}
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="userPage"
        :page-size="userSize"
        :total="userTotal"
        layout="total, prev, pager, next"
        @current-change="loadUsers"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import request from '../../utils/request';

const loading = ref(false);
const users = ref<any[]>([]);
const userPage = ref(1);
const userSize = 10;
const userTotal = ref(0);

const loadUsers = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/users', {
      params: { page: userPage.value, size: userSize }
    });
    users.value = res.items || [];
    userTotal.value = res.total || 0;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadUsers();
});
</script>

<style scoped>
.page-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
