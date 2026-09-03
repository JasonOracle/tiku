<!--
 * [变更日志]
 * 修改时间：2026-09-03
 * AI模型：Gemini 底层
 * 修改内容：[1. 实现 B 端注册用户列表与全站答题明细面板]
-->
<template>
  <div class="page-card">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="注册 C端用户" name="users">
        <el-table :data="users" v-loading="loading" stripe style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status ? 'success' : 'danger'">
                {{ row.status ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="注册时间">
            <template #default="{ row }">
              {{ new Date(row.created_at).toLocaleString() }}
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="全站答题明细" name="records">
        <el-table :data="records" v-loading="loading" stripe style="width: 100%">
          <el-table-column prop="record_id" label="记录ID" width="90" />
          <el-table-column prop="username" label="答题用户" width="140" />
          <el-table-column prop="exam_title" label="试卷名称" min-width="180" />
          <el-table-column label="做题结果" width="130">
            <template #default="{ row }">
              <el-tag :type="row.passed ? 'success' : 'danger'">
                {{ row.score }} 分 ({{ row.passed ? '及格' : '不及格' }})
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="time_spent" label="做题用时" width="110">
            <template #default="{ row }">
              {{ Math.floor(row.time_spent / 60) }}分{{ row.time_spent % 60 }}秒
            </template>
          </el-table-column>
          <el-table-column prop="submit_time" label="提交时间">
            <template #default="{ row }">
              {{ row.submit_time ? new Date(row.submit_time).toLocaleString() : '未交卷' }}
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import request from '../../utils/request';

const activeTab = ref('users');
const loading = ref(false);
const users = ref<any[]>([]);
const records = ref<any[]>([]);

const loadUsers = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/users');
    users.value = res.items || [];
  } finally {
    loading.value = false;
  }
};

const loadRecords = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/users/records');
    records.value = res.items || [];
  } finally {
    loading.value = false;
  }
};

const handleTabChange = (name: any) => {
  if (name === 'users') loadUsers();
  else loadRecords();
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
</style>
