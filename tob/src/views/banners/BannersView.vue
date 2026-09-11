<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 底层
 * 修改内容：[1. 全面对齐现代 SaaS 无硬边框、首行专用淡蓝灰底色与立体弥散阴影设计规范; 2. 统一接入全局 list-layout.css 样式系统]
 -->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="filters">
        <span class="muted-gray-text">C端首页轮播（1张静显，超1张自动轮播）。启用上限 3 张。</span>
      </div>
      <div class="actions">
        <el-button type="primary" class="primary-create-btn" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增Banner
        </el-button>
      </div>
    </div>

    <!-- Banner 列表表格 (无硬边框，仅首行背景与微划线) -->
    <el-table
      :data="banners"
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
      <el-table-column prop="id" label="ID" width="80" align="center">
        <template #default="{ row }">
          <span class="col-id-text">{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="图片预览" width="190" align="center">
        <template #default="{ row }">
          <img :src="imgSrc(row.image_url)" class="thumb" alt="banner" />
        </template>
      </el-table-column>
      <el-table-column label="跳转链接" min-width="240">
        <template #default="{ row }">
          <div style="display: flex; align-items: center; gap: 8px">
            <span class="prop-pill" v-if="row.link_type === 'none'">不跳转</span>
            <span class="prop-pill" style="background: #fffbeb; color: #d97706" v-else-if="row.link_type === 'external'">外部链接</span>
            <span class="prop-pill" style="background: #ecfdf5; color: #047857" v-else>站内路径</span>
            <span v-if="row.link_type !== 'none'" class="muted-gray-text">{{ row.link_value }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="90" align="center">
        <template #default="{ row }">
          <span class="col-id-text">{{ row.sort_order }}</span>
        </template>
      </el-table-column>
      <el-table-column label="启用状态" width="130" align="center">
        <template #default="{ row }">
          <div
            class="status-dot-pill"
            :class="row.is_enabled ? 'published' : 'draft'"
            @click="toggleEnabled(row, !row.is_enabled)"
            title="点击切换启用状态"
          >
            <span class="dot"></span>
            <span class="text">{{ row.is_enabled ? '已启用' : '已停用' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" align="center" fixed="right">
        <template #default="{ row }">
          <div class="action-btn-group">
            <el-button type="primary" link class="action-link-btn" @click="openEdit(row)">编辑</el-button>
            <el-button type="danger" link class="action-link-btn red" @click="handleDelete(row.id)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-divider content-position="left"><strong>轮播设置</strong></el-divider>
    <div class="interval-row">
      <span>多张时自动滚动间隔</span>
      <el-input-number v-model="intervalSec" :min="2" :max="10" />
      <span>秒</span>
      <el-button type="primary" size="small" @click="saveInterval">保存</el-button>
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑Banner' : '新增Banner'" width="560px" destroy-on-close>
      <el-form :model="form" label-width="90px">
        <el-form-item label="图片" required>
          <el-upload
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFile"
            accept="image/*"
          >
            <img v-if="previewUrl" :src="previewUrl" class="preview" alt="预览" />
            <el-button v-else type="primary" plain>选择图片（建议16:9）</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="链接类型">
          <el-radio-group v-model="form.link_type">
            <el-radio-button label="none">不跳转</el-radio-button>
            <el-radio-button label="external">外部链接</el-radio-button>
            <el-radio-button label="internal">内部页面</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.link_type === 'external'" label="外链URL" required>
          <el-input v-model="form.link_value" placeholder="https://..." />
        </el-form-item>
        <el-form-item v-if="form.link_type === 'internal'" label="站内路径" required>
          <el-input v-model="form.link_value" placeholder="/quiz?exam_id=1 或 /profile" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveBanner">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import request from '../../utils/request';

const loading = ref(false);
const banners = ref<any[]>([]);
const intervalSec = ref(4);
const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const saving = ref(false);
const previewUrl = ref('');
const pendingFile = ref<File | null>(null);

const form = reactive({
  image_url: '',
  link_type: 'none',
  link_value: '',
  sort_order: 0,
  is_enabled: true
});

// 同源：/uploads 经 Nginx 代理与 vite proxy，禁止写死 8000
const imgSrc = (u: string) => u || '';

const loadBanners = async () => {
  loading.value = true;
  try {
    banners.value = (await request.get('/api/v1/admin/banners')) || [];
    const s: any = await request.get('/api/v1/admin/banners/settings');
    intervalSec.value = s.interval_seconds || 4;
  } finally {
    loading.value = false;
  }
};

const handleFile = (f: any) => {
  pendingFile.value = f.raw;
  previewUrl.value = URL.createObjectURL(f.raw);
};

const uploadIfNeeded = async () => {
  if (!pendingFile.value) return form.image_url;
  const fd = new FormData();
  fd.append('file', pendingFile.value);
  const res: any = await request.post('/api/v1/admin/upload', fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.url;
};

const openCreate = () => {
  editingId.value = null;
  const maxSort = banners.value.reduce((max, item) => Math.max(max, item.sort_order || 0), 0);
  Object.assign(form, { image_url: '', link_type: 'none', link_value: '', sort_order: maxSort + 1, is_enabled: true });
  previewUrl.value = '';
  pendingFile.value = null;
  dialogVisible.value = true;
};

const openEdit = (row: any) => {
  editingId.value = row.id;
  Object.assign(form, {
    image_url: row.image_url,
    link_type: row.link_type,
    link_value: row.link_value || '',
    sort_order: row.sort_order,
    is_enabled: row.is_enabled
  });
  previewUrl.value = imgSrc(row.image_url);
  pendingFile.value = null;
  dialogVisible.value = true;
};

const saveBanner = async () => {
  if (!pendingFile.value && !form.image_url) {
    ElMessage.error('请先选择图片');
    return;
  }
  saving.value = true;
  try {
    form.image_url = await uploadIfNeeded();
    const payload = { ...form, link_value: form.link_type === 'none' ? '' : form.link_value };
    if (editingId.value) {
      await request.put(`/api/v1/admin/banners/${editingId.value}`, payload);
      ElMessage.success('已保存');
    } else {
      await request.post('/api/v1/admin/banners', payload);
      ElMessage.success('已创建');
    }
    dialogVisible.value = false;
    loadBanners();
  } finally {
    saving.value = false;
  }
};

const toggleEnabled = async (row: any, v: boolean) => {
  try {
    await request.put(`/api/v1/admin/banners/${row.id}`, { is_enabled: v });
    loadBanners();
  } catch (e) {
    loadBanners();
  }
};

const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定删除该Banner吗？', '提示', { type: 'warning' }).then(async () => {
    await request.delete(`/api/v1/admin/banners/${id}`);
    ElMessage.success('删除成功');
    loadBanners();
  });
};

const saveInterval = async () => {
  await request.put('/api/v1/admin/banners/settings', { interval_seconds: intervalSec.value });
  ElMessage.success('轮播间隔已保存');
};

onMounted(loadBanners);
</script>

<style scoped>
.tip { color: #64748b; font-size: 13px; }
.thumb { width: 150px; height: 64px; object-fit: cover; border-radius: 8px; }
.link-val { margin-left: 8px; font-size: 12px; color: #64748b; }
.interval-row { display: flex; align-items: center; gap: 10px; color: #475569; font-size: 14px; }
.preview { width: 100%; max-height: 200px; object-fit: cover; border-radius: 8px; }
</style>
