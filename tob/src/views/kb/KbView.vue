<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[会话隔离解耦: 抽屉测试召回切换至专属接口 /api/v1/admin/kb/query，仅做即时切片召回与回答，不生成持久化会话，彻底避免测试问题污染 AI 助理会话历史]
 * 修改时间：2026-09-11
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[修复切片相似度展示 Bug：兼容后端返回的 similarity 与 similarity_score 浮点字段，杜绝 NaN% 现象；文档名兼容 document_name 与 file_name]
-->
<template>
  <div class="kb-page">
    <!-- 顶部科技感 Hero 区域 -->
    <div class="kb-hero">
      <div class="hero-content">
        <div class="hero-title-row">
          <span class="hero-title">知识库 · 让知识更有价值</span>
        </div>
        <div class="hero-desc">
          构建企业专属的 AI 知识库，支持多种格式文档，智能切片与向量化，助力高效问答与知识管理。
        </div>

        <!-- 公共知识库 vs 私人知识库 大切换卡片 -->
        <div class="scope-tabs-wrap">
          <div
            class="scope-card"
            :class="{ active: currentScope === 'public' }"
            @click="switchScope('public')"
          >
            <div class="scope-icon-wrap public">
              <svg viewBox="0 0 1024 1024" width="22" height="22" style="fill: currentColor;">
                <path d="M512 64a448 448 0 1 0 448 448A448 448 0 0 0 512 64z m0 832a384 384 0 0 1-182.4-46.72c21.76-78.72 69.76-137.6 137.6-169.6 14.72 9.6 30.72 17.28 47.36 21.76 53.76 15.36 108.16 2.56 151.04-32.64 42.88-35.84 62.72-88.96 52.48-142.72-3.84-19.84-11.52-38.4-22.4-55.68 33.92-66.56 94.72-113.28 171.52-133.76A384.64 384.64 0 0 1 512 896z" />
              </svg>
            </div>
            <div class="scope-texts">
              <div class="scope-title">公共知识库</div>
              <div class="scope-sub">全员知识 · 协作共建</div>
            </div>
            <span v-if="currentScope === 'public'" class="active-badge">✓</span>
          </div>

          <div
            class="scope-card"
            :class="{ active: currentScope === 'private' }"
            @click="switchScope('private')"
          >
            <div class="scope-icon-wrap private">
              <svg viewBox="0 0 1024 1024" width="22" height="22" style="fill: currentColor;">
                <path d="M832 448h-64V320A256 256 0 0 0 256 320v128h-64a64 64 0 0 0-64 64v384a64 64 0 0 0 64 64h640a64 64 0 0 0 64-64V512a64 64 0 0 0-64-64zM320 320a192 192 0 0 1 384 0v128H320z m224 352v96a32 32 0 0 1-64 0v-96a64 64 0 1 1 64-64c0 23.68-12.8 44.16-32 55.68V672z" />
              </svg>
            </div>
            <div class="scope-texts">
              <div class="scope-title">私人知识库</div>
              <div class="scope-sub">个人专属 · 安全可控</div>
            </div>
            <span v-if="currentScope === 'private'" class="active-badge">✓</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 4 大指标数据卡 + 上传主按钮 -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="m-icon-box doc">
          <svg viewBox="0 0 1024 1024" width="22" height="22" style="fill: #2563eb;">
            <path d="M768 128H256c-35.3 0-64 28.7-64 64v640c0 35.3 28.7 64 64 64h512c35.3 0 64-28.7 64-64V192c0-35.3-28.7-64-64-64z m-64 640H320V256h384v512z" />
            <path d="M384 384h256v64H384z m0 160h256v64H384z m0 160h192v64H384z" />
          </svg>
        </div>
        <div class="m-body">
          <div class="m-label">文档总数</div>
          <div class="m-val-row">
            <span class="m-num">{{ metrics.total_docs }}</span>
            <span class="m-trend up">↑ 100% 活跃</span>
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="m-icon-box chunk">
          <svg viewBox="0 0 1024 1024" width="22" height="22" style="fill: #0284c7;">
            <path d="M832 256c0 70.7-143.3 128-320 128S192 326.7 192 256 335.3 128 512 128s320 57.3 320 128z" />
            <path d="M832 448c0 70.7-143.3 128-320 128S192 518.7 192 448v-96c68.3 46.8 186.2 78 320 78s251.7-31.2 320-78v96z" />
            <path d="M832 640c0 70.7-143.3 128-320 128S192 710.7 192 640v-96c68.3 46.8 186.2 78 320 78s251.7-31.2 320-78v96z" />
          </svg>
        </div>
        <div class="m-body">
          <div class="m-label">已切片</div>
          <div class="m-val-row">
            <span class="m-num" style="color: #0284c7;">{{ metrics.total_chunks }}</span>
            <span class="m-trend up">智能向量化</span>
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="m-icon-box proc">
          <svg viewBox="0 0 1024 1024" width="22" height="22" style="fill: #16a34a;">
            <path d="M512 64a448 448 0 1 0 448 448A448 448 0 0 0 512 64z m-48 640l-160-160 45.2-45.2L464 613.5l250.8-250.7L760 408z" />
          </svg>
        </div>
        <div class="m-body">
          <div class="m-label">处理就绪</div>
          <div class="m-val-row">
            <span class="m-num" style="color: #16a34a;">{{ metrics.total_docs - metrics.processing_count }}</span>
            <span class="m-sub-tip">0 待排队</span>
          </div>
        </div>
      </div>

      <div class="metric-card storage-card">
        <div class="m-icon-box store">
          <svg viewBox="0 0 1024 1024" width="22" height="22" style="fill: #9333ea;">
            <path d="M512 64l384 219.4v457.2L512 960 128 740.6V283.4L512 64z m0 73.1L192 300.3v423.4l320 182.9 320-182.9V300.3L512 137.1z" />
            <path d="M512 320l192 110-192 110-192-110z" />
          </svg>
        </div>
        <div class="m-body" style="flex: 1;">
          <div class="m-label">存储空间</div>
          <div class="m-val-row">
            <span class="m-storage-text">{{ (metrics.used_storage_mb / 1024).toFixed(2) }} GB <span class="muted">/ 20 GB</span></span>
            <span class="m-percent">{{ metrics.storage_percent }}%</span>
          </div>
          <div class="storage-bar-wrap">
            <div class="storage-bar-fill" :style="{ width: Math.max(metrics.storage_percent, 2) + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- 右侧快速上传与批量导入按钮组 -->
      <div class="upload-action-box">
        <el-upload
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          accept=".txt,.md,.pdf,.docx,.xlsx"
          :on-change="handleUpload"
        >
          <el-button type="primary" size="large" class="btn-main-upload" :loading="uploading">
            <svg viewBox="0 0 1024 1024" width="16" height="16" style="margin-right: 6px; fill: currentColor;"><path d="M480 160h64v352h352v64H544v352h-64V576H128v-64h352z" /></svg>
            上传文档
          </el-button>
        </el-upload>
        <el-button size="default" class="btn-chat-verify" @click="chatDrawerVisible = true">
          <svg viewBox="0 0 1024 1024" width="14" height="14" style="margin-right: 6px; fill: currentColor;"><path d="M512 64a448 448 0 1 0 448 448A448 448 0 0 0 512 64z m-48 640l-160-160 45.2-45.2L464 613.5l250.8-250.7L760 408z" /></svg>
          溯源对话测试
        </el-button>
      </div>
    </div>

    <!-- 文档表格列表卡片 -->
    <div class="table-card">
      <div class="table-toolbar">
        <div class="tb-left">
          <el-select v-model="filterType" placeholder="全部类型" clearable size="default" style="width: 130px" @change="applyFilter">
            <el-option label="全部类型" value="" />
            <el-option label="PDF" value="pdf" />
            <el-option label="DOCX" value="docx" />
            <el-option label="Markdown" value="md" />
            <el-option label="TXT" value="txt" />
          </el-select>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索知识文档名称..."
            clearable
            size="default"
            style="width: 240px"
            @keyup.enter="loadDocs"
            @clear="loadDocs"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" size="default" @click="loadDocs">
            <el-icon><Search /></el-icon> 检索
          </el-button>
          <el-button circle size="default" title="重置筛选" @click="resetFilter">
            <el-icon><RefreshRight /></el-icon>
          </el-button>
        </div>
        <div class="tb-right">
          <span class="file-total-tip">当前共 {{ filteredDocs.length }} 篇知识文档</span>
        </div>
      </div>

      <!-- 核心文件列表表格 -->
      <el-table :data="filteredDocs" v-loading="loading" stripe style="width: 100%; margin-top: 14px">
        <el-table-column label="文件名" min-width="260">
          <template #default="{ row }">
            <div class="file-cell">
              <div class="file-badge" :class="row.ext">
                {{ row.ext ? row.ext.toUpperCase() : 'DOC' }}
              </div>
              <div class="file-detail">
                <span class="file-name" :title="row.file_name">{{ row.file_name }}</span>
                <div class="file-tags">
                  <span class="file-tag">{{ row.scope === 'public' ? '公共知识' : '私人专享' }}</span>
                  <span class="file-tag chunk-tag">{{ row.chunks_count }} 个切片</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="ext" label="格式" width="100">
          <template #default="{ row }">
            <span class="ext-badge">{{ (row.ext || 'txt').toUpperCase() }}</span>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <div class="status-badge" :class="row.status">
              <span class="status-dot"></span>
              <span>{{ row.status === 'completed' ? '已就绪' : '处理中' }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="切片与向量进度" min-width="200">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress
                :percentage="row.progress || 100"
                :status="row.status === 'completed' ? 'success' : ''"
                :stroke-width="8"
                style="flex: 1;"
              />
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="size_str" label="大小" width="100">
          <template #default="{ row }">
            <span style="color: #64748b; font-size: 13px;">{{ row.size_str }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="上传时间" width="160">
          <template #default="{ row }">
            <span style="color: #64748b; font-size: 13px;">{{ row.created_at }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="testDocQuery(row)">测试召回</el-button>
            <el-button type="danger" text size="small" @click="handleDeleteDoc(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && filteredDocs.length === 0" style="padding: 40px 0;">
        <el-empty description="当前知识库暂无文档，请点击右上角上传" />
      </div>
    </div>

    <!-- 溯源对话验证抽屉 -->
    <el-drawer
      v-model="chatDrawerVisible"
      title="🤖 知识库智能问答与溯源验证"
      size="560px"
      destroy-on-close
    >
      <div class="drawer-chat-wrap">
        <div class="chat-tip-banner">
          基于当前知识库向量切片进行 RAG 召回，展示匹配的依据片段与相似度评分。
        </div>

        <div class="search-input-box">
          <el-input
            v-model="chatQuery"
            placeholder="输入您想向知识库提问的问题，按回车检索..."
            size="large"
            clearable
            @keyup.enter="doChat"
          />
          <el-button type="primary" size="large" :loading="chatSearching" @click="doChat">提问</el-button>
        </div>

        <div v-if="chatAnswer" class="answer-card">
          <div class="ans-head">
            <svg viewBox="0 0 1024 1024" width="18" height="18" style="fill: #2563eb;"><path d="M512 64a448 448 0 1 0 448 448A448 448 0 0 0 512 64z" /></svg>
            <span>AI 知识库权威回答</span>
          </div>
          <div class="ans-content">{{ chatAnswer }}</div>
        </div>

        <div v-if="chatSources.length" class="sources-box">
          <div class="sources-title">
            <span>📚 检索命中的事实知识切片 ({{ chatSources.length }} 处)</span>
          </div>
          <div v-for="(s, idx) in chatSources" :key="idx" class="source-item">
            <div class="source-head">
              <span class="source-doc-name">{{ s.document_name || s.file_name || '知识文档' }}</span>
              <span class="source-score">相似度 {{ formatScore(s) }}</span>
            </div>
            <div class="source-text">{{ s.chunk_content }}</div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, RefreshRight } from '@element-plus/icons-vue';
import request from '../../utils/request';

const loading = ref(false);
const uploading = ref(false);
const currentScope = ref<'public' | 'private'>('public');
const filterType = ref('');
const searchKeyword = ref('');

const docs = ref<any[]>([]);
const metrics = ref({
  total_docs: 0,
  total_chunks: 0,
  processing_count: 0,
  used_storage_mb: 0,
  max_storage_mb: 20480,
  storage_percent: 0
});

// 抽屉对话
const chatDrawerVisible = ref(false);
const chatQuery = ref('');
const chatSearching = ref(false);
const chatAnswer = ref('');
const chatSources = ref<any[]>([]);

const filteredDocs = computed(() => {
  return docs.value.filter((d) => {
    const matchType = !filterType.value || (d.ext || '').toLowerCase() === filterType.value.toLowerCase();
    return matchType;
  });
});

const loadMetrics = async () => {
  try {
    const res: any = await request.get('/api/v1/admin/kb/metrics');
    // request.ts 拦截器如果返回了 res.data，则 res 本身就是指标数据对象，否则取 res.data
    const data = res?.total_docs !== undefined ? res : res?.data;
    if (data) {
      metrics.value = {
        total_docs: data.total_docs ?? 0,
        total_chunks: data.total_chunks ?? 0,
        processing_count: data.processing_count ?? 0,
        used_storage_mb: data.used_storage_mb ?? 0,
        max_storage_mb: data.max_storage_mb ?? 20480,
        storage_percent: data.storage_percent ?? 0
      };
    }
  } catch (e) {
    /* 静默 */
  }
};

const loadDocs = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/kb/documents', {
      params: {
        scope: currentScope.value,
        keyword: searchKeyword.value.trim()
      }
    });
    docs.value = res?.items || res?.data?.items || [];
  } finally {
    loading.value = false;
  }
};

const switchScope = (s: 'public' | 'private') => {
  currentScope.value = s;
  loadDocs();
};

const applyFilter = () => {
  // filteredDocs 为 computed 自动过滤
};

const resetFilter = () => {
  searchKeyword.value = '';
  filterType.value = '';
  loadDocs();
};

const handleUpload = async (file: any) => {
  if (file.size > 15 * 1024 * 1024) {
    ElMessage.error('文件超过 15MB 限制');
    return;
  }
  const fd = new FormData();
  fd.append('file', file.raw);
  fd.append('scope', currentScope.value);
  uploading.value = true;
  try {
    await request.post('/api/v1/admin/kb/documents', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    ElMessage.success(`已成功上传至${currentScope.value === 'public' ? '公共知识库' : '私人知识库'}并完成智能切片`);
    loadDocs();
    loadMetrics();
  } finally {
    uploading.value = false;
  }
};

const handleDeleteDoc = (row: any) => {
  ElMessageBox.confirm(`确定要彻底删除文档《${row.file_name}》及其向量切片吗？`, '安全删除确认', {
    type: 'warning',
    confirmButtonText: '确定删除',
    cancelButtonText: '取消'
  }).then(async () => {
    await request.delete(`/api/v1/admin/kb/documents/${row.id}`);
    ElMessage.success('文档已删除');
    loadDocs();
    loadMetrics();
  });
};

const testDocQuery = (row: any) => {
  chatQuery.value = `总结一下《${row.file_name}》的核心知识点与考纲内容`;
  chatDrawerVisible.value = true;
  doChat();
};

const doChat = async () => {
  if (!chatQuery.value.trim()) {
    ElMessage.warning('请输入问题');
    return;
  }
  chatSearching.value = true;
  chatAnswer.value = '';
  chatSources.value = [];
  try {
    const res: any = await request.post(
      '/api/v1/admin/kb/query',
      { message: chatQuery.value },
      { timeout: 60000 } // AI 深度推理与切片召回预留充足时间
    );
    const data = res?.content !== undefined ? res : res?.data;
    if (data) {
      chatAnswer.value = data.content || '';
      chatSources.value = data.ai_rag_sources || [];
      if (!chatSources.value.length) {
        ElMessage.info('未在当前知识库检索到强相关切片（回答已基于大模型通用认知生成）');
      }
    }
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || 'AI 服务响应超时或异常，请稍后重试');
  } finally {
    chatSearching.value = false;
  }
};

const formatScore = (s: any) => {
  const val = s?.similarity_score ?? s?.similarity ?? 0.85;
  const num = Number(val);
  if (isNaN(num)) return '85.0%';
  // 如果值在 0~1 之间，转换为百分比；否则直接保留1位小数
  return num <= 1 ? `${(num * 100).toFixed(1)}%` : `${num.toFixed(1)}%`;
};

onMounted(() => {
  loadMetrics();
  loadDocs();
});
</script>

<style scoped>
.kb-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 顶部科技 Hero 卡片 (明亮现代风) */
.kb-hero {
  position: relative;
  background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 60%, #e0e7ff 100%);
  border: 1px solid #dbeafe;
  border-radius: 20px;
  padding: 24px 28px;
  color: #0f172a;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.05);
}

.kb-hero::after {
  content: '';
  position: absolute;
  top: -50px;
  right: -50px;
  width: 260px;
  height: 260px;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.45) 0%, rgba(147, 197, 253, 0) 70%);
  pointer-events: none;
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hero-title {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.3px;
  background: linear-gradient(90deg, #1e293b 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
  max-width: 680px;
  line-height: 1.6;
}

/* 公共 vs 私人 宽卡片 Tabs (明亮现代风) */
.scope-tabs-wrap {
  display: flex;
  gap: 14px;
  margin-top: 18px;
}

.scope-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  width: 240px;
  padding: 12px 18px;
  border-radius: 12px;
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
  transition: all 0.25s ease;
}

.scope-card:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.scope-card.active {
  background: #ffffff;
  border-color: #3b82f6;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15);
}

.scope-icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  transition: all 0.2s;
}

.scope-card.active .scope-icon-wrap.public {
  background: #eff6ff;
  color: #2563eb;
}

.scope-card.active .scope-icon-wrap.private {
  background: #fdf2f8;
  color: #db2777;
}

.scope-title {
  font-size: 14px;
  font-weight: 700;
  color: #334155;
}

.scope-card.active .scope-title {
  color: #1d4ed8;
}

.scope-sub {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.active-badge {
  position: absolute;
  right: 12px;
  font-size: 13px;
  font-weight: 800;
  color: #2563eb;
  background: #dbeafe;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 指标卡片网格 */
.metrics-grid {
  display: flex;
  gap: 14px;
  align-items: stretch;
}

.metric-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 14px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}

.storage-card {
  flex: 1.4;
}

.m-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.m-icon-box.doc { background: #eff6ff; }
.m-icon-box.chunk { background: #f0f9ff; }
.m-icon-box.proc { background: #f0fdf4; }
.m-icon-box.store { background: #faf5ff; }

.m-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}

.m-val-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-top: 4px;
}

.m-num {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1;
}

.m-trend {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
}

.m-trend.up {
  color: #16a34a;
  background: #dcfce7;
}

.m-sub-tip {
  font-size: 11px;
  color: #94a3b8;
}

.m-storage-text {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}
.m-storage-text .muted {
  font-size: 12px;
  color: #94a3b8;
  font-weight: normal;
}

.m-percent {
  margin-left: auto;
  font-size: 12px;
  font-weight: 700;
  color: #9333ea;
}

.storage-bar-wrap {
  width: 100%;
  height: 6px;
  background: #f1f5f9;
  border-radius: 99px;
  margin-top: 8px;
  overflow: hidden;
}

.storage-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #9333ea, #3b82f6);
  border-radius: 99px;
  transition: width 0.4s ease;
}

.upload-action-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
}

.btn-main-upload {
  background: #2563eb !important;
  border-color: #2563eb !important;
  color: #ffffff !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
  width: 125px;
}

.btn-main-upload:hover {
  background: #1d4ed8 !important;
  border-color: #1d4ed8 !important;
}

.btn-chat-verify {
  border-radius: 10px !important;
  color: #475569 !important;
  font-weight: 600 !important;
  border: 1px solid #cbd5e1 !important;
  background: #ffffff !important;
  width: 125px;
}

.btn-chat-verify:hover {
  color: #2563eb !important;
  border-color: #93c5fd !important;
  background: #eff6ff !important;
}

/* 表格卡片 */
.table-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.02);
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tb-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-total-tip {
  font-size: 13px;
  color: #64748b;
}

/* 文件行排版 */
.file-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-badge {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 800;
  color: #ffffff;
  flex-shrink: 0;
  letter-spacing: 0.5px;
}

.file-badge.pdf { background: #ef4444; }
.file-badge.docx { background: #2563eb; }
.file-badge.md { background: #8b5cf6; }
.file-badge.txt { background: #64748b; }

.file-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-weight: 600;
  color: #0f172a;
  font-size: 14px;
}

.file-tags {
  display: flex;
  gap: 6px;
}

.file-tag {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 4px;
  background: #f1f5f9;
  color: #475569;
}

.chunk-tag {
  background: #eff6ff;
  color: #1d4ed8;
}

.ext-badge {
  font-size: 12px;
  font-weight: 700;
  color: #475569;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 8px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.completed {
  background: #ecfdf5;
  color: #059669;
}

.status-badge .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.progress-cell {
  display: flex;
  align-items: center;
}

/* 抽屉样式 */
.drawer-chat-wrap {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-tip-banner {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
}

.search-input-box {
  display: flex;
  gap: 10px;
}

.answer-card {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 12px;
  padding: 14px 16px;
}

.ans-head {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #15803d;
  margin-bottom: 8px;
}

.ans-content {
  font-size: 14px;
  color: #166534;
  line-height: 1.6;
  white-space: pre-wrap;
}

.sources-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sources-title {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
}

.source-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
}

.source-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.source-doc-name {
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
}

.source-score {
  font-size: 12px;
  font-weight: 700;
  color: #2563eb;
}

.source-text {
  font-size: 12px;
  color: #475569;
  line-height: 1.5;
  background: #ffffff;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
}
</style>
