<!--
 * [变更日志]
 * 修改时间：2026-09-07 01:05:00
 * AI模型：Gemini 系列
 * 修改内容：[重构为「用户管理」模块: 支持超级管理员、管理员、出题人三级角色管理；新增名字/真实姓名、手机号输入与展示]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <el-input v-model="keyword" placeholder="搜索账号或姓名..." clearable style="width: 220px" @change="loadMembers" />
      <el-button type="primary" class="primary-btn" @click="openCreate">
        <el-icon><Plus /></el-icon> 新增用户账号
      </el-button>
    </div>

    <el-table :data="members" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="账号" min-width="120" />
      <el-table-column label="姓名" min-width="120">
        <template #default="{ row }">
          <span style="font-weight: 700">{{ row.name || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="手机号" min-width="130">
        <template #default="{ row }">
          <span>{{ row.phone || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="角色" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.role === 'super_admin'" type="danger" size="small">超级管理员</el-tag>
          <el-tag v-else-if="row.role === 'admin'" type="warning" size="small">管理员</el-tag>
          <el-tag v-else type="primary" size="small">出题人</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status ? 'success' : 'info'" size="small">{{ row.status ? '正常' : '已禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="每日AI额度" width="120">
        <template #default="{ row }">
          <span style="font-weight: 700">{{ row.ai_quota_limit }}</span>
        </template>
      </el-table-column>
      <el-table-column label="今日余额" width="140">
        <template #default="{ row }">
          <el-progress :percentage="row.ai_quota_limit ? Math.min(100, Math.round(row.daily_ai_quota / row.ai_quota_limit * 100)) : 0"
                       :stroke-width="10" :color="row.daily_ai_quota > 0 ? '#0284c7' : '#ef4444'" />
          <span style="font-size: 12px; color: #64748b">{{ row.daily_ai_quota }} / {{ row.ai_quota_limit }} 次</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="openEdit(row)">编辑</el-button>
          <el-button type="success" text size="small" @click="openRefill(row)">补额度</el-button>
          <el-button :type="row.status ? 'warning' : 'success'" text size="small" @click="toggleStatus(row)" :disabled="row.role === 'super_admin'">
            {{ row.status ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination v-model:current-page="page" :page-size="size" :total="total"
                     layout="total, prev, pager, next" @current-change="loadMembers" />
    </div>

    <!-- 新增弹窗 -->
    <el-dialog v-model="createVisible" title="新增用户账号" width="460px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="账号" required>
          <el-input v-model="createForm.username" placeholder="3-50位用户名" />
        </el-form-item>
        <el-form-item label="真实姓名" required>
          <el-input v-model="createForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号" required>
          <el-input v-model="createForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="分配角色" required>
          <el-select v-model="createForm.role" style="width: 100%">
            <el-option v-if="userStore.isSuper()" label="管理员" value="admin" />
            <el-option label="出题人" value="teacher" />
          </el-select>
        </el-form-item>
        <el-form-item label="初始密码" required>
          <el-input v-model="createForm.password" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="每日AI额度">
          <el-input-number v-model="createForm.ai_quota_limit" :min="0" :max="10000" />
          <span style="font-size: 12px; color: #94a3b8; margin-left: 8px">AI出题/组卷/聊天每日额度</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="doCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editVisible" :title="`编辑账号：${editing?.username}`" width="460px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="真实姓名">
          <el-input v-model="editForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item v-if="userStore.isSuper() && editing?.role !== 'super_admin'" label="分配角色">
          <el-select v-model="editForm.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="出题人" value="teacher" />
          </el-select>
        </el-form-item>
        <el-form-item label="重置密码">
          <el-input v-model="editForm.password" type="password" show-password placeholder="留空则不修改" />
        </el-form-item>
        <el-form-item label="每日AI额度">
          <el-input-number v-model="editForm.ai_quota_limit" :min="0" :max="10000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="doEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 补额度 -->
    <el-dialog v-model="refillVisible" :title="`为 ${refilling?.username} 补充今日 AI 余额`" width="380px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="补充次数">
          <el-input-number v-model="refillAmount" :min="1" :max="10000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="refillVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="doRefill">确认补充</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import request from '../../utils/request';
import { useUserStore } from '../../store/user';

const userStore = useUserStore();
const members = ref<any[]>([]);
const loading = ref(false);
const keyword = ref('');
const page = ref(1);
const size = 20;
const total = ref(0);
const saving = ref(false);

const createVisible = ref(false);
const createForm = reactive({ username: '', name: '', phone: '', role: 'teacher', password: '', ai_quota_limit: 20 });

const editVisible = ref(false);
const editing = ref<any>(null);
const editForm = reactive({ name: '', phone: '', role: 'teacher', password: '', ai_quota_limit: 0 });

const refillVisible = ref(false);
const refilling = ref<any>(null);
const refillAmount = ref(10);

const loadMembers = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/members', {
      params: { keyword: keyword.value || undefined, page: page.value, size }
    });
    members.value = res.items || [];
    total.value = res.total || 0;
  } finally {
    loading.value = false;
  }
};

const openCreate = () => {
  createForm.username = '';
  createForm.name = '';
  createForm.phone = '';
  createForm.role = userStore.isSuper() ? 'admin' : 'teacher';
  createForm.password = '';
  createForm.ai_quota_limit = 20;
  createVisible.value = true;
};

const doCreate = async () => {
  if (!createForm.username.trim() || !createForm.password) {
    ElMessage.error('请填写账号和密码');
    return;
  }
  saving.value = true;
  try {
    await request.post('/api/v1/admin/members', { ...createForm });
    ElMessage.success('创建成功');
    createVisible.value = false;
    loadMembers();
  } finally {
    saving.value = false;
  }
};

const openEdit = (row: any) => {
  editing.value = row;
  editForm.name = row.name || '';
  editForm.phone = row.phone || '';
  editForm.role = row.role || 'teacher';
  editForm.password = '';
  editForm.ai_quota_limit = row.ai_quota_limit;
  editVisible.value = true;
};

const doEdit = async () => {
  saving.value = true;
  try {
    const payload: any = {
      name: editForm.name,
      phone: editForm.phone,
      role: editForm.role,
      ai_quota_limit: editForm.ai_quota_limit
    };
    if (editForm.password) payload.password = editForm.password;
    await request.put(`/api/v1/admin/members/${editing.value.id}`, payload);
    ElMessage.success('已保存');
    editVisible.value = false;
    loadMembers();
  } finally {
    saving.value = false;
  }
};

const openRefill = (row: any) => {
  refilling.value = row;
  refillAmount.value = 10;
  refillVisible.value = true;
};

const doRefill = async () => {
  saving.value = true;
  try {
    await request.post(`/api/v1/admin/members/${refilling.value.id}/refill`, { amount: refillAmount.value });
    ElMessage.success(`已为 ${refilling.value.username} 补充 ${refillAmount.value} 次`);
    refillVisible.value = false;
    loadMembers();
  } finally {
    saving.value = false;
  }
};

const toggleStatus = async (row: any) => {
  await request.put(`/api/v1/admin/members/${row.id}`, { status: !row.status });
  ElMessage.success(row.status ? '已禁用' : '已启用');
  loadMembers();
};

onMounted(loadMembers);
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

.primary-btn {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  border: none;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
