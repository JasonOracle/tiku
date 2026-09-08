<!--
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Gemini 系列
 * 修改内容：[统一命题资料文案为「参考私有文库」: 明确说明与出题材料不相关时将智能脱钩避免张冠李戴，提升交互准确性与专业感]
 * 修改时间：2026-09-09
 * AI模型：Gemini 系列
 * 修改内容：[优化AI出题私有资料交互: 1. 将「参考教材/私有资料(RAG)」下拉多选移至出题材料正下方，极大提升发现率; 2. 增加 v-if="ragDocs.length" 条件渲染，无已解析文档时不予展示; 3. 从折叠的高级选项中剥离]
 * 修改时间：2026-09-08
 * AI模型：Gemini 系列
 * 修改内容：[✨AI出题界面极简化: 将「私有资料 (RAG)」移入高级选项折叠面板内，首屏主界面仅保留所属分类与出题材料，界面更加清爽不臃肿]
 * 修改时间：2026-09-06 22:30:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.5 AI出题体验: 单次生成上限10道(数量输入/后端双重限制)+顶部红色提示+材料指定数量优先 + 生成中全弹窗loading("AI生成中，请稍候") /
 *          v1.2 题海管理: 填空/简答题 / ✨AI出题(预览+二次确认入库) / 题目锁定防篡改 / 来源标签(AI生成)]
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
          <el-option label="填空题" value="fill" />
          <el-option label="简答题" value="short" />
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
        <el-button type="warning" plain class="ai-btn" @click="openAiDialog">✨ AI 出题</el-button>
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
      <el-table-column label="来源" width="90">
        <template #default="{ row }">
          <el-tag v-if="row.source === 'ai'" type="warning" size="small" effect="dark">AI生成</el-tag>
          <el-tag v-else type="info" size="small" effect="plain">人工</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="category_id" label="所属分类" width="110">
        <template #default="{ row }">
          <el-tag type="info" effect="plain">{{ getCategoryName(row.category_id) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="题干" min-width="220" show-overflow-tooltip />
      <el-table-column prop="score" label="默认分值" width="90">
        <template #default="{ row }">
          <span style="font-weight: 700; color: #0284c7">{{ row.score || 10 }} 分</span>
        </template>
      </el-table-column>
      <el-table-column label="锁定" width="70">
        <template #default="{ row }">
          <el-tooltip v-if="row.locked" content="已被上架/归档试卷引用，全局只读（可复制新题）">
            <span class="lock-icon">🔒</span>
          </el-tooltip>
          <span v-else style="color: #cbd5e1">—</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="270" fixed="right">
        <template #default="{ row }">
          <el-button v-if="(row.source_ref || []).length" type="success" text size="small" @click="openTrace(row)">引用溯源</el-button>
          <el-button v-if="row.locked" type="warning" text size="small" @click="handleCopy(row)">复制新题</el-button>
          <el-button v-else type="primary" text size="small" @click="openEditDialog(row)">编辑</el-button>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="640px" destroy-on-close>
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
            <el-option label="填空题" value="fill" />
            <el-option label="简答题" value="short" />
          </el-select>
        </el-form-item>
        <el-form-item label="题干" required>
          <el-input v-if="form.type === 'fill'" v-model="form.title" type="textarea" :rows="3"
                    placeholder="题干中用三个下划线 ___ 表示空位，如：中国的首都是___，简称___" />
          <el-input v-else v-model="form.title" type="textarea" :rows="3" placeholder="请输入题目详细描述..." />
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

        <!-- 客观题: 选项 -->
        <el-form-item v-if="isObjective" label="选项">
          <div v-for="(opt, idx) in form.options" :key="idx" class="option-row">
            <span class="opt-key">{{ opt.key }}.</span>
            <el-input v-model="opt.text" placeholder="选项描述" />
            <el-button type="danger" circle text @click="removeOption(idx)"><el-icon><Delete /></el-icon></el-button>
          </div>
          <el-button type="primary" text @click="addOption">+ 添加选项</el-button>
        </el-form-item>

        <!-- 客观题: 选项答案 -->
        <el-form-item v-if="isObjective" label="标准答案" required>
          <el-input v-model="answerStr" :placeholder="form.type === 'multiple' ? '多个答案用逗号分隔，如 A,B' : '如 A'" />
        </el-form-item>

        <!-- 填空题: 一空多答 -->
        <template v-if="form.type === 'fill'">
          <el-form-item label="空位校验">
            <el-tag :type="fillBlankCount === fillAnswers.length ? 'success' : 'danger'" size="small">
              题干 ___ 数量：{{ fillBlankCount }} 个 / 答案空数：{{ fillAnswers.length }} 个
              {{ fillBlankCount === fillAnswers.length && fillBlankCount > 0 ? '✓' : '（必须一致且大于0）' }}
            </el-tag>
          </el-form-item>
          <el-form-item v-for="(blank, bi) in fillAnswers" :key="bi" :label="`第${bi + 1}空答案`" required>
            <div style="width: 100%">
              <div v-for="(ans, ai) in blank" :key="ai" class="fill-answer-row">
                <el-input v-model="blank[ai]" placeholder="可接受答案（判卷忽略大小写与首尾空格）">
                  <template #append>
                    <el-button :disabled="blank.length <= 1" @click="blank.splice(ai, 1)">删</el-button>
                  </template>
                </el-input>
              </div>
              <el-button type="primary" text size="small" @click="blank.push('')">+ 该空的可接受答案</el-button>
              <el-button type="danger" text size="small" :disabled="fillAnswers.length <= 1" @click="fillAnswers.splice(bi, 1)">删除此空</el-button>
            </div>
          </el-form-item>
        </template>

        <!-- 简答题: 标准答案 + 踩分点 -->
        <template v-if="form.type === 'short'">
          <el-form-item label="标准答案" required>
            <el-input v-model="shortAnswer" type="textarea" :rows="3" placeholder="参考答案全文（供老师与 AI 批阅对照）" />
          </el-form-item>
          <el-form-item label="踩分点">
            <el-input v-model="gradingPointsStr" type="textarea" :rows="3"
                      placeholder="每行一个踩分点，AI 阅卷时按点给分。如：&#10;无状态协议&#10;基于TCP" />
          </el-form-item>
        </template>

        <el-form-item label="文字解析">
          <el-input v-model="form.explanation" type="textarea" :rows="2" placeholder="解析说明..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveQuestion">保存</el-button>
      </template>
    </el-dialog>

    <!-- ✨ AI 出题 Dialog -->
    <el-dialog v-model="aiDialogVisible" title="✨ AI 出题" width="760px" top="30px" destroy-on-close>
      <div v-loading="aiGenerating" element-loading-text="AI生成中，请稍候..."
           element-loading-background="rgba(255, 255, 255, 0.92)" class="ai-gen-body">
        <el-alert type="info" :closable="false" show-icon style="margin-bottom: 8px"
                  title="AI 生成带「AI生成」标签的题目，必须勾选预览确认后才会入库。支持一次生成多道题。默认难度中等、默认生成 5 题（材料中指定数量优先）。" />
        <div class="ai-limit-tip">⚠️ 单次最多生成 10 道题：材料或高级选项中要求超过 10 道时，将只按 10 道生成；如需更多请分批生成，避免等待过久。</div>
        <div class="form-row" style="display: flex; gap: 16px;">
          <div class="form-item" style="flex: 1;">
            <label class="form-label required">所属分类</label>
            <el-select v-model="aiForm.category_id" placeholder="请选择归属分类" style="width: 100%">
              <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </div>
        </div>

        <div class="form-item">
          <label class="form-label required">出题材料</label>
          <el-input v-model="aiForm.material" type="textarea" :rows="4"
                    placeholder="粘贴一段材料文本，或直接描述需求。例如：生成5道关于Python并发编程的题目，带详细解析" />
        </div>

        <!-- 私有文库（RAG，选填多选）：仅当存在已解析完成的文档时呈现，紧跟出题材料下方 -->
        <div v-if="ragDocs.length" class="form-item">
          <label class="form-label">参考私有文库（选填）</label>
          <el-select v-model="aiForm.docIds" multiple collapse-tags collapse-tags-tooltip clearable
                     placeholder="可多选：勾选后 AI 优先依据所选私有文库出题并自动溯源（留空则依据出题材料/通用题库）" style="width: 100%">
            <el-option v-for="d in ragDocs" :key="d.id" :label="`${d.filename}（${d.total_chunks}块）`" :value="d.id" />
          </el-select>
          <div class="field-tip">已检测到您在私有文库上传的资料；若所选文档与出题材料不相关，系统将自动脱钩并以通识出题，避免张冠李戴</div>
        </div>

        <!-- 高级选项: 默认收起, 提示放在标题右侧 -->
        <el-collapse v-model="advancedOpen" class="adv-collapse">
          <el-collapse-item name="adv">
            <template #title>
              <span class="adv-title">高级选项（选填）</span>
              <span class="adv-tip">自定义题型、题目数量与难度；与材料描述冲突时以此为准</span>
            </template>
            <div class="adv-body">
              <div class="form-item">
                <label class="form-label">题目难度</label>
                <el-radio-group v-model="aiForm.difficulty" @change="markAdvancedTouched">
                  <el-radio label="easy">简单</el-radio>
                  <el-radio label="medium">中等</el-radio>
                  <el-radio label="hard">困难</el-radio>
                </el-radio-group>
              </div>
              <div class="form-item">
                <label class="form-label">题型</label>
                <el-checkbox-group v-model="aiForm.types" @change="markAdvancedTouched">
                  <el-checkbox value="single">单选</el-checkbox>
                  <el-checkbox value="multiple">多选</el-checkbox>
                  <el-checkbox value="judge">判断</el-checkbox>
                  <el-checkbox value="fill">填空</el-checkbox>
                  <el-checkbox value="short">简答</el-checkbox>
                </el-checkbox-group>
                <div class="field-tip">可勾选多种题型混合出题；不勾选则由 AI 根据材料自主决定题型</div>
              </div>
              <div class="form-item">
                <label class="form-label">题目数量</label>
                <el-input-number v-model="aiForm.count" :min="1" :max="10" controls-position="right"
                                 placeholder="默认 5，最多 10" style="width: 200px" @change="markAdvancedTouched" />
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>

        <!-- 预览区 -->
        <div v-if="aiPreview.length" class="ai-preview">
          <el-divider content-position="left"><strong>生成结果预览（勾选后入库）</strong></el-divider>
          <el-table :data="aiPreview" size="small" @selection-change="aiSelected = $event" max-height="320">
            <el-table-column type="selection" width="45" />
            <el-table-column prop="type" label="题型" width="80">
              <template #default="{ row }">
                <el-tag size="small" :type="getTypeTag(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="题干" min-width="200" show-overflow-tooltip />
            <el-table-column label="答案" min-width="140" show-overflow-tooltip>
              <template #default="{ row }">
                {{ formatAnswer(row) }}
              </template>
            </el-table-column>
            <el-table-column prop="explanation" label="解析" min-width="140" show-overflow-tooltip />
          </el-table>
        </div>
      </div>

      <template #footer>
        <el-button @click="aiDialogVisible = false">关闭</el-button>
        <el-button v-if="!aiPreview.length" type="warning" :loading="aiGenerating" @click="generateQuestions">
          {{ aiGenerating ? 'AI 生成中...' : '生成题目' }}
        </el-button>
        <el-button v-else type="primary" :loading="aiImporting" :disabled="aiSelected.length === 0"
                   @click="confirmImport">
          确认入库 ({{ aiSelected.length }})
        </el-button>
      </template>
    </el-dialog>

    <!-- v1.3: RAG 引用溯源抽屉 -->
    <TraceDrawer
      :visible="traceVisible"
      :question="traceQuestion"
      @update:visible="traceVisible = $event"
    />

    <!-- Excel 批量导入 Dialog -->
      <el-dialog v-model="importDialogVisible" title="批量导入题目" width="520px">
      <div style="margin-bottom: 12px; color: #64748b; font-size: 13px">
        分类按 Excel “分类”列逐题归入（不存在自动新建，留空归第一个分类）。<br />
        填空题答案格式：<code>北京,北京市|是</code>（逗号=一空多答，竖线=分空）；简答题“答案”列为标准答案，可选“踩分点”列用分号分隔。
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
import TraceDrawer from './components/TraceDrawer.vue';

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
  ] as Array<{ key: string; text: string }>,
  answer: ['A'] as any[],
  grading_points: [] as string[],
  explanation: ''
});

// 填空题编辑态: 每空一个可接受答案数组
const fillAnswers = ref<string[][]>([['']]);
const shortAnswer = ref('');
const gradingPointsStr = ref('');

const isObjective = computed(() => ['single', 'multiple', 'judge'].includes(form.type));
const fillBlankCount = computed(() => (form.title.match(/___/g) || []).length);

const answerStr = computed({
  get: () => form.answer.join(','),
  set: (val: string) => {
    if (form.type === 'multiple') {
      // 连写兼容: "ABC" / "A,B" / "a b c" → 拆成单字母数组
      form.answer = (val.toUpperCase().match(/[A-F]/g) || []);
    } else {
      form.answer = val.split(',').map((s: string) => s.trim().toUpperCase()).filter(Boolean);
    }
  }
});

// ---- ✨ AI 出题 (v1.4: 高级选项默认收起, 任一填写则需完整; 与材料冲突时以高级选项为准) ----
const aiDialogVisible = ref(false);
const aiGenerating = ref(false);
const aiImporting = ref(false);
const advancedOpen = ref<string[]>([]);
const advancedTouched = ref(false);
const markAdvancedTouched = () => {
  advancedTouched.value = true;
};
const aiForm = reactive({
  category_id: undefined as number | undefined,
  material: '',
  types: [] as string[],
  count: 5 as number | undefined,
  difficulty: 'medium',
  docIds: [] as number[]
});
const aiPreview = ref<any[]>([]);
const aiSelected = ref<any[]>([]);
const ragDocs = ref<any[]>([]);

const loadRagDocs = async () => {
  try {
    const res: any = await request.get('/api/v1/admin/rag/documents');
    ragDocs.value = (res.items || []).filter((d: any) => d.status === 'done');
  } catch (e) {
    ragDocs.value = [];
  }
};

const openAiDialog = () => {
  if (!checkCategoryPrerequisite()) return;
  aiPreview.value = [];
  aiSelected.value = [];
  aiForm.category_id = firstCategoryId();
  aiForm.material = '';
  aiForm.types = [];
  aiForm.count = 5;
  aiForm.difficulty = 'medium';
  aiForm.docIds = [];
  advancedTouched.value = false;
  advancedOpen.value = [];
  loadRagDocs();
  aiDialogVisible.value = true;
};

const formatAnswer = (row: any) => {
  if (row.type === 'fill') return (row.answer || []).map((b: any) => (Array.isArray(b) ? b.join('/') : b)).join(' | ');
  if (row.type === 'short') return (row.answer || [])[0] || '';
  return (row.answer || []).join(', ');
};

const generateQuestions = async () => {
  if (!aiForm.category_id) {
    ElMessage.error('请选择所属分类');
    return;
  }
  if (!aiForm.material.trim()) {
    ElMessage.error('请填写出题材料或需求描述');
    return;
  }
  // 高级选项未动过则三项全空（后端自主：材料数量优先，默认 5 道/中等）；
  // 动过则必须三项齐全，否则后端 400
  const useAdvanced = advancedTouched.value;
  if (useAdvanced) {
    if (!aiForm.types.length) {
      ElMessage.error('已启用高级选项，请至少勾选一种题型');
      return;
    }
    if (aiForm.count == null) {
      ElMessage.error('已启用高级选项，请填写题目数量');
      return;
    }
    if (!aiForm.difficulty) {
      ElMessage.error('已启用高级选项，请选择题目难度');
      return;
    }
  }
  aiGenerating.value = true;
  try {
    const res: any = await request.post('/api/v1/admin/ai/questions/generate', {
      material: aiForm.material,
      types: useAdvanced ? aiForm.types : undefined,
      count: useAdvanced ? aiForm.count : undefined,
      difficulty: useAdvanced ? aiForm.difficulty : undefined,
      doc_ids: aiForm.docIds.length ? aiForm.docIds : undefined,
      category_id: aiForm.category_id
    }, { timeout: 120000 }); // 真实大模型出题较慢, 覆盖全局 10s 超时
    aiPreview.value = res.questions || [];
    aiSelected.value = [];
    ElMessage.success(res.message || 'AI 已生成，请预览勾选后入库');
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    aiGenerating.value = false;
  }
};

const confirmImport = async () => {
  if (!aiForm.category_id) {
    ElMessage.error('请选择所属分类');
    return;
  }
  aiImporting.value = true;
  try {
    const payload = aiSelected.value.map((q) => ({ ...q, category_id: aiForm.category_id, source: 'ai' }));
    const res: any = await request.post('/api/v1/admin/questions/batch', payload);
    ElMessage.success(res.message || '入库成功');
    aiDialogVisible.value = false;
    loadQuestions();
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    aiImporting.value = false;
  }
};

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
  if (type === 'fill') return 'success';
  if (type === 'short') return 'danger';
  return 'info';
};

const getTypeLabel = (type: string) => {
  if (type === 'single') return '单选题';
  if (type === 'multiple') return '多选题';
  if (type === 'fill') return '填空题';
  if (type === 'short') return '简答题';
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
  form.grading_points = [];
  form.explanation = '';
  fillAnswers.value = [['']];
  shortAnswer.value = '';
  gradingPointsStr.value = '';
  dialogVisible.value = true;
};

const openEditDialog = (row: any) => {
  if (row.locked) {
    ElMessage.warning('该题目已被上架/归档试卷引用锁定为只读，请使用「复制新题」');
    return;
  }
  editingId.value = row.id;
  form.type = row.type;
  form.title = row.title;
  form.score = row.score || 10;
  form.difficulty = row.difficulty || 'medium';
  form.category_id = row.category_id || firstCategoryId();
  form.options = row.options || [];
  form.answer = row.answer || [];
  form.grading_points = row.grading_points || [];
  form.explanation = row.explanation || '';
  // 题型相关编辑态
  if (row.type === 'fill') {
    fillAnswers.value = (row.answer || [['']]).map((blank: any) =>
      Array.isArray(blank) ? [...blank] : [String(blank)]
    );
  }
  if (row.type === 'short') {
    shortAnswer.value = (row.answer || [''])[0] || '';
    gradingPointsStr.value = (row.grading_points || []).join('\n');
  }
  dialogVisible.value = true;
};

// 锁定题目的唯一修改路径: 复制产生新题
const handleCopy = async (row: any) => {
  const res: any = await request.post(`/api/v1/admin/questions/${row.id}/copy`);
  ElMessage.success('已复制为新题，可编辑副本');
  loadQuestions();
  if (res?.id) {
    // 打开副本编辑
    openEditDialog({ ...res, locked: false, options: res.options || [], answer: res.answer || [] });
  }
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

  const payload: any = { ...form };
  if (form.type === 'fill') {
    if (fillBlankCount.value !== fillAnswers.value.length) {
      ElMessage.error(`题干 ___ 数量(${fillBlankCount.value})必须与答案空数(${fillAnswers.value.length})一致`);
      return;
    }
    payload.answer = fillAnswers.value.map((blank) => blank.map((a) => a.trim()).filter(Boolean));
    if (payload.answer.some((blank: string[]) => blank.length === 0)) {
      ElMessage.error('每个空至少需要一个可接受答案');
      return;
    }
    payload.options = [];
    payload.grading_points = [];
  } else if (form.type === 'short') {
    if (!shortAnswer.value.trim()) {
      ElMessage.error('简答题必须填写标准答案');
      return;
    }
    payload.answer = [shortAnswer.value];
    payload.grading_points = gradingPointsStr.value.split('\n').map((s) => s.trim()).filter(Boolean);
    payload.options = [];
  } else {
    payload.grading_points = [];
  }

  if (editingId.value) {
    await request.put(`/api/v1/admin/questions/${editingId.value}`, payload);
    ElMessage.success('题目已修改');
  } else {
    await request.post('/api/v1/admin/questions', payload);
    ElMessage.success('题目已创建');
  }
  dialogVisible.value = false;
  loadQuestions();
};

// v1.3: RAG 引用溯源
const traceVisible = ref(false);
const traceQuestion = ref<any>(null);

const openTrace = (row: any) => {
  traceQuestion.value = row;
  traceVisible.value = true;
};

const handleDelete = (id: number) => {  ElMessageBox.confirm('删除后题目将从题库隐藏，但已被试卷引用的原题仍可正常使用（防牵连软删除）。确定删除吗？', '提示', { type: 'warning' }).then(async () => {
    await request.delete(`/api/v1/admin/questions/${id}`);
    ElMessage.success('已删除');
    loadQuestions();
  });
};

const handleBatchDelete = () => {
  if (selectedQuestionIds.value.length === 0) return;
  ElMessageBox.confirm(`确定要批量删除已选中的 ${selectedQuestionIds.value.length} 道题目吗？删除后题库隐藏，已引用试卷不受影响。`, '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    let successCount = 0;
    for (const qId of selectedQuestionIds.value) {
      try {
        await request.delete(`/api/v1/admin/questions/${qId}`);
        successCount++;
      } catch (e) {
        /* 拦截器已提示 */
      }
    }
    ElMessage.success(`已删除 ${successCount} 道题目`);
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
    ElMessage.success(`成功导入 ${res.imported_count} 道题目${skipped ? `，跳过 ${skipped} 行无法解析的题目` : ''}`);
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

.fill-answer-row {
  margin-bottom: 6px;
}

.lock-icon {
  font-size: 16px;
}

.ai-preview {
  margin-top: 8px;
}

.ai-btn {
  color: #7c3aed;
  border-color: #c4b5fd;
}

.ai-btn:hover {
  color: #6d28d9;
  border-color: #a78bfa;
  background: #f5f3ff;
}

/* AI 出题弹窗: 顶部红色上限提示 (v1.5) */
.ai-limit-tip {
  color: #f56c6c;
  font-size: 13px;
  line-height: 1.6;
  font-weight: 600;
  margin: 0 0 12px;
}

/* AI 出题弹窗: 高级选项 */
.adv-collapse {
  border: none;
  margin-top: 4px;
}

.adv-collapse :deep(.el-collapse-item__header) {
  background: #faf5ff;
  border-radius: 8px;
  padding: 0 12px;
  height: 40px;
}

.adv-collapse :deep(.el-collapse-item__wrap) {
  border: none;
}

.adv-collapse :deep(.el-collapse-item__content) {
  padding: 12px 4px 0;
}

.adv-title {
  font-weight: 700;
  color: #6d28d9;
  font-size: 13px;
}

.adv-tip {
  margin-left: 12px;
  font-size: 12px;
  color: #94a3b8;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.adv-body {
  background: #faf5ff;
  border-radius: 8px;
  padding: 12px 16px;
}

.form-item {
  margin-bottom: 14px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: #334155;
  margin-bottom: 6px;
}

.form-label.required::before {
  content: '* ';
  color: #e11d48;
}

.field-tip {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.adv-row {
  display: flex;
  gap: 24px;
}

.adv-row .grow {
  flex: 1;
}
</style>
