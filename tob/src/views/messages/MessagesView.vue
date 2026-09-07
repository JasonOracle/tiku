<!--
 * [变更日志]
 * 修改时间：2026-09-06 20:40:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.2 新增消息中心: 站内信列表/未读过滤/单条与全部已读/链接跳转]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <el-checkbox v-model="unreadOnly" @change="loadList">只看未读</el-checkbox>
      <el-button text type="primary" @click="markAllRead">全部标记已读</el-button>
    </div>

    <el-table :data="items" v-loading="loading" style="width: 100%; margin-top: 14px" @row-click="handleRowClick">
      <el-table-column width="50">
        <template #default="{ row }">
          <span class="dot" :class="{ unread: !row.is_read }"></span>
        </template>
      </el-table-column>
      <el-table-column label="类型" width="110">
        <template #default="{ row }">
          <el-tag size="small" :type="typeTag(row.notif_type)">{{ typeLabel(row.notif_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="200">
        <template #default="{ row }">
          <span :style="{ fontWeight: row.is_read ? 400 : 700 }">{{ row.title }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
      <el-table-column prop="created_at" label="时间" width="170" />
      <el-table-column label="操作" width="170" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.link" type="primary" text size="small" @click="goLink(row)">前往处理</el-button>
          <el-button v-if="!row.is_read" text size="small" @click="markRead(row)">标为已读</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination v-model:current-page="page" :page-size="size" :total="total"
                     layout="total, prev, pager, next" @current-change="loadList" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '../../utils/request';

const router = useRouter();
const items = ref<any[]>([]);
const loading = ref(false);
const unreadOnly = ref(false);
const page = ref(1);
const size = 15;
const total = ref(0);

const typeTag = (t: string) => (t === 'ai_error' ? 'danger' : t === 'grading' ? 'warning' : t === 'exam_draft' ? 'success' : 'info');
const typeLabel = (t: string) => ({ grading: '阅卷', exam_draft: '组卷', ai_error: 'AI异常', system: '系统' } as any)[t] || '系统';

const loadList = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/notifications', {
      params: { unread_only: unreadOnly.value, page: page.value, size }
    });
    items.value = res.items || [];
    total.value = res.total || 0;
  } finally {
    loading.value = false;
  }
};

const markRead = async (row: any) => {
  await request.post('/api/v1/admin/notifications/read', { ids: [row.id] });
  loadList();
};

const markAllRead = async () => {
  await request.post('/api/v1/admin/notifications/read', { ids: null });
  ElMessage.success('已全部标记为已读');
  loadList();
};

const goLink = async (row: any) => {
  if (!row.is_read) {
    row.is_read = true; // Optimistic update
    await request.post('/api/v1/admin/notifications/read', { ids: [row.id] });
  }
  if (row.link && row.link.startsWith('/admin/')) {
    router.push(row.link.replace('/admin', ''));
  }
  loadList();
};

const handleRowClick = async (row: any) => {
  if (!row.is_read) {
    row.is_read = true; // Optimistic update to make red dot disappear immediately
    await request.post('/api/v1/admin/notifications/read', { ids: [row.id] });
  }
};

onMounted(loadList);
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

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e2e8f0;
}

.dot.unread {
  background: #ef4444;
}

.el-table__row {
  cursor: pointer;
}
</style>
