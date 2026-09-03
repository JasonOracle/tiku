<!--
 * [变更日志]
 * 修改时间：2026-09-04 00:08:00
 * AI模型：Gemini 底层
 * 修改内容：[1. 实现题目分类 (target_type='question') 与试卷分类 (target_type='exam') Tabs 选项卡双重隔离 CRUD]
-->
<template>
  <div class="page-card">
    <el-tabs v-model="activeTab" class="cat-tabs" @tab-change="loadCategories">
      <el-tab-pane label="题目分类 (题海专用)" name="question" />
      <el-tab-pane label="试卷分类 (考试场景)" name="exam" />
    </el-tabs>

    <div class="filter-bar" style="margin-top: 16px">
      <el-button type="primary" class="primary-btn" @click="openCreateDialog">
        <el-icon><Plus /></el-icon> 新增 {{ activeTab === 'question' ? '题目分类' : '试卷分类' }}
      </el-button>
    </div>

    <el-table :data="categories" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="分类名称" />
      <el-table-column prop="target_type" label="分类用途" width="140">
        <template #default="{ row }">
          <el-tag :type="row.target_type === 'question' ? 'warning' : 'primary'">
            {{ row.target_type === 'question' ? '题目分类' : '试卷分类' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="icon" label="图标 key" width="120" />
      <el-table-column prop="sort_order" label="排序权重" width="100" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button type="danger" text size="small" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="450px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="分类用途">
          <el-tag :type="form.target_type === 'question' ? 'warning' : 'primary'">
            {{ form.target_type === 'question' ? '题目分类' : '试卷分类' }}
          </el-tag>
        </el-form-item>
        <el-form-item label="分类名称" required>
          <el-input v-model="form.name" :placeholder="form.target_type === 'question' ? '如：金融类、消防安全' : '如：模拟试卷、真题'" />
        </el-form-item>
        <el-form-item label="图标标识">
          <el-input v-model="form.icon" placeholder="默认 folder" />
        </el-form-item>
        <el-form-item label="排序权重">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import request from '../../utils/request';

const activeTab = ref('question');
const loading = ref(false);
const categories = ref<any[]>([]);

const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const dialogTitle = computed(() => (editingId.value ? '编辑分类' : `新增${activeTab.value === 'question' ? '题目' : '试卷'}分类`));

const form = reactive({ name: '', target_type: 'question', icon: 'folder', sort_order: 1 });

const loadCategories = async (tabName?: string) => {
  if (tabName && typeof tabName === 'string') {
    activeTab.value = tabName;
  }
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/categories', {
      params: { target_type: activeTab.value }
    });
    categories.value = res || [];
  } finally {
    loading.value = false;
  }
};

const openCreateDialog = () => {
  editingId.value = null;
  form.name = '';
  form.target_type = activeTab.value;
  form.icon = 'folder';
  form.sort_order = 1;
  dialogVisible.value = true;
};

const openEditDialog = (row: any) => {
  editingId.value = row.id;
  form.name = row.name;
  form.target_type = row.target_type;
  form.icon = row.icon;
  form.sort_order = row.sort_order;
  dialogVisible.value = true;
};

const saveCategory = async () => {
  if (!form.name) {
    ElMessage.error('分类名称不能为空');
    return;
  }
  if (editingId.value) {
    await request.put(`/api/v1/admin/categories/${editingId.value}`, form);
    ElMessage.success('修改成功');
  } else {
    await request.post('/api/v1/admin/categories', form);
    ElMessage.success('创建成功');
  }
  dialogVisible.value = false;
  loadCategories();
};

const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定删除该分类吗？正被题目/试卷使用的分类不可删除。', '提示', { type: 'warning' }).then(async () => {
    await request.delete(`/api/v1/admin/categories/${id}`);
    ElMessage.success('已删除');
    loadCategories();
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
}

.primary-btn {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  border: none;
}
</style>
