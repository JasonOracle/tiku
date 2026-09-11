<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[彻底根除图2文字省略号截断Bug：优化单元格padding为紧凑型12px 10px，将性别、角色、状态等定宽列转为 min-width 弹性自适应，确保胶囊与文本完整舒展不压缩]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[全面接入全局 SaaS 列表规范 list-layout.css：1. 消除页面和表格硬边框，改用高定立体弥散阴影；2. 表格仅首行赋予淡蓝灰底色，列宽合理扩充杜绝字形折行；3. 升级角色标签与状态物理圆点胶囊；4. 操作列采用无边框轻质链接按键]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[员工编辑画像打通: 1. 列表表格新增性别、职业、年龄展示列，直观呈现补充信息；2. openDialog 稳健兼容回显画像字段]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗重写：手机号静默录入+租户成员列表，旧账号/额度体系已删除]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="filters">
        <el-input
          v-model="keyword"
          placeholder="搜索手机号 / 姓名 / 昵称..."
          clearable
          class="custom-search-input"
          style="width: 280px"
          @change="doSearch"
          @keyup.enter="doSearch"
        >
          <template #prefix>
            <el-icon class="search-prefix-icon"><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="actions">
        <el-button type="primary" class="primary-create-btn" @click="openDialog">
          <el-icon><Plus /></el-icon> 录入成员
        </el-button>
      </div>
    </div>

    <!-- 成员列表表格 (无硬边框，仅首行背景与微划线) -->
    <el-table
      :data="members"
      v-loading="loading"
      class="saas-modern-table"
      style="width: 100%"
      :header-cell-style="{
        backgroundColor: '#f1f5f9',
        color: '#475569',
        fontWeight: '700',
        fontSize: '13px',
        padding: '12px 10px',
        borderBottom: '1px solid #e2e8f0',
        whiteSpace: 'nowrap'
      }"
      :cell-style="{
        padding: '14px 10px',
        borderBottom: '1px solid #f1f5f9'
      }"
    >
      <el-table-column prop="user_id" label="ID" width="80" align="center">
        <template #default="{ row }">
          <span class="col-id-text">{{ row.user_id }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机号" min-width="140">
        <template #default="{ row }">
          <span style="font-weight: 600; color: #1e293b">{{ row.phone }}</span>
        </template>
      </el-table-column>
      <el-table-column label="姓名" min-width="110">
        <template #default="{ row }">
          <span class="cell-main-title">{{ row.display_name || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="昵称" min-width="110">
        <template #default="{ row }">
          <span class="muted-gray-text">{{ row.nickname || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="性别" min-width="85" align="center">
        <template #default="{ row }">
          <span v-if="row.gender === 'male'" style="color: #2563eb; font-weight: 600">男</span>
          <span v-else-if="row.gender === 'female'" style="color: #db2777; font-weight: 600">女</span>
          <span v-else-if="row.gender === 'secret'" class="muted-gray-text">保密</span>
          <span v-else class="muted-gray-text">—</span>
        </template>
      </el-table-column>
      <el-table-column prop="age" label="年龄" min-width="85" align="center">
        <template #default="{ row }">
          <span>{{ row.age ? `${row.age} 岁` : '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="occupation" label="职业" min-width="120" align="center">
        <template #default="{ row }">
          <span class="prop-pill">{{ row.occupation || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="角色" min-width="105" align="center">
        <template #default="{ row }">
          <span v-if="row.role === 'owner'" class="prop-pill" style="background: #fef2f2; color: #dc2626">所有者</span>
          <span v-else-if="row.role === 'admin'" class="prop-pill" style="background: #fffbeb; color: #d97706">管理员</span>
          <span v-else class="prop-pill" style="background: #eff6ff; color: #2563eb">成员</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" min-width="120" align="center">
        <template #default="{ row }">
          <div class="status-dot-pill" :class="row.status === 'active' ? 'published' : 'draft'">
            <span class="dot"></span>
            <span class="text">{{ row.status === 'active' ? '正常' : '禁用' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <div class="action-btn-group">
            <el-button type="primary" link class="action-link-btn" @click="openDialog(row)">编辑</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination v-model:current-page="page" :page-size="size" :total="total"
                     layout="total, prev, pager, next" @current-change="doSearch" />
    </div>

    <!-- 录入/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑成员' : '录入成员'"
      width="560px"
      destroy-on-close
      class="member-dialog"
    >
      <el-form :model="form" label-width="88px" size="default">
        <el-form-item label="手机号" required>
          <el-input v-model="form.phone" placeholder="11 位手机号（录入必填）" maxlength="11" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.display_name" placeholder="成员展示名" maxlength="50" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="成员" value="member" />
            <el-option label="管理员" value="admin" />
            <el-option label="所有者" value="owner" />
          </el-select>
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="选填" maxlength="50" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="选填" maxlength="100" />
        </el-form-item>
        <el-form-item label="职业">
          <el-input v-model="form.occupation" placeholder="选填" maxlength="100" />
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="form.age" :min="1" :max="150" placeholder="选填" style="width: 120px" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender" style="width: 100%">
            <el-option label="未设置" value="" />
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
            <el-option label="保密" value="secret" />
          </el-select>
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.bio" type="textarea" :rows="3"
                    placeholder="选填，个人简介" maxlength="500" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="save">保存</el-button>
        </div>
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
const page = ref(1);
const size = 20;
const total = ref(0);
const keyword = ref('');
const saving = ref(false);
const dialogVisible = ref(false);
const editingId = ref<number | null>(null);

const form = reactive({
  phone: '',
  display_name: '',
  role: 'member' as string,
  nickname: '',
  email: '',
  occupation: '',
  age: undefined as number | undefined,
  gender: '' as string,
  bio: '',
  status: 'active' as string
});

const doSearch = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/members', {
      params: { page: page.value, size, keyword: keyword.value }
    });
    members.value = res.items || [];
    total.value = res.total || 0;
  } finally {
    loading.value = false;
  }
};

const openDialog = (row?: any) => {
  if (row) {
    editingId.value = row.user_id;
    Object.assign(form, {
      phone: row.phone || '',
      display_name: row.display_name || '',
      role: row.role || 'member',
      nickname: row.nickname || '',
      email: row.email || '',
      occupation: row.occupation || '',
      age: row.age,
      gender: row.gender || '',
      bio: row.bio || '',
      status: row.status || 'active'
    });
  } else {
    editingId.value = null;
    Object.assign(form, {
      phone: '', display_name: '', role: 'member',
      nickname: '', email: '', occupation: '',
      age: undefined, gender: '', bio: '', status: 'active'
    });
  }
  dialogVisible.value = true;
};

const save = async () => {
  if (!editingId.value) {
    // 新建
    if (!/^1[3-9]\d{9}$/.test(form.phone.trim())) {
      ElMessage.error('请输入正确的 11 位手机号');
      return;
    }
    saving.value = true;
    try {
      await request.post('/api/v1/admin/members', {
        phone: form.phone.trim(),
        name: form.display_name.trim(),
        role: form.role,
        nickname: form.nickname.trim() || undefined,
        email: form.email.trim() || undefined,
        occupation: form.occupation.trim() || undefined,
        age: form.age || undefined,
        gender: form.gender || undefined,
        bio: form.bio.trim() || undefined
      });
      ElMessage.success('成员添加成功（默认密码 123456）');
      dialogVisible.value = false;
      doSearch();
    } finally {
      saving.value = false;
    }
  } else {
    // 编辑
    saving.value = true;
    try {
      await request.put(`/api/v1/admin/members/${editingId.value}`, {
        display_name: form.display_name.trim() || null,
        role: form.role,
        status: form.status,
        nickname: form.nickname.trim() || null,
        email: form.email.trim() || null,
        occupation: form.occupation.trim() || null,
        age: form.age || null,
        gender: form.gender || null,
        bio: form.bio.trim() || null
      });
      ElMessage.success('成员信息已更新');
      dialogVisible.value = false;
      doSearch();
    } finally {
      saving.value = false;
    }
  }
};

onMounted(doSearch);
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
  gap: 12px;
  flex-wrap: wrap;
}

.add-btn { font-weight: 600; }

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
