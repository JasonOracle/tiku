<!--
 * [变更日志]
 * 修改时间：2026-09-06 20:00:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.3: 用户列表新增 昵称/性别/手机号 列并补齐分页; 答题明细用户列显示 昵称(用户名) 优先口径]
-->
<template>
  <div class="page-card">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="注册 C端用户" name="users">
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
      </el-tab-pane>

      <el-tab-pane label="全站答题明细" name="records">
        <el-table :data="records" v-loading="loading" stripe style="width: 100%">
          <el-table-column prop="record_id" label="记录ID" width="90" />
          <el-table-column label="答题用户" min-width="160">
            <template #default="{ row }">
              <span style="font-weight: 700">{{ row.nickname || row.username }}</span>
              <span v-if="row.nickname" style="font-size: 12px; color: #94a3b8"> ({{ row.username }})</span>
            </template>
          </el-table-column>
          <el-table-column prop="exam_title" label="试卷名称" min-width="180" />
          <el-table-column label="做题结果" width="140">
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
        <div class="pagination-bar">
          <el-pagination
            v-model:current-page="recordPage"
            :page-size="recordSize"
            :total="recordTotal"
            layout="total, prev, pager, next"
            @current-change="loadRecords"
          />
        </div>
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
const userPage = ref(1);
const userSize = 10;
const userTotal = ref(0);
const recordPage = ref(1);
const recordSize = 10;
const recordTotal = ref(0);

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

const loadRecords = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/users/records', {
      params: { page: recordPage.value, size: recordSize }
    });
    records.value = res.items || [];
    recordTotal.value = res.total || 0;
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

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
