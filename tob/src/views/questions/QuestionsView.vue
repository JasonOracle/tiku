<!--
 * [变更日志]
 * 修改时间：2026-09-04
 * AI模型：Gemini 底层
 * 修改内容：[1. 增加无题目分类时的强引导弹窗拦截; 2. 新建/编辑题目时所属分类设为必选项; 3. 添加 checkbox-group 复选列与批量删除功能]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="filters">
        <el-input v-model="filters.keyword" placeholder="搜索题目关键词..." clearable style="width: 200px" @change="loadQuestions" />
        <el-select v-model="filters.category_id" placeholder="全部分类" clearable style="width: 140px" @change="loadQuestions">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="filters.type" placeholder="全部分型" clearable style="width: 120px" @change="loadQuestions">
          <el-option label="单选题" value="single" />
          <el-option label="多选题" value="multiple" />
          <el-option label="判断题" value="judge" />
        </el-select>
      </div>

      <div class="actions">
        <el-button
          v-if="selectedQuestionIds.length > 0"
          type="danger"
          plain
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon> 批量删除 ({{ selectedQuestionIds.length }})
        </el-button>
        <el-button type="primary" class="primary-btn" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> 新建题目
        </el-button>
        <el-button type="success" plain @click="openImportDialog">
          <el-icon><Upload /></el-icon> Excel 导入
        </el-button>
      </div>
    </div>

    <!-- 题目数据表格 -->
    <el-table
      :data="questions"
      v-loading="loading"
      stripe
      style="width: 100%; margin-top: 16px"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="50" />
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="type" label="题型" width="90">
        <template #default="{ row }">
          <el-tag :type="getTypeTag(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="category_id" label="所属分类" width="120">
        <template #default="{ row }">
          <el-tag type="info" effect="plain">{{ getCategoryName(row.category_id) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="题干" min-width="240" show-overflow-tooltip />
      <el-table-column prop="score" label="默认分值" width="90">
        <template #default="{ row }">
          <span style="font-weight: 700; color: #0284c7">{{ row.score || 10 }} 分</span>
        </template>
      </el-table-column>
      <el-table-column prop="difficulty" label="难度" width="90">
        <template #default="{ row }">
          <el-tag effect="plain" :type="row.difficulty === 'easy' ? 'success' : row.difficulty === 'hard' ? 'danger' : 'warning'">
            {{ getDifficultyLabel(row.difficulty) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" text size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button type="danger" text size="small" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        layout="total, prev, pager, next, jumper"
        @current-change="loadQuestions"
      />
    </div>

    <!-- 新建/编辑 Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="所属分类" required>
          <el-select v-model="form.category_id" placeholder="请选择题目分类（必填）" style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="题型" required>
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="单选题" value="single" />
            <el-option label="多选题" value="multiple" />
            <el-option label="判断题" value="judge" />
          </el-select>
        </el-form-item>
        <el-form-item label="题干" required>
          <el-input v-model="form.title" type="textarea" :rows="3" placeholder="请输入题目详细描述..." />
        </el-form-item>
        <el-form-item label="默认分数" required>
          <el-input-number v-model="form.score" :min="1" :max="100" style="width: 160px" />
          <span style="margin-left: 8px; color: #64748b; font-size: 12px">组卷时将自动累加为试卷总分</span>
        </el-form-item>
        <el-form-item label="难度" required>
          <el-radio-group v-model="form.difficulty">
            <el-radio-button label="easy">简单</el-radio-button>
            <el-radio-button label="medium">中等</el-radio-button>
            <el-radio-button label="hard">困难</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="选项">
          <div v-for="(opt, idx) in form.options" :key="idx" class="option-row">
            <span class="opt-key">{{ opt.key }}.</span>
            <el-input v-model="opt.text" placeholder="选项描述" />
            <el-button type="danger" circle text @click="removeOption(idx)"><el-icon><Delete /></el-icon></el-button>
          </div>
          <el-button type="primary" text @click="addOption">+ 添加选项</el-button>
        </el-form-item>
        <el-form-item label="标准答案" required>
          <el-input v-model="answerStr" placeholder="如 A 或 A,B" />
        </el-form-item>
        <el-form-item label="文字解析">
          <el-input v-model="form.explanation" type="textarea" :rows="2" placeholder="解析说明..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveQuestion">保存</el-button>
      </template>
    </el-dialog>

    <!-- Excel 批量导入 Dialog -->
      <el-dialog v-model="importDialogVisible" title="批量导入题目" width="480px">
      <div style="margin-bottom: 12px; color: #64748b; font-size: 13px">
        分类按 Excel “分类”列逐题归入（不存在自动新建，留空归第一个分类）；short / fill 为预留题型，导入时跳过计数。
      </div>

      <el-upload
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".xlsx, .xls"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">将 Excel 文件拖到此处，或 <em>点击上传</em></div>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="submitImport">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Upload, Delete, UploadFilled } from '@element-plus/icons-vue';
import request from '../../utils/request';

import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(false);
const questions = ref<any[]>([]);
const categories = ref<any[]>([]);
const filters = reactive({ keyword: '', type: '', category_id: null });
const pagination = reactive({ page: 1, size: 10, total: 0 });
const selectedQuestionIds = ref<number[]>([]);

const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const dialogTitle = computed(() => (editingId.value ? '编辑题目' : '新建题目'));

const handleSelectionChange = (val: any[]) => {
  selectedQuestionIds.value = val.map((item) => item.id);
};

const checkCategoryPrerequisite = (): boolean => {
  if (categories.value.length === 0) {
    ElMessageBox.confirm('当前暂无任何“题目分类”，无法新建或导入题目。请先去新建题目分类。', '无法进行此操作', {
      confirmButtonText: '去新建题目分类',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      router.push('/categories');
    }).catch(() => {});
    return false;
  }
  return true;
};

const openImportDialog = () => {
  if (!checkCategoryPrerequisite()) return;
  importDialogVisible.value = true;
};

const form = reactive({
  type: 'single',
  title: '',
  score: 10,
  difficulty: 'medium',
  category_id: null as number | null,
  options: [
    { key: 'A', text: '' },
    { key: 'B', text: '' }
  ],
  answer: ['A'],
  explanation: ''
});

const answerStr = computed({
  get: () => form.answer.join(','),
  set: (val: string) => {
    form.answer = val.split(',').map((s: string) => s.trim().toUpperCase()).filter(Boolean);
  }
});

const importDialogVisible = ref(false);
const importing = ref(false);
const selectedFile = ref<File | null>(null);

const firstCategoryId = () => (categories.value.length > 0 ? categories.value[0].id : null);

const loadCategories = async () => {
  try {
    const res: any = await request.get('/api/v1/admin/categories', {
      params: { target_type: 'question' }
    });
    categories.value = res || [];
  } catch (e) {
    categories.value = [];
  }
};

const getCategoryName = (catId: number | null) => {
  if (!catId) return '无分类';
  const c = categories.value.find((item) => item.id === catId);
  return c ? c.name : `分类#${catId}`;
};

const loadQuestions = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/questions', {
      params: { ...filters, page: pagination.page, size: pagination.size }
    });
    questions.value = res.items || [];
    pagination.total = res.total || 0;
  } finally {
    loading.value = false;
  }
};

const getTypeTag = (type: string) => {
  if (type === 'single') return 'primary';
  if (type === 'multiple') return 'warning';
  return 'info';
};

const getTypeLabel = (type: string) => {
  if (type === 'single') return '单选题';
  if (type === 'multiple') return '多选题';
  return '判断题';
};

const getDifficultyLabel = (diff: string) => {
  if (diff === 'easy') return '简单';
  if (diff === 'hard') return '困难';
  return '中等';
};

const addOption = () => {
  const keys = ['A', 'B', 'C', 'D', 'E', 'F'];
  const nextKey = keys[form.options.length] || 'X';
  form.options.push({ key: nextKey, text: '' });
};

const removeOption = (idx: number) => {
  form.options.splice(idx, 1);
};

const openCreateDialog = () => {
  if (!checkCategoryPrerequisite()) return;
  editingId.value = null;
  form.type = 'single';
  form.title = '';
  form.score = 10;
  form.difficulty = 'medium';
  form.category_id = firstCategoryId();
  form.options = [{ key: 'A', text: '' }, { key: 'B', text: '' }];
  form.answer = ['A'];
  form.explanation = '';
  dialogVisible.value = true;
};

const openEditDialog = (row: any) => {
  editingId.value = row.id;
  form.type = row.type;
  form.title = row.title;
  form.score = row.score || 10;
  form.difficulty = row.difficulty || 'medium';
  form.category_id = row.category_id || firstCategoryId();
  form.options = row.options || [];
  form.answer = row.answer || [];
  form.explanation = row.explanation || '';
  dialogVisible.value = true;
};

const saveQuestion = async () => {
  if (!form.category_id) {
    ElMessage.error('请选择所属分类');
    return;
  }
  if (!form.title) {
    ElMessage.error('题干不能为空');
    return;
  }
  if (editingId.value) {
    await request.put(`/api/v1/admin/questions/${editingId.value}`, form);
    ElMessage.success('题目已修改');
  } else {
    await request.post('/api/v1/admin/questions', form);
    ElMessage.success('题目已创建');
  }
  dialogVisible.value = false;
  loadQuestions();
};

const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除该题目吗？被已上架/已归档试卷引用的题目不可删除。', '提示', { type: 'warning' }).then(async () => {
    await request.delete(`/api/v1/admin/questions/${id}`);
    ElMessage.success('删除成功');
    loadQuestions();
  });
};

const handleBatchDelete = () => {
  if (selectedQuestionIds.value.length === 0) return;
  ElMessageBox.confirm(`确定要批量删除已选中的 ${selectedQuestionIds.value.length} 道题目吗？`, '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    let successCount = 0;
    let failCount = 0;
    for (const qId of selectedQuestionIds.value) {
      try {
        await request.delete(`/api/v1/admin/questions/${qId}`);
        successCount++;
      } catch (e) {
        failCount++;
      }
    }
    if (failCount > 0) {
      ElMessage.warning(`成功删除 ${successCount} 道题目，${failCount} 道被试卷关联的题目无法删除`);
    } else {
      ElMessage.success(`已成功批量删除 ${successCount} 道题目`);
    }
    selectedQuestionIds.value = [];
    loadQuestions();
  });
};

const handleFileChange = (uploadFile: any) => {
  selectedFile.value = uploadFile.raw;
};

const submitImport = async () => {
  if (!selectedFile.value) {
    ElMessage.error('请选择 Excel 文件');
    return;
  }
  importing.value = true;
  const formData = new FormData();
  formData.append('file', selectedFile.value);
  try {
    const res: any = await request.post('/api/v1/admin/questions/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    const skipped = res.skipped_count || 0;
    ElMessage.success(`成功导入 ${res.imported_count} 道题目${skipped ? `，跳过 ${skipped} 行预留题型` : ''}`);
    importDialogVisible.value = false;
    loadQuestions();
  } finally {
    importing.value = false;
  }
};

onMounted(() => {
  loadCategories();
  loadQuestions();
});
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

.filters {
  display: flex;
  gap: 12px;
}

.actions {
  display: flex;
  gap: 12px;
}

.primary-btn {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  border: none;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.opt-key {
  font-weight: 700;
  color: #0284c7;
  width: 20px;
}
</style>
