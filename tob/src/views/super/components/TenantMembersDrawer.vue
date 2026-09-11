<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 底层
 * 修改内容：[表格对齐现代 SaaS 统一规范，接入 saas-modern-table 统一浅蓝灰表头首行与去边框细节]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[新建企业成员视察抽屉组件：超管上帝视角直查企业成员，所有者卡片置顶，支持手机号/姓名过滤，附带一键切换视察快捷入口]
 -->
<template>
  <el-drawer
    :model-value="visible"
    :title="`企业成员视察 — ${tenantName || ''}`"
    size="720px"
    destroy-on-close
    @close="handleClose"
  >
    <div v-loading="loading" class="drawer-container">
      <!-- 顶部所有者概览卡片 -->
      <div v-if="ownerUser" class="owner-card">
        <div class="owner-icon">
          <svg viewBox="0 0 1024 1024" width="28" height="28" style="fill: #ea580c;">
            <path d="M512 64l112 256 272 32-200 184 56 272-240-136-240 136 56-272-200-184 272-32z" />
          </svg>
        </div>
        <div class="owner-info">
          <div class="owner-tag-row">
            <span class="owner-name">{{ ownerUser.display_name || '企业所有者' }}</span>
            <el-tag size="small" type="danger" effect="dark">企业所有者 (Owner)</el-tag>
            <el-tag :type="ownerUser.status === 'active' ? 'success' : 'info'" size="small">
              {{ ownerUser.status === 'active' ? '账号正常' : '已禁用' }}
            </el-tag>
          </div>
          <div class="owner-meta">
            <span>手机号：<strong>{{ ownerUser.phone }}</strong></span>
            <span v-if="ownerUser.email" style="margin-left: 16px;">邮箱：{{ ownerUser.email }}</span>
            <span v-if="ownerUser.created_at" style="margin-left: 16px; color: #94a3b8;">加入时间：{{ ownerUser.created_at }}</span>
          </div>
        </div>
        <el-button type="primary" plain size="small" class="enter-btn" @click="handleEnterTenant">
          进入该企业视察
        </el-button>
      </div>

      <!-- 搜索过滤栏 -->
      <div class="filter-row">
        <el-input
          v-model="keyword"
          placeholder="搜索姓名 / 手机号"
          clearable
          style="width: 240px"
          @keyup.enter="loadMembers"
          @clear="loadMembers"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" plain size="small" @click="loadMembers">
          <el-icon><Search /></el-icon> 查询
        </el-button>
        <span class="total-text">共 {{ total }} 名成员</span>
      </div>

      <!-- 成员列表表格 (无硬边框，仅首行背景与微划线) -->
      <el-table
        :data="members"
        class="saas-modern-table"
        size="small"
        style="width: 100%; margin-top: 12px;"
        :header-cell-style="{
          backgroundColor: '#f1f5f9',
          color: '#475569',
          fontWeight: '700',
          fontSize: '12px',
          padding: '10px 12px',
          borderBottom: '1px solid #e2e8f0',
          whiteSpace: 'nowrap'
        }"
        :cell-style="{
          padding: '12px 12px',
          borderBottom: '1px solid #f1f5f9'
        }"
      >
        <el-table-column prop="user_id" label="UID" width="65" />
        <el-table-column prop="display_name" label="姓名" min-width="110">
          <template #default="{ row }">
            <span style="font-weight: 600; color: #0f172a">{{ row.display_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="125" />
        <el-table-column label="角色" width="95">
          <template #default="{ row }">
            <el-tag v-if="row.role === 'owner'" type="danger" size="small">所有者</el-tag>
            <el-tag v-else-if="row.role === 'admin'" type="warning" size="small">管理员</el-tag>
            <el-tag v-else type="info" size="small">普通成员</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="加入时间" min-width="150">
          <template #default="{ row }">
            <span style="font-size: 12px; color: #64748b">{{ row.created_at || '—' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total === 0 && !loading" style="margin-top: 40px;">
        <el-empty description="该企业暂无成员记录" />
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Search } from '@element-plus/icons-vue';
import request from '../../../utils/request';

const props = defineProps<{
  visible: boolean;
  tenantId: number | null;
  tenantName: string;
}>();

const emit = defineEmits<{
  (e: 'update:visible', val: boolean): void;
  (e: 'enter-tenant', tenantId: number): void;
}>();

const loading = ref(false);
const members = ref<any[]>([]);
const total = ref(0);
const keyword = ref('');

const ownerUser = computed(() =>
  members.value.find((m) => m.role === 'owner') || null
);

const loadMembers = async () => {
  if (!props.tenantId) return;
  loading.value = true;
  try {
    const res: any = await request.get(`/api/v1/super-admin/tenants/${props.tenantId}/members`, {
      params: { keyword: keyword.value.trim(), size: 100 }
    });
    members.value = res?.items || res?.data?.items || [];
    total.value = res?.total || res?.data?.total || members.value.length;
  } catch (e) {
    members.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

watch(
  () => props.visible,
  (val) => {
    if (val && props.tenantId) {
      keyword.value = '';
      loadMembers();
    } else {
      members.value = [];
      total.value = 0;
    }
  }
);

const handleClose = () => {
  emit('update:visible', false);
};

const handleEnterTenant = () => {
  if (props.tenantId) {
    emit('enter-tenant', props.tenantId);
  }
};
</script>

<style scoped>
.drawer-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.owner-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 16px;
}

.owner-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: #ffedd5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.owner-info {
  flex: 1;
}

.owner-tag-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.owner-name {
  font-size: 15px;
  font-weight: 700;
  color: #9a3412;
}

.owner-meta {
  font-size: 12px;
  color: #7c2d12;
}

.enter-btn {
  border-color: #f97316 !important;
  color: #ea580c !important;
}
.enter-btn:hover {
  background: #ea580c !important;
  color: #ffffff !important;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.total-text {
  margin-left: auto;
  font-size: 13px;
  color: #64748b;
}
</style>
