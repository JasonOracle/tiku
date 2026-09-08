<!--
  * [变更日志]
  * 修改时间：2026-09-08
  * AI模型：Muse Spark
  * 修改内容：[v1.3 任务3: RAG 私有文档库页 (上传切片 + 进度轮询 + 列表删除 + 检索验证)]
  -->
<template>
  <div class="page-card">
    <div class="rag-header">
      <div>
        <div class="rag-title">私有文档库</div>
        <div class="rag-sub">上传 PDF / Word / 文本资料，切片向量化后可在 AI 出题时勾选作为依据并自动溯源</div>
      </div>
      <el-upload
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        accept=".txt,.md,.pdf,.docx"
        :on-change="handleUpload"
      >
        <el-button type="primary" :loading="uploading">上传文档</el-button>
      </el-upload>
    </div>

    <el-table :data="docs" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
      <el-table-column label="切片进度" min-width="200">
        <template #default="{ row }">
          <el-tag v-if="row.status === 'done'" type="success" size="small">已完成 {{ row.done_chunks }}/{{ row.total_chunks }}</el-tag>
          <el-tag v-else-if="row.status === 'failed'" type="danger" size="small" effect="dark">失败：{{ row.error }}</el-tag>
          <span v-else style="font-size: 12px; color: #64748b">
            {{ row.status === 'chunking' ? '切片中' : '向量化中' }} {{ row.done_chunks }}/{{ row.total_chunks }}
          </span>
          <el-progress
            v-if="row.status !== 'done' && row.status !== 'failed'"
            :percentage="row.total_chunks ? Math.round((row.done_chunks * 100) / row.total_chunks) : 0"
            :show-text="false"
            stroke-width="6"
            style="margin-top: 4px"
          />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="上传时间" width="170" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button type="danger" text size="small" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-divider content-position="left"><strong>检索验证</strong></el-divider>
    <div class="search-row">
      <el-input v-model="query" placeholder="输入问题，验证切片召回效果" clearable style="flex: 1" @keyup.enter="doSearch" />
      <el-button type="primary" :loading="searching" @click="doSearch">检索</el-button>
    </div>
    <div v-for="h in hits" :key="h.id" class="hit-card">
      <div class="hit-head">
        <el-tag size="small" type="info">{{ h.filename }}</el-tag>
        <span class="hit-score">相似度 {{ h.score }}</span>
      </div>
      <div class="hit-text">{{ h.text }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '../../utils/request';

const loading = ref(false);
const uploading = ref(false);
const searching = ref(false);
const docs = ref<any[]>([]);
const query = ref('');
const hits = ref<any[]>([]);
let pollTimer: number | undefined;

const loadDocs = async (silent = false) => {
  if (!silent) loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/rag/documents');
    docs.value = res.items || [];
    // 仍有处理中的文档则继续轮询进度
    const busy = docs.value.some((d: any) => d.status === 'chunking' || d.status === 'embedding');
    if (busy && pollTimer === undefined) {
      pollTimer = window.setInterval(() => loadDocs(true), 2000);
    } else if (!busy && pollTimer !== undefined) {
      window.clearInterval(pollTimer);
      pollTimer = undefined;
    }
  } finally {
    if (!silent) loading.value = false;
  }
};

const handleUpload = async (file: any) => {
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件超过 10MB 上限');
    return;
  }
  const fd = new FormData();
  fd.append('file', file.raw);
  uploading.value = true;
  try {
    // 与题库 Excel 导入 / Banner 上传同一范式：request 相对路径 + multipart（同源代理，禁止写死 8000）
    await request.post('/api/v1/admin/rag/documents', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    ElMessage.success('已上传并开始切片');
    loadDocs();
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    uploading.value = false;
  }
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除该文档及其全部切片吗？', '提示', { type: 'warning' });
  } catch (e) {
    return;
  }
  await request.delete(`/api/v1/admin/rag/documents/${id}`);
  ElMessage.success('已删除');
  loadDocs();
};

const doSearch = async () => {
  if (!query.value.trim()) {
    ElMessage.error('请先输入检索问题');
    return;
  }
  searching.value = true;
  try {
    const res: any = await request.post('/api/v1/admin/rag/search', { query: query.value, limit: 5 });
    hits.value = res.items || [];
    if (!hits.value.length) ElMessage.info('未召回相关切片');
  } finally {
    searching.value = false;
  }
};

onMounted(loadDocs);

onUnmounted(() => {
  if (pollTimer !== undefined) window.clearInterval(pollTimer);
});
</script>

<style scoped>
.page-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.rag-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rag-title {
  font-size: 17px;
  font-weight: 800;
  color: #0f172a;
}

.rag-sub {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.search-row {
  display: flex;
  gap: 12px;
  margin: 12px 0 16px;
}

.hit-card {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 10px;
  background: #f8fafc;
}

.hit-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.hit-score {
  font-size: 12px;
  color: #0284c7;
  font-weight: 600;
}

.hit-text {
  font-size: 13px;
  color: #334155;
  line-height: 1.7;
  white-space: pre-wrap;
}
</style>
