<!--
 * [变更日志]
 * 修改时间：2026-09-04 00:08:00
 * AI模型：Gemini 底层
 * 修改内容：[1. 试卷分类仅绑定 target_type='exam'; 2. 新增上架/下架切换(带 Confirm 警示确认); 3. 已上架试卷锁定编辑，可查看“考情数据”看板(展示参与人数、平均分、及格率及作答记录)]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="filters">
        <el-input v-model="filters.keyword" placeholder="搜索试卷名称..." clearable style="width: 220px" @change="loadExams" />
        <el-select v-model="filters.category_id" placeholder="全部试卷分类" clearable style="width: 160px" @change="loadExams">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </div>

      <div class="actions">
        <el-button type="primary" class="primary-btn" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> 新建试卷
        </el-button>
      </div>
    </div>

    <!-- 试卷列表表格 -->
    <el-table :data="exams" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="试卷名称" min-width="200" show-overflow-tooltip />
      <el-table-column prop="category_id" label="试卷分类" width="140">
        <template #default="{ row }">
          <el-tag type="info" effect="plain">{{ row.category_name || getCategoryName(row.category_id) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="上架状态" width="130">
        <template #default="{ row }">
          <el-switch
            :model-value="row.status === 'published'"
            :disabled="row.status === 'archived'"
            active-text="已上架"
            :inactive-text="row.status === 'archived' ? '已归档' : '待上架'"
            inline-prompt
            @change="(val: boolean) => handleStatusChange(row, val)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="question_count" label="题目数" width="85">
        <template #default="{ row }">
          <span style="font-weight: 700; color: #0284c7">{{ row.question_count || 0 }} 题</span>
        </template>
      </el-table-column>
      <el-table-column prop="total_score" label="总分" width="80">
        <template #default="{ row }">
          <span style="font-weight: 700">{{ row.total_score || 0 }} 分</span>
        </template>
      </el-table-column>
      <el-table-column prop="pass_score" label="及格线" width="120">
        <template #default="{ row }">
          <el-tag type="success" effect="light">
            {{ row.pass_score }}分 ({{ row.pass_percent || 60 }}%)
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status !== 'draft'" type="success" text size="small" @click="openStatsDialog(row)">
            <el-icon><DataAnalysis /></el-icon> 考情数据
          </el-button>
          <el-button v-if="row.status === 'draft'" type="primary" text size="small" @click="openEditDialog(row)">编辑/组卷</el-button>
          <el-button v-if="row.status === 'draft'" type="danger" text size="small" @click="handleDelete(row.id)">删除</el-button>
          <el-tag v-if="row.status === 'archived'" type="info" size="small">已归档冻结</el-tag>
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
        @current-change="loadExams"
      />
    </div>

    <!-- 考情看板 Dialog -->
    <el-dialog v-model="statsDialogVisible" title="已上架试卷考情分析数据" width="700px">
      <div v-loading="statsLoading">
        <div class="stats-overview" v-if="statsData">
          <div class="stat-card">
            <span class="stat-num">{{ statsData.total_participants }}</span>
            <span class="stat-label">累计参与作答人数</span>
          </div>
          <div class="stat-card">
            <span class="stat-num" style="color: #0284c7">{{ statsData.avg_score }}</span>
            <span class="stat-label">全站平均得分</span>
          </div>
          <div class="stat-card">
            <span class="stat-num" style="color: #16a34a">{{ statsData.pass_rate }}%</span>
            <span class="stat-label">综合及格通过率</span>
          </div>
        </div>

        <el-divider content-position="left"><strong>用户答卷历史明细</strong></el-divider>

        <el-table :data="statsData?.user_records || []" size="small" stripe style="width: 100%" max-height="300">
          <el-table-column prop="username" label="作答用户" width="130" />
          <el-table-column prop="score" label="得 分" width="90">
            <template #default="{ row }">
              <span style="font-weight: 700">{{ row.score }} 分</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_passed" label="判定" width="90">
            <template #default="{ row }">
              <el-tag :type="row.is_passed ? 'success' : 'danger'" size="small">
                {{ row.is_passed ? '及格' : '未及格' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="time_spent" label="耗时" width="90">
            <template #default="{ row }">
              {{ Math.floor(row.time_spent / 60) }}分{{ row.time_spent % 60 }}秒
            </template>
          </el-table-column>
          <el-table-column prop="submit_time" label="提交时间" min-width="160" />
        </el-table>
      </div>
    </el-dialog>

    <!-- 新建/编辑 试卷 Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="850px" top="40px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="试卷名称" required>
              <el-input v-model="form.title" placeholder="请输入试卷名称" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="试卷分类" required>
              <el-select v-model="form.category_id" placeholder="选择试卷分类" style="width: 100%">
                <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="10">
            <el-form-item label="限时作答">
              <el-switch v-model="form.is_timed" />
              <el-input-number v-if="form.is_timed" v-model="form.time_limit" :min="1" :max="300" style="width: 120px; margin-left: 12px" />
              <span v-if="form.is_timed" style="margin-left: 4px; color: #64748b">分钟</span>
            </el-form-item>
          </el-col>
          <el-col :span="14">
            <el-form-item label="首页推荐">
              <el-switch v-model="form.is_recommended" active-text="推荐至移动端精选Hero卡片" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item label="及格比例">
              <div style="display: flex; align-items: center; width: 100%; gap: 16px">
                <el-slider v-model="form.pass_percent" :min="10" :max="100" :step="5" style="flex: 1" />
                <span style="font-weight: 700; width: 50px; color: #0284c7">{{ form.pass_percent }}%</span>
              </div>
              <div class="score-calc-tip">
                动态计算试卷总分：<strong style="color: #0284c7; font-size: 15px">{{ computedTotalScore }}</strong> 分 ➔ 
                及格线：<strong style="color: #16a34a; font-size: 15px">{{ computedPassScore }}</strong> 分 
                <span style="color: #94a3b8; font-size: 12px">({{ computedTotalScore }}分 × {{ form.pass_percent }}%，向上取整)</span>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left"><strong>组卷配置 (双层结构隔离)</strong></el-divider>

        <!-- 上方：当前已选题目列表 -->
        <div class="selected-box">
          <div class="box-header">
            <span>当前已加入试卷的题目 (共 <strong style="color: #0284c7">{{ selectedQuestions.length }}</strong> 题)</span>
            <el-button v-if="selectedQuestions.length > 0" type="danger" text size="small" @click="selectedQuestions = []">清空已选</el-button>
          </div>

          <el-table :data="selectedQuestions" size="small" border style="width: 100%; margin-top: 8px" max-height="220">
            <el-table-column type="index" label="序号" width="50" align="center" />
            <el-table-column prop="type" label="题型" width="80">
              <template #default="{ row }">
                <el-tag size="small" :type="getTypeTag(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="题干描述" show-overflow-tooltip />
            <el-table-column prop="score" label="分值" width="80">
              <template #default="{ row }">
                <span style="font-weight: 700; color: #0284c7">{{ row.score || 10 }} 分</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="70" align="center">
              <template #default="{ $index }">
                <el-button type="danger" text circle size="small" @click="removeSelectedQuestion($index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 下方：备选题库区 -->
        <div class="pool-box">
          <div class="pool-filter-header">
            <span><strong>题库备选选择区</strong></span>
            <div class="pool-filters">
              <el-radio-group v-model="poolFilter.type" size="small" @change="handlePoolFilterChange">
                <el-radio-button label="">全部题型</el-radio-button>
                <el-radio-button label="single">单选</el-radio-button>
                <el-radio-button label="multiple">多选</el-radio-button>
                <el-radio-button label="judge">判断</el-radio-button>
              </el-radio-group>
              <el-input v-model="poolFilter.keyword" placeholder="搜索题目..." size="small" clearable style="width: 180px" @change="handlePoolFilterChange" />
            </div>
          </div>

          <el-table :data="questionPool" size="small" v-loading="poolLoading" stripe style="width: 100%; margin-top: 8px" max-height="240">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="type" label="题型" width="80">
              <template #default="{ row }">
                <el-tag size="small" :type="getTypeTag(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="题干描述" show-overflow-tooltip />
            <el-table-column prop="score" label="分值" width="70">
              <template #default="{ row }">
                <span>{{ row.score || 10 }}分</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="90" align="center">
              <template #default="{ row }">
                <el-button v-if="isQuestionSelected(row.id)" disabled size="small" text type="info">已加入</el-button>
                <el-button v-else type="primary" size="small" text @click="addQuestionToExam(row)">+ 添加</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div style="display: flex; justify-content: flex-end; margin-top: 8px">
            <el-pagination
              size="small"
              v-model:current-page="poolFilter.page"
              :page-size="poolFilter.size"
              :total="poolFilter.total"
              layout="total, prev, pager, next"
              @current-change="handlePoolPageChange"
            />
          </div>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveExam">保存试卷</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Delete, DataAnalysis } from '@element-plus/icons-vue';
import request from '../../utils/request';

const loading = ref(false);
const exams = ref<any[]>([]);
const categories = ref<any[]>([]);
const filters = reactive({ keyword: '', category_id: null });
const pagination = reactive({ page: 1, size: 10, total: 0 });

const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const dialogTitle = computed(() => (editingId.value ? '编辑试卷与组卷' : '新建试卷'));
const saving = ref(false);

const statsDialogVisible = ref(false);
const statsLoading = ref(false);
const statsData = ref<any>(null);

const form = reactive({
  title: '',
  category_id: null as number | null,
  is_timed: true,
  time_limit: 30,
  pass_percent: 60,
  status: 'draft',
  is_recommended: false
});

const selectedQuestions = ref<any[]>([]);
const questionPool = ref<any[]>([]);
const poolLoading = ref(false);
const poolFilter = reactive({ type: '', keyword: '', page: 1, size: 10, total: 0 });

const computedTotalScore = computed(() => {
  return selectedQuestions.value.reduce((sum, item) => sum + (item.score || 10), 0);
});

const computedPassScore = computed(() => {
  const total = computedTotalScore.value;
  const pct = form.pass_percent || 60;
  return Math.ceil((total * pct) / 100);
});

const loadCategories = async () => {
  try {
    const res: any = await request.get('/api/v1/admin/categories', {
      params: { target_type: 'exam' }
    });
    categories.value = res || [];
  } catch (e) {
    categories.value = [];
  }
};

const getCategoryName = (catId: number | null) => {
  if (!catId) return '未分类';
  const c = categories.value.find((item) => item.id === catId);
  return c ? c.name : `试卷分类#${catId}`;
};

const loadExams = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/exams', {
      params: { ...filters, page: pagination.page, size: pagination.size }
    });
    exams.value = res.items || [];
    pagination.total = res.total || 0;
  } finally {
    loading.value = false;
  }
};

const handleStatusChange = (row: any, val: boolean) => {
  const newStatus = val ? 'published' : 'archived';
  if (!val) {
    ElMessageBox.confirm('下架后试卷将归档冻结（不可再编辑/删除/上架，已作答成绩保留），C 端用户将无法作答，确定要下架吗？', '下架确认', {
      type: 'warning',
      confirmButtonText: '确认下架归档',
      cancelButtonText: '取消'
    }).then(async () => {
      await request.put(`/api/v1/admin/exams/${row.id}/status?status=${newStatus}`);
      ElMessage.success('试卷已下架归档');
      loadExams();
    });
  } else {
    request.put(`/api/v1/admin/exams/${row.id}/status?status=${newStatus}`).then(() => {
      ElMessage.success('试卷已成功上线发布');
      loadExams();
    });
  }
};

const openStatsDialog = async (row: any) => {
  statsDialogVisible.value = true;
  statsLoading.value = true;
  try {
    const res: any = await request.get(`/api/v1/admin/exams/${row.id}/stats`);
    statsData.value = res;
  } finally {
    statsLoading.value = false;
  }
};

const loadQuestionPool = async () => {
  poolLoading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/questions', {
      params: { 
        type: poolFilter.type, 
        keyword: poolFilter.keyword, 
        page: poolFilter.page, 
        size: poolFilter.size 
      }
    });
    questionPool.value = res.items || [];
    poolFilter.total = res.total || 0;
  } finally {
    poolLoading.value = false;
  }
};

const handlePoolPageChange = (page: number) => {
  poolFilter.page = page;
  loadQuestionPool();
};

const handlePoolFilterChange = () => {
  poolFilter.page = 1;
  loadQuestionPool();
};

const isQuestionSelected = (qId: number) => {
  return selectedQuestions.value.some((q) => q.id === qId);
};

const addQuestionToExam = (q: any) => {
  if (!isQuestionSelected(q.id)) {
    selectedQuestions.value.push(q);
  }
};

const removeSelectedQuestion = (idx: number) => {
  selectedQuestions.value.splice(idx, 1);
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

const openCreateDialog = () => {
  editingId.value = null;
  form.title = '';
  form.category_id = categories.value.length > 0 ? categories.value[0].id : null;
  form.is_timed = true;
  form.time_limit = 30;
  form.pass_percent = 60;
  form.status = 'draft';
  form.is_recommended = false;
  selectedQuestions.value = [];
  poolFilter.type = '';
  poolFilter.keyword = '';
  dialogVisible.value = true;
  loadQuestionPool();
};

const openEditDialog = async (row: any) => {
  if (row.status === 'published') {
    ElMessage.warning('已上架试卷已锁定组卷编辑，请先下架后再进行修改');
    return;
  }
  if (row.status === 'archived') {
    ElMessage.warning('该试卷已归档冻结，不可编辑');
    return;
  }
  editingId.value = row.id;
  form.title = row.title;
  // 分类被删后悬空则置空，强制重选
  form.category_id = categories.value.some((c) => c.id === row.category_id) ? row.category_id : null;
  form.is_timed = row.is_timed;
  form.time_limit = row.time_limit;
  form.pass_percent = row.pass_percent || 60;
  form.status = row.status || 'draft';
  form.is_recommended = row.is_recommended;
  selectedQuestions.value = [];
  poolFilter.type = '';
  poolFilter.keyword = '';
  dialogVisible.value = true;

  try {
    const detail: any = await request.get(`/api/v1/admin/exams/${row.id}`);
    selectedQuestions.value = detail.questions || [];
  } catch (e) {
    selectedQuestions.value = [];
  }

  loadQuestionPool();
};

const saveExam = async () => {
  if (!form.title) {
    ElMessage.error('试卷名称不能为空');
    return;
  }
  if (!form.category_id) {
    ElMessage.error('请选择试卷分类');
    return;
  }
  if (selectedQuestions.value.length === 0) {
    ElMessage.error('试卷至少需要加入 1 道题目');
    return;
  }

  saving.value = true;
  const payload = {
    title: form.title,
    category_id: form.category_id,
    is_timed: form.is_timed,
    time_limit: form.time_limit,
    pass_percent: form.pass_percent,
    status: form.status,
    is_recommended: form.is_recommended,
    question_ids: selectedQuestions.value.map((q) => q.id)
  };

  try {
    if (editingId.value) {
      await request.put(`/api/v1/admin/exams/${editingId.value}`, payload);
      ElMessage.success('试卷及组卷已成功修改');
    } else {
      await request.post('/api/v1/admin/exams', payload);
      ElMessage.success('试卷及组卷已成功创建');
    }
    dialogVisible.value = false;
    loadExams();
  } finally {
    saving.value = false;
  }
};

const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除该试卷吗？仅草稿零作答可删除（有作答/已上架/已归档一律不可删），删除后不可恢复', '提示', { type: 'warning' }).then(async () => {
    await request.delete(`/api/v1/admin/exams/${id}`);
    ElMessage.success('删除成功');
    loadExams();
  });
};

onMounted(() => {
  loadCategories();
  loadExams();
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

.primary-btn {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  border: none;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.score-calc-tip {
  margin-top: 6px;
  background: #f0f9ff;
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid #bae6fd;
  color: #0369a1;
  font-size: 13px;
}

.selected-box {
  background: #f8fafc;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.box-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
}

.pool-box {
  margin-top: 16px;
  background: #fff;
  padding: 12px;
  border-radius: 12px;
  border: 1px dashed #cbd5e1;
}

.pool-filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pool-filters {
  display: flex;
  gap: 12px;
  align-items: center;
}

.stats-overview {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  text-align: center;
}

.stat-num {
  display: block;
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}
</style>
