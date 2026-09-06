<!--
 * [变更日志]
 * 修改时间：2026-09-06 20:40:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.2 新增成员与AI额度管理 (仅超管): 老师账号创建/改密/禁用/每日额度分配/余额即时补充]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <el-input v-model="keyword" placeholder="搜索用户名..." clearable style="width: 200px" @change="loadMembers" />
      <el-button type="primary" class="primary-btn" @click="createVisible = true">
        <el-icon><Plus /></el-icon> 新增老师账号
      </el-button>
    </div>

    <el-table :data="members" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="账号" min-width="130" />
      <el-table-column label="角色" width="110">
        <template #default="{ row }">
          <el-tag :type="row.role === 'super_admin' ? 'danger' : 'primary'" size="small">
            {{ row.role === 'super_admin' ? '超级管理员' : '老师' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status ? 'success' : 'info'" size="small">{{ row.status ? '正常' : '已禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="每日AI额度" width="130">
        <template #default="{ row }">
          <span style="font-weight: 700">{{ row.ai_quota_limit }}</span>
        </template>
      </el-table-column>
      <el-table-column label="今日余额" width="150">
        <template #default="{ row }">
          <el-progress :percentage="row.ai_quota_limit ? Math.min(100, Math.round(row.daily_ai_quota / row.ai_quota_limit * 100)) : 0"
                       :stroke-width="10" :color="row.daily_ai_quota > 0 ? '#0284c7' : '#ef4444'" />
          <span style="font-size: 12px; color: #64748b">{{ row.daily_ai_quota }} / {{ row.ai_quota_limit }} 次</span>
        </template>
      </el-table-column>
      <el-table-column prop="exam_count" label="名下试卷" width="95" align="center" />
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="openEdit(row)">编辑</el-button>
          <el-button type="success" text size="small" @click="openRefill(row)">补额度</el-button>
          <el-button :type="row.status ? 'warning' : 'success'" text size="small" @click="toggleStatus(row)">
            {{ row.status ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination v-model:current-page="page" :page-size="size" :total="total"
                     layout="total, prev, pager, next" @current-change="loadMembers" />
    </div>

    <!-- 新增 -->
    <el-dialog v-model="createVisible" title="新增老师账号" width="440px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="账号" required>
          <el-input v-model="createForm.username" placeholder="3-50位用户名" />
        </el-form-item>
        <el-form-item label="初始密码" required>
          <el-input v-model="createForm.password" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="每日AI额度">
          <el-input-number v-model="createForm.ai_quota_limit" :min="0" :max="10000" />
          <span style="font-size: 12px; color: #94a3b8; margin-left: 8px">AI出题/组卷/聊天每日可调用次数</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="doCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑 -->
    <el-dialog v-model="editVisible" :title="`编辑成员：${editing?.username}`" width="440px" destroy-on-close>
      <el-form label-width="100px">
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

const members = ref<any[]>([]);
const loading = ref(false);
const keyword = ref('');
const page = ref(1);
const size = 20;
const total = ref(0);
const saving = ref(false);

const createVisible = ref(false);
const createForm = reactive({ username: '', password: '', ai_quota_limit: 20 });

const editVisible = ref(false);
const editing = ref<any>(null);
const editForm = reactive({ password: '', ai_quota_limit: 0 });

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

const doCreate = async () => {
  saving.value = true;
  try {
    await request.post('/api/v1/admin/members', { ...createForm });
    ElMessage.success('创建成功');
    createVisible.value = false;
    createForm.username = '';
    createForm.password = '';
    loadMembers();
  } finally {
    saving.value = false;
  }
};

const openEdit = (row: any) => {
  editing.value = row;
  editForm.password = '';
  editForm.ai_quota_limit = row.ai_quota_limit;
  editVisible.value = true;
};

const doEdit = async () => {
  saving.value = true;
  try {
    const payload: any = { ai_quota_limit: editForm.ai_quota_limit };
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
