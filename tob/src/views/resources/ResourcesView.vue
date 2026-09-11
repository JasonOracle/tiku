<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[治本解决来源列文字截断问题：1. 将来源列宽度锁定为充足的 width="120"，表头与内容单元格内边距统一收紧至 10px；2. 将容易产生字体/渲染字宽不可控的 emoji 图标替换为精致矢量 SVG 火花图标(ai-sparkle-svg)与 inline-flex 精确排版；3. 操作列继续固定在最右侧(fixed="right")，彻底杜绝文字压缩与省略号截断]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[响应用户需求：彻底移除题目创建、编辑以及AI生成等全场景下的「踩分点」与「文字解析」输入/展示，仅保留各题型的标准答案作为判卷与核验基准]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[1. 彻底修复点击编辑题目时控制台报 TypeError: (e.answer || [[""]]).map is not a function 异常：强化 openEditDialog 防御性类型转换，对字符串或畸形 answer 进行 JSON/数组安全解析；2. 移除简答题冗余的「踩分点」表单输入项，统一判卷标准答案与文字解析模式]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 底层
 * 修改内容：[1. 重构 AI 创建题目预览区：引入 ResourcePreview 题目全貌展示，完整渲染题型、分值、结构化选项、正确答案绿色高亮与答案解析; 2. 增加批量全选与单题勾选，彻底解决只显示题干简略信息、缺失选项和解析的问题]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[对齐现代企业级SaaS列表高质感风格：1. 消除页面与表格硬边框，外层赋以高定悬浮多层立体弥散阴影(Elevated Island Box-Shadow)；2. 仅首行表头赋予清爽淡蓝灰底色(#f1f5f9)与微划线，杜绝字形压缩折行；3. 升级题型胶囊(不同题型低饱和度色彩体系)、来源胶囊(AI紫粉/人工灰)与分类胶囊；4. 操作列改为轻盈彩色无背景链接组(溯源/复制/编辑/删除)]
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[题目管理筛选栏升级：搜索条目关键词改为搜索题目标题，全部分类改为试卷分类，全部分型改为全部题型；增加检索按钮并改为点击后触发请求，增加重置图标按钮]
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗：全量通用化词汇映射，旧教育词汇已删除]
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Gemini 系列
 * 修改内容：[统一命题资料文案为「参考私有文库」: 明确说明与创建材料不相关时将智能脱钩避免张冠李戴，提升交互准确性与专业感]
 * 修改时间：2026-09-09
 * AI模型：Gemini 系列
 * 修改内容：[优化AI创建私有资料交互: 1. 将「参考教材/私有资料(RAG)」下拉多选移至创建材料正下方，极大提升发现率; 2. 增加 v-if="ragDocs.length" 条件渲染，无已解析文档时不予展示; 3. 从折叠的高级选项中剥离]
 * 修改时间：2026-09-08
 * AI模型：Gemini 系列
 * 修改内容：[✨AI创建界面极简化: 将「私有资料 (RAG)」移入高级选项折叠面板内，首屏主界面仅保留所属分类与创建材料，界面更加清爽不臃肿]
 * 修改时间：2026-09-06 22:30:00
 * AI模型：ZCode (GLM)
 * 修改内容：[AI创建体验: 单次生成上限10道(数量输入/后端双重限制)+顶部红色提示+材料指定数量优先 + 生成中全弹窗loading("AI生成中，请稍候") /
 *          v1.2 题海管理: 填空/简答题 / ✨AI创建(预览+二次确认入库) / 条目锁定防篡改 / 来源标签(AI生成)]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="filters">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索条目关键词、题干..."
          clearable
          class="custom-search-input"
          style="width: 240px"
          @change="loadQuestions"
        >
          <template #prefix>
            <el-icon class="search-prefix-icon"><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="filters.category_id"
          placeholder="全部分类"
          clearable
          class="custom-filter-select"
          style="width: 160px"
          @change="loadQuestions"
        >
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select
          v-model="filters.type"
          placeholder="全部题型"
          clearable
          class="custom-filter-select"
          style="width: 140px"
          @change="loadQuestions"
        >
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
          class="batch-del-btn"
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon> 批量删除 ({{ selectedQuestionIds.length }})
        </el-button>
        <el-button type="warning" plain class="ai-btn" @click="openAiDialog">✨ AI 创建</el-button>
        <el-button type="primary" class="primary-create-btn" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> 新建题目
        </el-button>
        <el-button type="success" plain class="import-btn" @click="openImportDialog">
          <el-icon><Upload /></el-icon> Excel 导入
        </el-button>
      </div>
    </div>

    <!-- 条目数据表格 (无硬边框，仅首行背景与微划线，右侧操作列固定，支持横向弹性滚动) -->
    <el-table
      :data="questions"
      v-loading="loading"
      class="saas-modern-table"
      style="width: 100%"
      :header-cell-style="{
        backgroundColor: '#f1f5f9',
        color: '#475569',
        fontWeight: '700',
        fontSize: '13px',
        padding: '12px 10px',
        borderBottom: '1px solid #e2e8f0',
        borderTop: 'none',
        borderRight: 'none',
        borderLeft: 'none',
        whiteSpace: 'nowrap'
      }"
      :cell-style="{
        padding: '14px 10px',
        borderBottom: '1px solid #f1f5f9',
        borderRight: 'none',
        borderLeft: 'none'
      }"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column prop="id" label="ID" width="80" align="center">
        <template #default="{ row }">
          <span class="col-id-text">{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="题型" min-width="100" align="center">
        <template #default="{ row }">
          <span class="type-pill" :class="row.type">
            {{ getTypeLabel(row.type) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="来源" width="120" align="center">
        <template #default="{ row }">
          <span v-if="row.source === 'ai'" class="source-ai-pill">
            <svg class="ai-sparkle-svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L13.8 8.2L20 10L13.8 11.8L12 18L10.2 11.8L4 10L10.2 8.2L12 2Z" />
            </svg>
            AI生成
          </span>
          <span v-else class="source-manual-pill">人工录入</span>
        </template>
      </el-table-column>
      <el-table-column prop="category_id" label="所属分类" min-width="130" align="center">
        <template #default="{ row }">
          <span class="category-pill">
            {{ getCategoryName(row.category_id) || '未分类' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="题干描述" min-width="320" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="question-main-title">{{ row.title }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="score" label="默认分值" min-width="100" align="center">
        <template #default="{ row }">
          <span class="score-highlight">{{ row.score || 10 }} 分</span>
        </template>
      </el-table-column>
      <el-table-column label="锁定" width="75" align="center">
        <template #default="{ row }">
          <el-tooltip v-if="row.locked" content="已被上架/归档任务引用，全局只读（可复制新题）">
            <span class="lock-icon" title="锁定中">🔒</span>
          </el-tooltip>
          <span v-else class="muted-gray-text">—</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" align="center" fixed="right">
        <template #default="{ row }">
          <div class="action-btn-group">
            <el-button v-if="(row.ai_rag_sources || []).length" type="success" link class="action-link-btn green" @click="openTrace(row)">溯源</el-button>
            <el-button v-if="row.locked" type="warning" link class="action-link-btn orange" @click="handleCopy(row)">复制</el-button>
            <el-button v-else type="primary" link class="action-link-btn" @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" link class="action-link-btn red" @click="handleDelete(row.id)">删除</el-button>
          </div>
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
          <el-select v-model="form.category_id" placeholder="请选择资源分类（必填）" style="width: 100%">
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
          <el-input v-else v-model="form.title" type="textarea" :rows="3" placeholder="请输入条目详细描述..." />
        </el-form-item>
        <el-form-item label="默认分数" required>
          <el-input-number v-model="form.score" :min="1" :max="100" style="width: 160px" />
          <span style="margin-left: 8px; color: #64748b; font-size: 12px">编排时将自动累加为任务总分</span>
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

        <!-- 简答题: 标准答案 -->
        <template v-if="form.type === 'short'">
          <el-form-item label="标准答案" required>
            <el-input v-model="shortAnswer" type="textarea" :rows="3" placeholder="参考答案全文（供判卷与核验对照）" />
          </el-form-item>
        </template>

        <!-- 答案解析: 全题型通用（选填），C端成绩报告与阅卷大厅均会展示 -->
        <el-form-item label="答案解析">
          <el-input
            v-model="form.explanation"
            type="textarea"
            :rows="3"
            placeholder="选填。简要说明正确答案依据、易错点或采分要点（50-150 字）。保存后 C 端成绩报告与阅卷大厅可见"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveQuestion">保存</el-button>
      </template>
    </el-dialog>

    <!-- ✨ AI 创建 Dialog -->
    <el-dialog v-model="aiDialogVisible" title="✨ AI创建题目" width="760px" top="30px" destroy-on-close>
      <div v-loading="aiGenerating" element-loading-text="AI生成中，请稍候..."
           element-loading-background="rgba(255, 255, 255, 0.92)" class="ai-gen-body">
        <el-alert type="info" :closable="false" show-icon style="margin-bottom: 8px"
                  title="AI 生成带「AI生成」标签的题目，必须勾选预览确认后才会入库。支持一次生成多道题。默认难度中等、默认生成 10 题（材料中指定数量优先）。" />
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
          <label class="form-label required">创建材料</label>
          <el-input v-model="aiForm.material" type="textarea" :rows="4"
                    placeholder="粘贴一段材料文本，或直接描述需求。例如：生成5道关于Python并发编程的条目，带详细解析" />
        </div>

        <!-- 高级选项: 默认收起, 提示放在标题右侧 -->
        <el-collapse v-model="advancedOpen" class="adv-collapse">
          <el-collapse-item name="adv">
            <template #title>
              <span class="adv-title">高级选项（选填）</span>
              <span class="adv-tip">自定义题型、题目数量与难度；与材料描述冲突时以此为准</span>
            </template>
            <div class="adv-body">
              <div v-if="ragDocs.length" class="form-item">
                <label class="form-label">参考私有文库（选填）</label>
                <el-select v-model="aiForm.docIds" multiple collapse-tags collapse-tags-tooltip clearable
                           placeholder="可多选：勾选后 AI 优先依据所选私有文库创建并自动溯源（留空则依据创建材料/通用资源库）" style="width: 100%">
                  <el-option v-for="d in ragDocs" :key="d.id" :label="`${d.filename}（${d.total_chunks}块）`" :value="d.id" />
                </el-select>
                <div class="field-tip">已检测到您在私有文库上传的资料；若所选文档与创建材料不相关，系统将自动脱钩并以通识创建，避免张冠李戴</div>
              </div>
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
                <div class="field-tip">可勾选多种题型混合创建；不勾选则由 AI 根据材料自主决定题型</div>
              </div>
              <div class="form-item">
                <label class="form-label">题目数量</label>
                <el-input-number v-model="aiForm.count" :min="1" :max="10" controls-position="right"
                                 placeholder="默认 5，最多 10" style="width: 200px" @change="markAdvancedTouched" />
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>

        <!-- 预览区 (完整展示题干、题型、选项高亮与答案解析) -->
        <div v-if="aiPreview.length" class="ai-preview-section">
          <div class="ai-preview-toolbar">
            <div class="tb-left">
              <el-checkbox
                :model-value="isAllAiSelected"
                :indeterminate="isAiIndeterminate"
                @change="toggleSelectAllAi"
              >
                全选所有生成题目 (已选 {{ aiSelected.length }} / {{ aiPreview.length }})
              </el-checkbox>
            </div>
            <div class="tb-right">
              <span class="preview-tip">请核对题干、选项与正确答案后勾选入库</span>
            </div>
          </div>

          <div class="ai-preview-cards-list">
            <div
              v-for="(q, idx) in aiPreview"
              :key="idx"
              class="ai-q-card"
              :class="{ 'is-checked': isAiItemChecked(idx) }"
              @click="toggleAiItemCheck(idx)"
            >
              <div class="ai-q-header">
                <el-checkbox
                  :model-value="isAiItemChecked(idx)"
                  @click.stop
                  @change="toggleAiItemCheck(idx)"
                />
                <span class="ai-q-seq">第 {{ idx + 1 }} 题</span>
                <el-tag size="small" :type="getTypeTag(q.type)">{{ getTypeLabel(q.type) }}</el-tag>
                <span class="ai-q-score">{{ q.score || 10 }} 分</span>
              </div>
              <div class="ai-q-title">{{ q.title }}</div>
              <!-- 嵌入试题核心结构化预览（选项高亮、正确答案、解析） -->
              <ResourcePreview :resource="q" />
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="aiDialogVisible = false">关闭</el-button>
        <el-button v-if="!aiPreview.length" type="warning" :loading="aiGenerating" @click="generateQuestions">
          {{ aiGenerating ? 'AI 生成中...' : '生成题目' }}
        </el-button>
        <el-button v-else type="primary" :loading="aiImporting" :disabled="aiSelected.length === 0"
                   @click="confirmImport">
          确认勾选入库 ({{ aiSelected.length }})
        </el-button>
      </template>
    </el-dialog>

    <!-- v1.3: RAG 引用溯源抽屉 -->
    <TraceDrawer
      :visible="traceVisible"
      :resource="traceQuestion"
      @update:visible="traceVisible = $event"
    />

    <!-- Excel 批量导入 Dialog -->
      <el-dialog v-model="importDialogVisible" title="批量导入条目" width="520px">
      <div style="margin-bottom: 12px; color: #64748b; font-size: 13px">
        分类按 Excel “分类”列逐题归入（不存在自动新建，留空归第一个分类）。<br />
        填空题答案格式：<code>北京,北京市|是</code>（逗号=一空多答，竖线=分空）；简答题“答案”列为极简标准答案全文。
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
import { Plus, Upload, Delete, UploadFilled, Search, RefreshRight } from '@element-plus/icons-vue';
import request from '../../utils/request';
import TraceDrawer from './components/TraceDrawer.vue';
import ResourcePreview from '../tasks/components/ResourcePreview.vue';

import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(false);
const questions = ref<any[]>([]);
const categories = ref<any[]>([]);
const filters = reactive({ keyword: '', type: '', category_id: null as number | null });

const handleSearch = () => {
  pagination.page = 1;
  loadQuestions();
};

const handleReset = () => {
  filters.keyword = '';
  filters.type = '';
  filters.category_id = null;
  pagination.page = 1;
  loadQuestions();
};
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
    ElMessageBox.confirm('当前暂无任何“资源分类”，无法新建或导入条目。请先去新建资源分类。', '无法进行此操作', {
      confirmButtonText: '去新建资源分类',
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

// ---- ✨ AI 创建 (高级选项默认收起, 任一填写则需完整; 与材料冲突时以高级选项为准) ----
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
  count: 10 as number | undefined,
  difficulty: 'medium',
  docIds: [] as number[]
});
const aiPreview = ref<any[]>([]);
const aiSelected = ref<any[]>([]);
const ragDocs = ref<any[]>([]);

const loadRagDocs = async () => {
  try {
    const res: any = await request.get('/api/v1/admin/kb/documents');
    ragDocs.value = (res.items || []).map((d: any) => ({ ...d, filename: d.file_name, status: d.scope === 'public' ? 'done' : 'done' }));
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
  aiForm.count = 10;
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
    ElMessage.error('请填写创建材料或需求描述');
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
      count: aiForm.count ?? 10,
      difficulty: useAdvanced ? aiForm.difficulty : undefined,
      doc_ids: aiForm.docIds.length ? aiForm.docIds : undefined,
      category_id: aiForm.category_id
    }, { timeout: 120000 }); // 真实大模型创建较慢, 覆盖全局 10s 超时
    aiPreview.value = res.questions || [];
    // 默认全选所有生成的高质量条目，方便用户直接一键入库或自由取消勾选
    aiSelected.value = [...(res.questions || [])];
    ElMessage.success(res.message || 'AI 已生成，请预览勾选后入库');
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    aiGenerating.value = false;
  }
};

const isAiItemChecked = (index: number) => {
  const item = aiPreview.value[index];
  return item && aiSelected.value.includes(item);
};

const toggleAiItemCheck = (index: number) => {
  const item = aiPreview.value[index];
  if (!item) return;
  const idx = aiSelected.value.indexOf(item);
  if (idx >= 0) {
    aiSelected.value.splice(idx, 1);
  } else {
    aiSelected.value.push(item);
  }
};

const isAllAiSelected = computed(() => {
  return aiPreview.value.length > 0 && aiSelected.value.length === aiPreview.value.length;
});

const isAiIndeterminate = computed(() => {
  return aiSelected.value.length > 0 && aiSelected.value.length < aiPreview.value.length;
});

const toggleSelectAllAi = (val: any) => {
  if (val) {
    aiSelected.value = [...aiPreview.value];
  } else {
    aiSelected.value = [];
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
    const res: any = await request.post('/api/v1/admin/resources/batch', payload);
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
      params: { target_type: 'resource' }
    });
    categories.value = res.items || [];
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
    const res: any = await request.get('/api/v1/admin/resources', {
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
    ElMessage.warning('该条目已被上架/归档任务引用锁定为只读，请使用「复制新题」');
    return;
  }
  editingId.value = row.id;
  form.type = row.type;
  form.title = row.title;
  form.score = row.score || 10;
  form.difficulty = row.difficulty || 'medium';
  form.category_id = row.category_id || firstCategoryId();
  form.options = row.options || [];
  // 规范化 answer 为数组，防御字符串或 null 异常
  let rawAnswer = row.answer;
  if (typeof rawAnswer === 'string') {
    try {
      rawAnswer = JSON.parse(rawAnswer);
    } catch {
      rawAnswer = rawAnswer ? [rawAnswer] : [];
    }
  }
  if (!Array.isArray(rawAnswer)) {
    rawAnswer = rawAnswer ? [rawAnswer] : [];
  }
  form.answer = rawAnswer;
  form.explanation = row.explanation || '';

  // 题型相关编辑态
  if (row.type === 'fill') {
    fillAnswers.value = rawAnswer.length > 0
      ? rawAnswer.map((blank: any) => (Array.isArray(blank) ? [...blank] : [String(blank ?? '')]))
      : [['']];
  }
  if (row.type === 'short') {
    shortAnswer.value = rawAnswer[0] || '';
    gradingPointsStr.value = (row.grading_points || []).join('\n');
  }
  dialogVisible.value = true;
};

// 锁定条目的唯一修改路径: 复制产生新题
const handleCopy = async (row: any) => {
  const res: any = await request.post(`/api/v1/admin/resources/${row.id}/copy`);
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
    payload.answer = [shortAnswer.value.trim()];
    payload.grading_points = [];
    payload.options = [];
  } else {
    payload.grading_points = [];
  }
  // 答案解析：全题型通用，留空则后端落库为 null
  payload.explanation = (form.explanation || '').trim() || undefined;

  if (editingId.value) {
    await request.put(`/api/v1/admin/resources/${editingId.value}`, payload);
    ElMessage.success('条目已修改');
  } else {
    await request.post('/api/v1/admin/resources', payload);
    ElMessage.success('条目已创建');
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

const handleDelete = (id: number) => {  ElMessageBox.confirm('删除后条目将从资源库隐藏，但已被任务引用的原题仍可正常使用（防牵连软删除）。确定删除吗？', '提示', { type: 'warning' }).then(async () => {
    await request.delete(`/api/v1/admin/resources/${id}`);
    ElMessage.success('已删除');
    loadQuestions();
  });
};

const handleBatchDelete = () => {
  if (selectedQuestionIds.value.length === 0) return;
  ElMessageBox.confirm(`确定要批量删除已选中的 ${selectedQuestionIds.value.length} 道条目吗？删除后资源库隐藏，已引用任务不受影响。`, '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    let successCount = 0;
    for (const qId of selectedQuestionIds.value) {
      try {
        await request.delete(`/api/v1/admin/resources/${qId}`);
        successCount++;
      } catch (e) {
        /* 拦截器已提示 */
      }
    }
    ElMessage.success(`已删除 ${successCount} 道条目`);
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
    const res: any = await request.post('/api/v1/admin/resources/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    const skipped = res.skipped_count || 0;
    ElMessage.success(`成功导入 ${res.imported_count} 道条目${skipped ? `，跳过 ${skipped} 行无法解析的条目` : ''}`);
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
  background: #ffffff;
  border-radius: 18px;
  padding: 24px 28px;
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.05), 0 20px 25px -5px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.03);
  border: none;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.filters {
  display: flex;
  gap: 14px;
  align-items: center;
}

.actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 高定圆角输入框与选择器 */
.custom-search-input :deep(.el-input__wrapper),
.custom-filter-select :deep(.el-select__wrapper) {
  border-radius: 10px !important;
  background-color: #ffffff !important;
  box-shadow: 0 0 0 1px #e2e8f0 inset !important;
  transition: all 0.2s ease !important;
  padding: 5px 14px !important;
}

.custom-search-input :deep(.el-input__wrapper.is-focus),
.custom-filter-select :deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 2px #1d4ed8 inset !important;
}

.search-prefix-icon {
  color: #94a3b8;
  font-size: 15px;
}

/* 顶部深蓝主创建按钮与操作按钮群 */
.primary-create-btn {
  background: #1d4ed8 !important;
  border-color: #1d4ed8 !important;
  color: #ffffff !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
  padding: 10px 20px !important;
  box-shadow: 0 2px 8px rgba(29, 78, 216, 0.25) !important;
  transition: all 0.2s ease !important;
}

.primary-create-btn:hover {
  background: #1e40af !important;
  border-color: #1e40af !important;
  transform: translateY(-1px);
}

.ai-btn, .import-btn, .batch-del-btn {
  border-radius: 10px !important;
  font-weight: 600 !important;
}

/* ─────────── 现代高质感 SaaS 列表样式体系 ─────────── */
.saas-modern-table {
  border: none !important;
}

/* 仅第一行表头赋予浅蓝灰底色与细分隔线 */
.saas-modern-table :deep(.el-table__header-wrapper th) {
  background-color: #f1f5f9 !important;
  color: #475569 !important;
  font-weight: 700 !important;
  font-size: 13px !important;
  border-bottom: 1px solid #e2e8f0 !important;
  border-right: none !important;
  border-top: none !important;
  border-left: none !important;
  white-space: nowrap !important;
  letter-spacing: 0.3px;
}

.saas-modern-table :deep(.el-table__header-wrapper th .cell) {
  white-space: nowrap !important;
  word-break: keep-all !important;
}

.saas-modern-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.saas-modern-table :deep(.el-table__row td) {
  border-right: none !important;
  border-left: none !important;
  border-bottom: 1px solid #f1f5f9 !important;
}

.saas-modern-table :deep(.el-table__row:hover td) {
  background-color: #f8fafc !important;
}

.saas-modern-table :deep(.el-checkbox__inner) {
  border-radius: 4px !important;
  border-color: #cbd5e1 !important;
}

.col-id-text {
  font-size: 13px;
  color: #64748b;
  font-weight: 700;
  white-space: nowrap;
}

.question-main-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.5;
}

/* 题型圆角胶囊 */
.type-pill {
  display: inline-block;
  padding: 3px 10px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 12px;
  white-space: nowrap;
}

.type-pill.single { background: #eff6ff; color: #1d4ed8; }
.type-pill.multiple { background: #f5f3ff; color: #7c3aed; }
.type-pill.judge { background: #fef3c7; color: #b45309; }
.type-pill.fill { background: #ecfdf5; color: #047857; }
.type-pill.short { background: #fff1f2; color: #e11d48; }

/* 来源胶囊 */
.source-ai-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  background: #fdf4ff;
  color: #c026d3;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  line-height: 1.4;
}

.ai-sparkle-svg {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
  color: #c026d3;
}

.source-manual-pill {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  background: #f8fafc;
  color: #64748b;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  line-height: 1.4;
}

/* 分类胶囊 */
.category-pill {
  display: inline-block;
  padding: 3px 12px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  font-weight: 600;
  border-radius: 14px;
  white-space: nowrap;
}

.score-highlight {
  font-size: 13px;
  font-weight: 700;
  color: #0284c7;
  white-space: nowrap;
}

.muted-gray-text {
  font-size: 13px;
  color: #94a3b8;
}

/* 操作列链接按钮组 */
.action-btn-group {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
}

.action-link-btn {
  font-size: 13px !important;
  font-weight: 600 !important;
  padding: 4px 6px !important;
  margin: 0 !important;
}

.action-link-btn.green { color: #16a34a !important; }
.action-link-btn.orange { color: #f97316 !important; }
.action-link-btn.red { color: #ef4444 !important; }

.action-link-btn:hover {
  background: #f1f5f9 !important;
  border-radius: 6px !important;
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

/* AI 创建弹窗: 顶部红色上限提示 */
.ai-limit-tip {
  color: #f56c6c;
  font-size: 13px;
  line-height: 1.6;
  font-weight: 600;
  margin: 0 0 12px;
}

/* AI 创建弹窗: 高级选项 */
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

/* ─────────── ✨ AI 创建题目结果卡片全貌展示体系 ─────────── */
.ai-preview-section {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-preview-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.preview-tip {
  font-size: 12px;
  color: #64748b;
}

.ai-preview-cards-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding: 2px;
}

.ai-q-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ai-q-card:hover {
  border-color: #94a3b8;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
}

.ai-q-card.is-checked {
  border-color: #3b82f6;
  background: #f8fbff;
  box-shadow: 0 0 0 1px #3b82f6 inset;
}

.ai-q-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.ai-q-seq {
  font-size: 13px;
  font-weight: 800;
  color: #0f172a;
}

.ai-q-score {
  font-size: 12px;
  font-weight: 700;
  color: #0284c7;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  padding: 1px 8px;
  border-radius: 10px;
  margin-left: auto;
}

.ai-q-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.6;
  margin-bottom: 6px;
}
</style>
