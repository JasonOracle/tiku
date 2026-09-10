<!--
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：Gemini 系列
 * 修改内容：[1. Tabs 更名为「题目分类」与「试卷分类」; 2. 按钮文字统一精简为「新增」; 3. 移除分类用途与排序权重列; 4. 实现原生表格行上下拖拽排序与实时持久化保存; 5. 弹窗移除分类用途与排序权重项，新建默认自动置顶]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗：资源/任务两用分类，旧题目/试卷词汇已删除]
-->
<template>
  <div class="page-card">
    <el-tabs v-model="activeTab" class="cat-tabs" @tab-change="loadCategories">
      <el-tab-pane label="题目分类" name="resource" />
      <el-tab-pane label="试卷分类" name="task" />
    </el-tabs>

    <div class="filter-bar" style="margin-top: 16px; display: flex; justify-content: space-between; align-items: center;">
      <el-button type="primary" class="primary-btn" @click="openCreateDialog">
        <el-icon><Plus /></el-icon> 新增
      </el-button>
      <span class="drag-hint">💡 提示：按住表格行可直接上下拖拽调换排序</span>
    </div>

    <el-table
      ref="tableRef"
      :data="categories"
      v-loading="loading"
      stripe
      style="width: 100%; margin-top: 16px"
      row-key="id"
      :row-class-name="getRowClassName"
    >
      <!-- 拖拽把手图标列 -->
      <el-table-column width="50" align="center">
        <template #default>
          <span class="drag-handle" title="按住可上下拖拽调序">
            <el-icon><Rank /></el-icon>
          </span>
        </template>
      </el-table-column>

      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="分类名称" />

      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button type="danger" text size="small" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="440px" destroy-on-close>
      <el-form :model="form" label-width="80px" style="margin-top: 8px">
        <el-form-item label="分类名称" required>
          <el-input
            v-model="form.name"
            :placeholder="form.target_type === 'resource' ? '如：近代史、金融类、消防安全' : '如：模拟任务、真题、期末考核'"
            maxlength="50"
            clearable
            @keyup.enter="saveCategory"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!form.name.trim()" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Rank } from '@element-plus/icons-vue';
import request from '../../utils/request';

const activeTab = ref('resource');
const loading = ref(false);
const categories = ref<any[]>([]);
const tableRef = ref<any>(null);

const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const dialogTitle = computed(() =>
  editingId.value ? '编辑分类' : `新增${activeTab.value === 'resource' ? '题目' : '试卷'}分类`
);

const form = reactive({ name: '', target_type: 'resource' });

const getRowClassName = ({ rowIndex }: { rowIndex: number }) => {
  return `cat-draggable-row row-idx-${rowIndex}`;
};

const loadCategories = async (tabName?: string) => {
  if (tabName && typeof tabName === 'string') {
    activeTab.value = tabName;
  }
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/categories', {
      params: { target_type: activeTab.value }
    });
    categories.value = res.items || [];
    nextTick(() => {
      initDragEvents();
    });
  } finally {
    loading.value = false;
  }
};

const openCreateDialog = () => {
  editingId.value = null;
  form.name = '';
  form.target_type = activeTab.value;
  dialogVisible.value = true;
};

const openEditDialog = (row: any) => {
  editingId.value = row.id;
  form.name = row.name;
  form.target_type = row.target_type;
  dialogVisible.value = true;
};

const saveCategory = async () => {
  const name = form.name.trim();
  if (!name) {
    ElMessage.error('分类名称不能为空');
    return;
  }
  if (editingId.value) {
    await request.put(`/api/v1/admin/categories/${editingId.value}`, {
      name,
      target_type: form.target_type
    });
    ElMessage.success('修改成功');
  } else {
    await request.post('/api/v1/admin/categories', {
      name,
      target_type: form.target_type
    });
    ElMessage.success('创建成功');
  }
  dialogVisible.value = false;
  loadCategories();
};

const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定删除该分类吗？正被使用的分类不可删除。', '提示', { type: 'warning' }).then(async () => {
    await request.delete(`/api/v1/admin/categories/${id}`);
    ElMessage.success('已删除');
    loadCategories();
  });
};

// ==========================================
// 原生 HTML5 表格行上下拖拽排序实现（零外部包依赖）
// ==========================================
let dragSourceIndex: number | null = null;

const initDragEvents = () => {
  const tableEl = tableRef.value?.$el;
  if (!tableEl) return;
  const tbody = tableEl.querySelector('tbody');
  if (!tbody) return;

  const rows = tbody.querySelectorAll('tr.cat-draggable-row');
  rows.forEach((tr: HTMLTableRowElement, index: number) => {
    tr.setAttribute('draggable', 'true');

    tr.ondragstart = (e: DragEvent) => {
      dragSourceIndex = index;
      tr.classList.add('is-dragging');
      if (e.dataTransfer) {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', String(index));
      }
    };

    tr.ondragover = (e: DragEvent) => {
      e.preventDefault();
      if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
      tr.classList.add('drag-over');
    };

    tr.ondragleave = () => {
      tr.classList.remove('drag-over');
    };

    tr.ondragend = () => {
      tr.classList.remove('is-dragging');
      rows.forEach((r: Element) => r.classList.remove('drag-over'));
      dragSourceIndex = null;
    };

    tr.ondrop = async (e: DragEvent) => {
      e.preventDefault();
      tr.classList.remove('drag-over');
      const targetIndex = index;
      if (dragSourceIndex === null || dragSourceIndex === targetIndex) return;

      // 调整前端本地数组
      const movingItem = categories.value.splice(dragSourceIndex, 1)[0];
      categories.value.splice(targetIndex, 0, movingItem);

      // 持久化到后端
      try {
        const idList = categories.value.map(c => c.id);
        await request.put('/api/v1/admin/categories/reorder', {
          category_ids: idList
        });
        ElMessage.success('排序已更新');
      } catch (err) {
        loadCategories();
      }
    };
  });
};

onMounted(() => {
  loadCategories();
});
</script>

<style scoped>
.page-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.primary-btn {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  border: none;
  padding: 8px 20px;
}

.drag-hint {
  font-size: 13px;
  color: #64748b;
}

.drag-handle {
  cursor: grab;
  color: #94a3b8;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
}

.drag-handle:active {
  cursor: grabbing;
}
</style>

<style>
/* 拖拽动态样式 */
tr.cat-draggable-row {
  transition: background-color 0.15s ease;
}

tr.cat-draggable-row.is-dragging {
  opacity: 0.4;
  background: #f1f5f9 !important;
}

tr.cat-draggable-row.drag-over {
  border-top: 2px solid #0284c7 !important;
  background: #e0f2fe !important;
}
</style>
