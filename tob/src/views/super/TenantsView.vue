<!--
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[1. 标题更名为「企业管理」，消除与成员管理概念混淆; 2. 表格操作列新增「成员」按钮，点击弹出 TenantMembersDrawer 原地视察成员与企业负责人，支持快捷切换视察]
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[重写为弹窗表单创建+列表编辑/封禁/解封+全字段展示]
-->
<template>
  <div class="tenants">
    <div class="head">
      <h2>企业管理</h2>
      <el-button type="primary" class="add-btn" @click="openCreateDialog">
        <el-icon><Plus /></el-icon> 新建企业
      </el-button>
    </div>

    <el-table :data="items" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="tenant_id" label="ID" width="70" />
      <el-table-column prop="tenant_name" label="企业名称" min-width="160" />
      <el-table-column prop="short_name" label="简称" width="120" />
      <el-table-column prop="industry" label="行业" width="110" />
      <el-table-column prop="scale" label="规模" width="90">
        <template #default="{ row }">
          <el-tag v-if="row.scale" size="small" type="info">{{ row.scale }}</el-tag>
          <span v-else class="muted">—</span>
        </template>
      </el-table-column>
      <el-table-column prop="contact_name" label="联系人" width="100" />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
            {{ row.status === 'active' ? '正常' : '已封禁' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="290" fixed="right">
        <template #default="scope">
          <el-button size="small" type="primary" plain @click="openMembersDrawer(scope.row)">成员</el-button>
          <el-button size="small" @click="enter(scope.row)">进入视察</el-button>
          <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-button v-if="scope.row.status === 'active'" size="small" type="danger"
                     @click="disable(scope.row)">封禁</el-button>
          <el-button v-else size="small" type="success"
                     @click="enable(scope.row)">解封</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑企业' : '新建企业'"
      width="560px"
      destroy-on-close
      class="tenant-dialog"
    >
      <el-form :model="form" label-width="90px" size="default">
        <el-form-item label="企业名称" required>
          <el-input v-model="form.name" placeholder="如：星辰教育科技" maxlength="100" />
        </el-form-item>
        <el-form-item label="企业简称">
          <el-input v-model="form.short_name" placeholder="如：星辰教育" maxlength="50" />
        </el-form-item>
        <el-form-item label="所属行业">
          <el-input v-model="form.industry" placeholder="如：教育/互联网/制造" maxlength="50" />
        </el-form-item>
        <el-form-item label="企业规模">
          <el-select v-model="form.scale" placeholder="选填" style="width: 100%">
            <el-option label="初创" value="初创" />
            <el-option label="中小" value="中小" />
            <el-option label="中型" value="中型" />
            <el-option label="大型" value="大型" />
            <el-option label="集团" value="集团" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact_name" placeholder="选填" maxlength="50" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" placeholder="选填" maxlength="20" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2"
                    placeholder="选填，最多 255 字" maxlength="255" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="save">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 成员视察抽屉 -->
    <TenantMembersDrawer
      :visible="membersDrawerVisible"
      :tenant-id="selectedTenantId"
      :tenant-name="selectedTenantName"
      @update:visible="membersDrawerVisible = $event"
      @enter-tenant="enterById"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import request from '../../utils/request';
import { useUserStore } from '../../store/user';
import TenantMembersDrawer from './components/TenantMembersDrawer.vue';

const userStore = useUserStore();
const items = ref<any[]>([]);
const loading = ref(false);
const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const saving = ref(false);

const membersDrawerVisible = ref(false);
const selectedTenantId = ref<number | null>(null);
const selectedTenantName = ref('');

const openMembersDrawer = (row: any) => {
  selectedTenantId.value = row.tenant_id;
  selectedTenantName.value = row.tenant_name;
  membersDrawerVisible.value = true;
};

const enterById = (tenantId: number) => {
  const t = items.value.find((x) => x.tenant_id === tenantId);
  enter(t || { tenant_id: tenantId, tenant_name: selectedTenantName.value });
};

const form = reactive({
  name: '',
  short_name: '',
  industry: '',
  scale: '' as string | undefined,
  contact_name: '',
  contact_phone: '',
  remark: ''
});

const load = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/super-admin/tenants');
    items.value = res?.items || res || [];
  } finally {
    loading.value = false;
  }
};

const openCreateDialog = () => {
  editingId.value = null;
  Object.assign(form, {
    name: '', short_name: '', industry: '', scale: undefined,
    contact_name: '', contact_phone: '', remark: ''
  });
  dialogVisible.value = true;
};

const openEditDialog = (row: any) => {
  editingId.value = row.tenant_id;
  Object.assign(form, {
    name: row.tenant_name || '',
    short_name: row.short_name || '',
    industry: row.industry || '',
    scale: row.scale || undefined,
    contact_name: row.contact_name || '',
    contact_phone: row.contact_phone || '',
    remark: row.remark || ''
  });
  dialogVisible.value = true;
};

const save = async () => {
  if (!form.name.trim()) {
    ElMessage.error('请填写企业名称');
    return;
  }
  saving.value = true;
  try {
    if (editingId.value !== null) {
      await request.put(`/api/v1/super-admin/tenants/${editingId.value}`, {
        name: form.name.trim(),
        short_name: form.short_name.trim() || null,
        industry: form.industry.trim() || null,
        scale: form.scale || null,
        contact_name: form.contact_name.trim() || null,
        contact_phone: form.contact_phone.trim() || null,
        remark: form.remark.trim() || null
      });
      ElMessage.success('企业已更新');
    } else {
      await request.post('/api/v1/super-admin/tenants', {
        name: form.name.trim(),
        short_name: form.short_name.trim() || undefined,
        industry: form.industry.trim() || undefined,
        scale: form.scale || undefined,
        contact_name: form.contact_name.trim() || undefined,
        contact_phone: form.contact_phone.trim() || undefined,
        remark: form.remark.trim() || undefined
      });
      ElMessage.success('企业创建成功');
    }
    dialogVisible.value = false;
    await load();
  } finally {
    saving.value = false;
  }
};

const disable = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定封禁企业「${row.tenant_name}」吗？封禁后该企业的成员将无法登录。`, '封禁确认', {
      type: 'warning', confirmButtonText: '确定封禁', cancelButtonText: '取消'
    });
  } catch (e) { return; }
  await request.post(`/api/v1/super-admin/tenants/${row.tenant_id}/disable`);
  ElMessage.success('已封禁');
  await load();
};

const enable = async (row: any) => {
  await request.put(`/api/v1/super-admin/tenants/${row.tenant_id}`, { status: 'active' });
  ElMessage.success('已解封');
  await load();
};

const enter = (row: any) => {
  userStore.setTenant(row.tenant_id);
  ElMessage.success(`已进入 ${row.tenant_name} 视察模式`);
  window.location.href = `${import.meta.env.BASE_URL}`;
};

onMounted(load);
</script>

<style scoped>
.tenants { padding: 20px; }
.head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.add-btn { font-weight: 600; }
.muted { color: #94a3b8; font-size: 12px; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 8px; }
</style>
