<!--
 * [变更日志]
 * 修改时间：2026-09-04
 * AI模型：Gemini 底层
 * 修改内容：[1. 修正 Banner 新建时的 sort_order 默认逻辑为已存在最大排序 + 1]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="filters">
        <span class="tip">C端首页轮播（1张静显，超1张自动轮播）。启用上限 3 张。</span>
      </div>
      <div class="actions">
        <el-button type="primary" class="primary-btn" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增Banner
        </el-button>
      </div>
    </div>

    <el-table :data="banners" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="图片" width="170">
        <template #default="{ row }">
          <img :src="imgSrc(row.image_url)" class="thumb" alt="banner" />
        </template>
      </el-table-column>
      <el-table-column label="链接" min-width="180">
        <template #default="{ row }">
          <el-tag v-if="row.link_type === 'none'" type="info" size="small">不跳转</el-tag>
          <el-tag v-else-if="row.link_type === 'external'" type="warning" size="small">外链</el-tag>
          <el-tag v-else type="success" size="small">站内</el-tag>
          <span v-if="row.link_type !== 'none'" class="link-val">{{ row.link_value }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column label="启用" width="110">
        <template #default="{ row }">
          <el-switch :model-value="row.is_enabled" @change="(v: boolean) => toggleEnabled(row, v)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="170" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="openEdit(row)">编辑</el-button>
          <el-button type="danger" text size="small" @click="handleDelete(row.id)">删除</el-button>
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
.page-card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); }
.filter-bar { display: flex; justify-content: space-between; align-items: center; }
.tip { color: #64748b; font-size: 13px; }
.primary-btn { background: linear-gradient(135deg, #0284c7, #0369a1); border: none; }
.thumb { width: 150px; height: 64px; object-fit: cover; border-radius: 8px; }
.link-val { margin-left: 8px; font-size: 12px; color: #64748b; }
.interval-row { display: flex; align-items: center; gap: 10px; color: #475569; font-size: 14px; }
.preview { width: 100%; max-height: 200px; object-fit: cover; border-radius: 8px; }
</style>
