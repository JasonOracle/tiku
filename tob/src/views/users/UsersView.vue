<!--
  * [变更日志]
  * 修改时间：2026-09-07 00:42:00
  * AI模型：Gemini 系列
  * 修改内容：[根据需求清理冗余的全站答题明细页标签，精简保留 C 端注册用户管理列表]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[用户管理解耦为 B端成员 / C端学员双 Tab；B端普管仅见直属下级（后端已隔离）；出题人无菜单入口]
  -->
<template>
  <div class="page-card">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="B端成员" name="staff">
        <el-table :data="members" v-loading="staffLoading" stripe style="width: 100%">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="username" label="用户名" min-width="140" />
          <el-table-column prop="name" label="姓名" width="110">
            <template #default="{ row }">{{ row.name || '—' }}</template>
          </el-table-column>
          <el-table-column label="角色" width="110">
            <template #default="{ row }">
              <el-tag size="small" :type="row.role === 'super_admin' ? 'danger' : (row.role === 'admin' ? 'warning' : 'primary')">
                {{ roleText(row.role) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="今日 AI 剩余额度" width="140">
            <template #default="{ row }">{{ row.daily_ai_quota ?? 0 }} 次</template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status ? 'success' : 'danger'" size="small">
                {{ row.status ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-bar">
          <el-pagination
            v-model:current-page="staffPage"
            :page-size="staffSize"
            :total="staffTotal"
            layout="total, prev, pager, next"
            @current-change="loadMembers"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane label="C端学员" name="students">
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
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import request from '../../utils/request';

const activeTab = ref('staff');

const loading = ref(false);
const users = ref<any[]>([]);
const userPage = ref(1);
const userSize = 10;
const userTotal = ref(0);

const staffLoading = ref(false);
const members = ref<any[]>([]);
const staffPage = ref(1);
const staffSize = 10;
const staffTotal = ref(0);

const roleText = (role: string) => {
  if (role === 'super_admin') return '超级管理员';
  if (role === 'admin') return '管理员';
  return '出题人';
};

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

const loadMembers = async () => {
  staffLoading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/members', {
      params: { page: staffPage.value, size: staffSize }
    });
    members.value = res.items || [];
    staffTotal.value = res.total || 0;
  } finally {
    staffLoading.value = false;
  }
};

const handleTabChange = (tab: string | number) => {
  if (tab === 'staff' && members.value.length === 0) loadMembers();
  if (tab === 'students' && users.value.length === 0) loadUsers();
};

onMounted(() => {
  loadMembers();
});
</script>

<style scoped>
.page-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
