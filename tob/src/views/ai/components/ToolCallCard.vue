<!--
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[修复底部双重操作按钮Bug：将通用 action-footer 的排除条件补充 create_question_draft 与 delete_question，彻底杜绝出现两对'确认/取消'按钮]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[重构 create_question_draft 批量出题卡片：区分批量出题参数确认与已有题目草稿预览形态，支持真实材料、多选/单选题型标签、出题数量、难度与题库分类选择，解决数据错配导致界面空白/单选题/正确答案破折号的问题]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[1. 修正试卷分类接口入参 target_type 为 task，彻底解决分类下拉列表为空的Bug; 2. 增强 hasShortQuestion 题型匹配，兼容 short/essay/subjective/qa，无简答题自动隐藏AI阅卷选项，有简答题显示且默认ai_auto]
 * 修改时间：2026-09-10
 * AI模型：Gemini 系列
 * 修改内容：[1. 改造题目列表手风琴：将题型标签、分值、知识库来源直接平铺展示在题目题干下方，常态可见，无需折叠展开; 2. 知识库来源标签添加 @click.stop 彻底阻止折叠展开冒泡; 3. AI 阅卷模式默认值更改为「ai_auto (AI 自动托管)」]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[新增 delete_question 题目删除安全确认卡片视图与交互闭环]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[1. 修复 riskColor 未定义 Bug; 2. 修复 draftPreview 与 formatQuestion 函数签名错配; 3. 增强试题知识溯源标签展示与 show-source 抽屉事件联动; 4. 合并试卷分类/考试时长/阅卷模式到确认事件中]
 * 修改时间：2026-09-10
 * AI模型：Agnes-2.5-Flash
 * 修改内容：[新建工具调用确认卡组件 - action_required 事件渲染]
-->
<template>
  <div class="tool-card" :class="riskClass">
    <div class="tool-card__header">
      <span class="tool-card__icon"><el-icon><MagicStick /></el-icon></span>
      <span class="tool-card__title">确认: {{ riskLabel }}风险业务操作</span>
      <span class="tool-card__badge" :class="resolvedClass">{{ resolvedText }}</span>
    </div>
    <div class="tool-card__body">
      <div v-if="!content" class="tool-card__desc">
        请确认是否执行刚才的操作【{{ toolCnName }}】
      </div>
      <div v-else class="tool-card__desc">
        风险等级: <strong :style="{ color: riskColor }">{{ riskLabel }}风险</strong><br/>
        有效期: 5 分钟
      </div>

      <!-- 组卷确认卡 -->
      <div v-if="toolName === 'create_exam_draft'" class="exam-draft-card" style="position: relative;">
        <AiGeneratingOverlay
          :visible="fetchingExam"
          title="AI 正在生成试卷题目…"
          detail="大模型全量出题约需10~20秒"
          :elapsed="fetchExamElapsed"
          @cancel="cancelExamFetch"
          @retry="fetchExamFallback"
        />
        <AiGeneratingOverlay
          :visible="confirming"
          title="正在创建试卷入库…"
          detail="入库完成前卡片不可操作"
          :elapsed="execElapsed"
          :cancelable="false"
        />
        <div class="exam-draft-title">AI 智能组卷确认</div>
        <div class="exam-draft-summary">{{ examTypeSummary }}</div>
        <el-collapse v-if="examDisplayQuestions.length > 0">
          <el-collapse-item
            v-for="(q, qi) in examDisplayQuestions"
            :key="qi"
            :name="qi"
          >
            <template #title>
              <div class="collapse-title-wrap">
                <div class="title-text">第 {{ qi + 1 }} 题 · {{ q.title || '（未命题干）' }}</div>
                <div class="draft-meta title-meta">
                  <el-tag size="small" type="primary">{{ formatQuestion(q).typeLabel }}</el-tag>
                  <span class="score-badge">{{ formatQuestion(q).score }} 分</span>
                  <el-tag
                    v-if="q.ai_rag_sources && q.ai_rag_sources.length"
                    size="small"
                    type="success"
                    effect="plain"
                    class="src-tag-clickable"
                    @click.stop="$emit('show-source', q.ai_rag_sources[0])"
                  >
                    📚 知识库来源: {{ q.ai_rag_sources[0].file_name || q.ai_rag_sources[0].document_name || '参考文档' }}
                  </el-tag>
                </div>
              </div>
            </template>
            <div
              v-for="(opt, oi) in formatQuestion(q).options"
              :key="oi"
              class="draft-opt"
              :class="{ correct: opt.correct }"
            >
              <span class="draft-opt-key">{{ opt.label }}</span>
              <span>{{ opt.text }}</span>
              <span v-if="opt.correct" class="draft-opt-mark">✓</span>
            </div>
            <div class="draft-row" style="margin-top: 6px">
              <span class="draft-label">答案:</span> {{ formatQuestion(q).answerText }}
            </div>
            <div v-if="q.explanation" class="draft-row draft-explanation">
              <span class="draft-label">解析:</span> {{ q.explanation }}
            </div>

          </el-collapse-item>
        </el-collapse>
        <div v-if="examDisplayQuestions.length === 0 && !actionResolved && !fetchingExam && fetchExamError" class="tool-card__desc" style="color: #b91c1c;">
          {{ fetchExamError }}
          <el-button size="small" type="primary" plain style="margin-left: 8px;" @click="fetchExamFallback">重新生成</el-button>
        </div>
        <el-form label-width="90px" size="small" style="margin-top: 12px">
          <el-form-item label="试卷分类">
            <el-select v-model="examForm.category_id" placeholder="选择试卷分类" style="width: 100%">
              <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="考试时间">
            <el-date-picker
              v-model="examForm.timeRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="考试时长">
            <div style="display: flex; align-items: center; gap: 12px">
              <el-switch v-model="examForm.is_timed" />
              <div v-if="examForm.is_timed" style="display: flex; align-items: center; gap: 6px">
                <el-input-number v-model="examForm.time_limit" :min="1" :max="600" />
                <span style="color: #64748b">分钟</span>
              </div>
              <span v-else style="color: #94a3b8">不限时长</span>
            </div>
          </el-form-item>
          <el-form-item v-if="hasShortQuestion" label="AI 阅卷模式">
            <el-radio-group v-model="examForm.grading_mode">
              <el-radio label="ai_auto">AI 自动托管</el-radio>
              <el-radio label="manual">人工全权批阅</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
        <div v-if="!actionResolved" class="action-footer">
          <button class="btn-confirm-medium" :disabled="fetchingExam || confirming" :style="(fetchingExam || confirming) ? { opacity: 0.5, cursor: 'not-allowed' } : {}" @click="handleConfirm">{{ confirming ? '正在入库…请稍候' : (fetchingExam ? '题目生成中…' : '确认创建试卷') }}</button>
          <button class="btn-cancel" :disabled="confirming" @click="$emit('cancel', message)">取消</button>
        </div>
        <div v-else class="tool-card__desc">
          试卷草稿已创建，可前往<a class="exam-link" href="#/tasks">试卷管理</a>查看
        </div>
      </div>

      <!-- 批量/单道出题确认卡 (create_question_draft)：一步明细预览 + 复选批量删 + 题干可改 -->
      <div v-else-if="toolName === 'create_question_draft'" class="exam-draft-card" style="position: relative;">
        <AiGeneratingOverlay
          :visible="fetchingQuestions"
          :title="countIsSingle ? 'AI 正在生成题目…' : 'AI 正在批量生成题目…'"
          :detail="`大模型全量出题约需10~20秒（计划${plannedCount}道）`"
          :elapsed="fetchElapsed"
          @cancel="cancelFetch"
          @retry="fetchQuestionsFallback"
        />
        <AiGeneratingOverlay
          :visible="confirming"
          :title="`正在入库 ${remainingCount} 道题目…`"
          detail="入库完成前题目不可删改"
          :elapsed="execElapsed"
          :cancelable="false"
        />
        <div class="exam-draft-title" style="color: #0284c7; display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 6px;">
            <el-icon><MagicStick /></el-icon>
            <span>AI 批量出题确认</span>
          </div>
          <el-tag size="small" type="primary" effect="plain">
            <template v-if="hasServerQuestions">{{ remainingCount }} 道题目<span v-if="deletedCount > 0" style="opacity: 0.7">（共{{ originalTotal }}，已删{{ deletedCount }}）</span></template>
            <template v-else>题目生成中…（计划{{ plannedCount }}道）</template>
          </el-tag>
        </div>

        <!-- 场景A：明细预览（必现，后端已保障首包含 questions） -->
        <template v-if="editableQuestions.length > 0">
          <div class="exam-draft-summary">{{ editableExamTypeSummary }}</div>
          <div v-if="!actionResolved" class="draft-toolbar">
            <el-checkbox v-model="allChecked" :indeterminate="isIndeterminate" @change="toggleAll">全选</el-checkbox>
            <el-button size="small" type="danger" plain :disabled="checkedCount === 0" @click="batchDelete">批量删除({{ checkedCount }})</el-button>
            <el-button v-if="deletedCount > 0" size="small" plain @click="restoreAll">恢复全部</el-button>
            <span class="toolbar-hint">勾选后可批量删，题干可直接改</span>
          </div>
          <el-collapse>
            <el-collapse-item
              v-for="(q, qi) in editableQuestions"
              :key="qi"
              :name="qi"
            >
              <template #title>
                <div class="collapse-title-wrap">
                  <div class="title-text" style="display: flex; align-items: center; gap: 8px;">
                    <el-checkbox v-if="!actionResolved" :model-value="checked[qi]" @click.stop @change="onCheck(qi, $event)" />
                    <span>第 {{ qi + 1 }} 题 · {{ (q.title || '（未命题干）').slice(0, 40) }}</span>
                    <el-button v-if="!actionResolved" size="small" type="danger" text @click.stop="removeQuestion(qi)">删除</el-button>
                  </div>
                  <div class="draft-meta title-meta">
                    <el-tag size="small" type="primary">{{ formatQuestion(q).typeLabel }}</el-tag>
                    <span class="score-badge">{{ formatQuestion(q).score }} 分</span>
                  </div>
                </div>
              </template>
              <div v-if="!actionResolved" style="margin-bottom: 8px;">
                <div class="draft-label" style="margin-bottom: 4px;">题干（可直接修改）：</div>
                <el-input v-model="editableQuestions[qi].title" type="textarea" :rows="2" maxlength="500" show-word-limit placeholder="请输入题干" @click.stop />
              </div>
              <div v-else class="draft-row" style="margin-bottom: 8px;">
                <span class="draft-label">题干:</span> {{ q.title }}
              </div>
              <div v-if="formatQuestion(q).options.length" class="draft-opts">
                <div
                  v-for="(opt, oi) in formatQuestion(q).options"
                  :key="oi"
                  class="draft-opt"
                  :class="{ correct: opt.correct }"
                >
                  <span class="draft-opt-key">{{ opt.label }}</span>
                  <span>{{ opt.text }}</span>
                  <span v-if="opt.correct" class="draft-opt-mark">✓</span>
                </div>
              </div>
              <div class="draft-row">
                <span class="draft-label">正确答案:</span> {{ formatQuestion(q).answerText }}
              </div>
              <div v-if="q.explanation" class="draft-row draft-explanation" style="margin-top: 6px">
                <span class="draft-label">解析:</span> {{ q.explanation }}
              </div>
            </el-collapse-item>
          </el-collapse>
          <div class="toolbar-hint" style="margin-top: 8px;">刷新后按服务端原始还原，删改态不持久化；确认后仅入库剩余 {{ remainingCount }} 道。</div>
        </template>

        <!-- 场景B降级：后端未返回明细时显示，不再误报“已删” -->
        <template v-else>
          <div v-if="!actionResolved" class="draft-meta" style="margin-top: 8px; margin-bottom: 12px;">
            <el-tag v-for="t in questionDraftSummary.typeLabels" :key="t" size="small" type="primary">{{ t }}</el-tag>
            <el-tag size="small" type="warning">难度: {{ questionDraftSummary.difficultyLabel }}</el-tag>
            <span v-if="fetchingQuestions" style="font-size: 12px; color: #0284c7;">题目生成中…（计划{{ plannedCount }}道）</span>
            <span v-else-if="hasServerQuestions" style="font-size: 12px; color: #64748b;">{{ `已删除全部 ${originalTotal} 道题目，可恢复后重新选择` }}</span>
            <span v-else-if="fetchError" style="font-size: 12px; color: #dc2626;">{{ fetchError }}</span>
            <span v-else style="font-size: 12px; color: #64748b;">题目明细尚未生成，点击下方按钮重新生成（历史消息默认不自动生成）</span>
          </div>
          <div v-if="hasServerQuestions && !actionResolved" style="margin-bottom: 12px;">
            <el-button size="small" plain @click="restoreAll">恢复全部 {{ originalTotal }} 道题目</el-button>
          </div>
          <div v-if="!hasServerQuestions && !actionResolved && !fetchingQuestions" style="margin-bottom: 12px;">
            <el-button size="small" type="primary" plain @click="fetchQuestionsFallback">重新生成题目明细</el-button>
          </div>

          <div style="background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 12px; margin-bottom: 12px;">
            <div style="font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 4px;">出题需求 / 背景材料：</div>
            <div style="font-size: 13px; color: #1e293b; line-height: 1.6; word-break: break-word;">
              {{ questionDraftSummary.material || '无特定出题材料，按通用业务标准生成' }}
            </div>
          </div>
        </template>

        <!-- 出题入库表单设置 (归属题库分类等) -->
        <el-form v-if="!actionResolved" size="small" label-position="top" style="margin-top: 10px;">
          <el-form-item label="归属题库分类 (可选)">
            <el-select
              v-model="questionForm.category_id"
              placeholder="默认未分类（可选择目标题库）"
              clearable
              style="width: 100%;"
            >
              <el-option
                v-for="c in resourceCategories"
                :key="c.id"
                :label="c.name"
                :value="c.id"
              />
            </el-select>
          </el-form-item>
        </el-form>

        <div v-if="!actionResolved" class="action-footer" style="margin-top: 8px;">
          <button class="btn-confirm-medium" :disabled="remainingCount === 0 || fetchingQuestions || confirming" :style="(remainingCount === 0 || fetchingQuestions || confirming) ? { opacity: 0.5, cursor: 'not-allowed' } : {}" @click="handleConfirmQuestionDraft">{{ confirming ? '正在入库…请稍候' : (fetchingQuestions ? `题目生成中…（已等待${fetchElapsed}s，可取消）` : `确认生成 ${remainingCount} 道题目并入库`) }}</button>
          <button class="btn-cancel" :disabled="confirming" @click="$emit('cancel', message)">取消</button>
        </div>
        <div v-else class="tool-card__desc" style="margin-top: 8px;">
          已确认批量出题，题目生成后将自动归档至题库。
        </div>
      </div>

      <!-- 删除试卷安全确认卡 -->
      <div v-else-if="toolName === 'delete_exam'" class="exam-draft-card" style="border-color: #fed7aa; background: #fffaf5;">
        <div class="exam-draft-title" style="color: #c2410c; display: flex; align-items: center; gap: 6px;">
          <el-icon><Delete /></el-icon>
          <span>试卷删除确认（不可逆操作）</span>
        </div>
        <div style="font-size: 13px; color: #475569; margin-bottom: 8px;">
          您正在通过 AI 助理申请物理删除试卷
          <span v-if="toolArgs?.keyword">（匹配关键词<strong>{{ toolArgs.keyword }}</strong>）</span>
          <span v-else-if="toolArgs?.exam_id">（指定试卷 ID<strong>{{ toolArgs.exam_id }}</strong>）</span>
          <span v-else>（默认操作：您名下最近创建的一份试卷）</span>
        </div>
        <div style="background: #fff; border: 1px dashed #fdba74; border-radius: 6px; padding: 8px 12px; font-size: 12px; color: #9a3412; line-height: 1.6;">
          ⚠️ <strong>风控安全准则</strong>：仅允许删除<strong>您本人创建</strong>、处<strong>未上架草稿(draft)或已下架(archived)</strong>状态且<strong>零学员作答</strong>的试卷。若试卷正在上架中需先下架；若已有学员提交考试，系统将拒绝删除以保护成绩数据安全。
        </div>
        <div v-if="!actionResolved" class="action-footer">
          <button class="btn-confirm" @click="handleConfirm">确认删除试卷</button>
          <button class="btn-cancel" @click="$emit('cancel', message)">取消</button>
        </div>
      </div>

      <!-- 删除题目安全确认卡 -->
      <div v-else-if="toolName === 'delete_question'" class="exam-draft-card" style="border-color: #fed7aa; background: #fffaf5;">
        <div class="exam-draft-title" style="color: #c2410c; display: flex; align-items: center; gap: 6px;">
          <el-icon><Delete /></el-icon>
          <span>题目删除确认（软删除）</span>
        </div>
        <div style="font-size: 13px; color: #475569; margin-bottom: 8px;">
          您正在通过 AI 助理申请从企业题库中删除题目
          <span v-if="toolArgs?.keyword">（匹配关键词<strong>{{ toolArgs.keyword }}</strong>）</span>
          <span v-else-if="toolArgs?.question_id">（指定题目 ID<strong>{{ toolArgs.question_id }}</strong>）</span>
          <span v-else>（默认操作：最近创建的一道题目）</span>
        </div>
        <div style="background: #fff; border: 1px dashed #fdba74; border-radius: 6px; padding: 8px 12px; font-size: 12px; color: #9a3412; line-height: 1.6;">
          ⚠️ <strong>操作提示</strong>：删除后题目将从题库列表中移除，但已引用该题目的历史试卷不受影响。
        </div>
        <div v-if="!actionResolved" class="action-footer">
          <button class="btn-confirm" @click="handleConfirm">确认删除题目</button>
          <button class="btn-cancel" @click="$emit('cancel', message)">取消</button>
        </div>
      </div>

      <!-- 通用卡片 -->
      <div v-else class="action-code">
        <pre>{{ JSON.stringify(toolArgs, null, 2) }}</pre>
      </div>

      <div v-if="!actionResolved && !['create_exam_draft', 'create_question_draft', 'delete_exam', 'delete_question'].includes(toolName)" class="action-footer">
        <button class="btn-confirm-medium" @click="handleConfirm">
          确认执行
        </button>
        <button class="btn-cancel" @click="$emit('cancel', message)">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { MagicStick, Delete } from '@element-plus/icons-vue';
import request from '../../../utils/request';
import AiGeneratingOverlay from './AiGeneratingOverlay.vue';

export interface ToolCallMessage {
  role: 'assistant';
  actionRequired?: boolean;
  toolName?: string;
  toolCallId?: string;
  arguments?: any;
  riskLevel?: string;
  actionResolved?: boolean;
  executeNonce?: number;
  content?: string;
  id?: number | string;
}

const props = defineProps<{
  message: ToolCallMessage;
  categories?: any[];
}>();

const emit = defineEmits<{
  (e: 'confirm', msg: ToolCallMessage): void;
  (e: 'cancel', msg: ToolCallMessage): void;
  (e: 'show-source', source: any): void;
}>();

const categories = ref<any[]>(props.categories || []);
const resourceCategories = ref<any[]>([]);
const fetchingQuestions = ref(false);
const fetchError = ref('');
const fetchElapsed = ref(0);
let fetchTimer: number | null = null;
let fetchController: AbortController | null = null;

const startElapsed = () => {
  stopElapsed();
  fetchElapsed.value = 0;
  fetchTimer = window.setInterval(() => {
    fetchElapsed.value += 1;
  }, 1000);
};
const stopElapsed = () => {
  if (fetchTimer !== null) {
    window.clearInterval(fetchTimer);
    fetchTimer = null;
  }
};
onUnmounted(() => {
  stopElapsed();
  fetchController?.abort();
});

const cancelFetch = () => {
  fetchController?.abort();
};

// 预览缓存 + 新旧卡片闸门：历史还原的卡片默认不自动生成，只留重试按钮
const cardCacheKey = (suffix = '') => {
  const id = props.message.id ?? props.message.toolCallId ?? '';
  if (id === '' || id === null || id === undefined) return '';
  return `tiku:ai:qpreview:${props.message.toolName || 'q'}:${id}${suffix}`;
};
const isFreshCard = () => {
  try {
    const ids = JSON.parse(sessionStorage.getItem('tiku_ai_fresh_cards') || '[]');
    const cur = props.message.toolCallId || '';
    return !!cur && Array.isArray(ids) && ids.includes(cur);
  } catch (e) {
    return false;
  }
};
const loadCachedPreview = (suffix = ''): any[] | null => {
  try {
    const k = cardCacheKey(suffix);
    if (!k) return null;
    const raw = localStorage.getItem(k);
    if (!raw) return null;
    const list = JSON.parse(raw);
    return Array.isArray(list) && list.length > 0 ? list : null;
  } catch (e) {
    return null;
  }
};
const saveCachedPreview = (list: any[], suffix = '') => {
  try {
    const k = cardCacheKey(suffix);
    if (!k) return;
    localStorage.setItem(k, JSON.stringify(list.slice(0, 20)));
  } catch (e) { /* 配额不足时忽略 */ }
};
const clearCachedPreview = (suffix = '') => {
  try {
    const k = cardCacheKey(suffix);
    if (k) localStorage.removeItem(k);
  } catch (e) { /* 忽略 */ }
};

const fetchQuestionsFallback = async () => {
  if (toolName.value !== 'create_question_draft') return;
  if (actionResolved.value) return;
  if (originalQuestions.value.length > 0 || fetchingQuestions.value) return;
  const material = String((toolArgs.value as any)?.material || (toolArgs.value as any)?.description || '').trim();
  if (!material) return;
  let count = Number((toolArgs.value as any)?.count || 5);
  if (!Number.isFinite(count)) count = 5;
  count = Math.max(1, Math.min(count, 10));
  fetchController?.abort();
  fetchController = new AbortController();
  fetchingQuestions.value = true;
  fetchError.value = '';
  startElapsed();
  try {
    const res: any = await request.post('/api/v1/admin/ai/questions/generate', {
      material,
      count,
      types: (toolArgs.value as any)?.types || ['single'],
      difficulty: (toolArgs.value as any)?.difficulty || 'medium'
    }, { timeout: 120000, signal: fetchController.signal, silent: true } as any);
    const list = res?.questions || res?.data?.questions || [];
    if (Array.isArray(list) && list.length > 0) {
      originalQuestions.value = cloneQuestions(list);
      editableQuestions.value = cloneQuestions(list);
      checked.value = editableQuestions.value.map(() => true);
      saveCachedPreview(list);
    } else {
      fetchError.value = '题目生成返回为空，请重试';
    }
  } catch (e: any) {
    if (e?.code === 'ERR_CANCELED' || String(e?.message || '').toLowerCase().includes('canceled')) {
      fetchError.value = '已取消生成，可重新生成或直接取消本操作';
    } else {
      fetchError.value = e?.response?.data?.detail || e?.message || '题目生成失败，请重试';
    }
  } finally {
    fetchingQuestions.value = false;
    stopElapsed();
  }
};

// 组卷卡兜底：SSE 首包无 questions 时，用题库出题接口按 specs 总量拉预览（仅预览，确认仍走 execute_tool 建卷）
const fetchingExam = ref(false);
const fetchExamError = ref('');
const fetchExamElapsed = ref(0);
const examEditableQuestions = ref<any[]>([]);
let examTimer: number | null = null;
let examController: AbortController | null = null;
onUnmounted(() => {
  if (examTimer !== null) window.clearInterval(examTimer);
  examController?.abort();
});
const examDisplayQuestions = computed(() => examEditableQuestions.value.length > 0 ? examEditableQuestions.value : (toolArgs.value?.questions || []));
const cancelExamFetch = () => {
  examController?.abort();
};
const fetchExamFallback = async () => {
  if (toolName.value !== 'create_exam_draft') return;
  if (actionResolved.value) return;
  if (fetchingExam.value) return;
  const serverQs = Array.isArray((toolArgs.value as any)?.questions) ? (toolArgs.value as any).questions : [];
  if (serverQs.length > 0 || examEditableQuestions.value.length > 0) return;
  const specs = Array.isArray((toolArgs.value as any)?.specs) ? (toolArgs.value as any).specs : [];
  const total = specs.reduce((s: number, sp: any) => s + (Number(sp?.count) || 0), 0) || 5;
  const material = String((toolArgs.value as any)?.title || (toolArgs.value as any)?.description || '').trim();
  if (!material) return;
  examController?.abort();
  examController = new AbortController();
  fetchingExam.value = true;
  fetchExamError.value = '';
  fetchExamElapsed.value = 0;
  if (examTimer !== null) window.clearInterval(examTimer);
  examTimer = window.setInterval(() => {
    fetchExamElapsed.value += 1;
  }, 1000);
  try {
    const res: any = await request.post('/api/v1/admin/ai/questions/generate', {
      material: `${material}（组卷预览）`,
      count: Math.max(1, Math.min(total, 10)),
      difficulty: 'medium'
    }, { timeout: 120000, signal: examController.signal, silent: true } as any);
    const list = res?.questions || res?.data?.questions || [];
    if (Array.isArray(list) && list.length > 0) {
      examEditableQuestions.value = cloneQuestions(list);
      try {
        const k = cardCacheKey(':exam');
        if (k) localStorage.setItem(k, JSON.stringify(list.slice(0, 20)));
      } catch (e) { /* 忽略 */ }
    } else {
      fetchExamError.value = '试卷题目生成返回为空，请重试';
    }
  } catch (e: any) {
    if (e?.code === 'ERR_CANCELED' || String(e?.message || '').toLowerCase().includes('canceled')) {
      fetchExamError.value = '已取消生成，可重新生成或直接取消本操作';
    } else {
      fetchExamError.value = e?.response?.data?.detail || e?.message || '试卷题目生成失败，请重试';
    }
  } finally {
    fetchingExam.value = false;
    if (examTimer !== null) {
      window.clearInterval(examTimer);
      examTimer = null;
    }
  }
};

onMounted(async () => {
  if (categories.value.length === 0) {
    try {
      const res: any = await request.get('/api/v1/admin/categories', { params: { target_type: 'task' } });
      categories.value = Array.isArray(res) ? res : (res.items || []);
      if (!examForm.value.category_id && categories.value.length > 0) {
        examForm.value.category_id = categories.value[0].id;
      }
    } catch (e) {
      categories.value = [];
    }
  } else if (!examForm.value.category_id && categories.value.length > 0) {
    examForm.value.category_id = categories.value[0].id;
  }
  try {
    const resRes: any = await request.get('/api/v1/admin/categories', { params: { target_type: 'resource' } });
    resourceCategories.value = Array.isArray(resRes) ? resRes : (resRes.items || []);
    if (!questionForm.value.category_id && resourceCategories.value.length > 0) {
      questionForm.value.category_id = resourceCategories.value[0].id;
    }
  } catch (e) {
    resourceCategories.value = [];
  }
  // 挂载顺序：服务端明细 > 本地缓存秒恢复 > 本页新卡自动生成 > 历史卡片仅留重试按钮
  const cachedQs = loadCachedPreview();
  if (cachedQs && originalQuestions.value.length === 0) {
    originalQuestions.value = cloneQuestions(cachedQs);
    editableQuestions.value = cloneQuestions(cachedQs);
    checked.value = editableQuestions.value.map(() => true);
  }
  try {
    const examCached = loadCachedPreview(':exam');
    if (examCached && examEditableQuestions.value.length === 0) {
      examEditableQuestions.value = cloneQuestions(examCached);
    }
  } catch (e) { /* 忽略 */ }
  // v1.3/v1.4 回归兜底：仅本页新出的卡自动拉真实明细，历史还原卡片默认不烧 token
  if (isFreshCard()) {
    fetchQuestionsFallback();
    fetchExamFallback();
  }
});

const content = computed(() => props.message.content || '');

const riskColor = computed(() => {
  const l = props.message.riskLevel;
  if (l === 'high') return '#ef4444';
  if (l === 'medium') return '#f59e0b';
  return '#10b981';
});

const riskLabel = computed(() => {
  const level = props.message.riskLevel;
  if (level === 'high') return '高';
  if (level === 'medium') return '中';
  if (level === 'low') return '低';
  return '业务';
});

const riskClass = computed(() => {
  const level = props.message.riskLevel;
  if (level === 'high') return 'high-risk';
  if (level === 'medium') return 'med-risk';
  return 'low-risk';
});

const resolvedText = computed(() => {
  if (props.message.actionResolved) return '已处理';
  return '待确认';
});

const resolvedClass = computed(() => {
  if (props.message.actionResolved) return 'resolved';
  return '';
});

const toolName = computed(() => props.message.toolName || '');
const toolCnName = computed(() => {
  const map: Record<string, string> = {
    create_exam_draft: '智能组卷',
    create_question_draft: 'AI 批量出题',
    delete_exam: '删除试卷',
    delete_question: '删除题目'
  };
  return map[toolName.value] || toolName.value;
});
const toolArgs = computed(() => props.message.arguments || {});
const actionResolved = computed(() => props.message.actionResolved || false);

const questionDraftSummary = computed(() => {
  const args = toolArgs.value || {};
  const typeMap: Record<string, string> = { single: '单选题', multiple: '多选题', judge: '判断题', fill: '填空题', short: '简答题' };
  const diffMap: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难' };
  const rawTypes = Array.isArray(args.types) ? args.types : (args.types ? [args.types] : (args.type ? [args.type] : ['single']));
  const typeLabels = rawTypes.map((t: string) => typeMap[t] || t);
  const totalCount = args.count || (Array.isArray(args.questions) ? args.questions.length : 5);
  const difficultyLabel = diffMap[args.difficulty] || args.difficulty || '中等';
  const material = args.material || args.description || '';
  return {
    typeLabels: typeLabels.length ? typeLabels : ['多选题'],
    totalCount,
    difficultyLabel,
    material
  };
});

const questionForm = ref({
  category_id: toolArgs.value?.category_id || null as number | null
});

// 一步明细卡本地可编辑态：复选批量删 + 题干可改（只改题干，选项/答案只读）
const cloneQuestions = (list: any[]) => {
  try {
    return JSON.parse(JSON.stringify(list || []));
  } catch (e) {
    return [...(list || [])];
  }
};
const originalQuestions = ref<any[]>(cloneQuestions(toolArgs.value?.questions || []));
const editableQuestions = ref<any[]>(cloneQuestions(toolArgs.value?.questions || []));
const checked = ref<boolean[]>((toolArgs.value?.questions || []).map(() => true));
const syncEditableFromArgs = () => {
  originalQuestions.value = cloneQuestions(toolArgs.value?.questions || []);
  editableQuestions.value = cloneQuestions(toolArgs.value?.questions || []);
  checked.value = editableQuestions.value.map(() => true);
};
watch(
  () => (toolArgs.value as any)?.questions,
  (nv) => {
    if (actionResolved.value) return;
    if (Array.isArray(nv) && nv.length > 0 && originalQuestions.value.length === 0) {
      syncEditableFromArgs();
    } else if (originalQuestions.value.length === 0 && !fetchingQuestions.value && isFreshCard()) {
      fetchQuestionsFallback();
    }
  },
  { deep: true }
);
// 确认/取消后清理本地预览缓存，避免 stale 占用
watch(
  () => actionResolved.value,
  (v) => {
    if (v) {
      clearCachedPreview();
      clearCachedPreview(':exam');
    }
  }
);
const plannedCount = computed(() => questionDraftSummary.value.totalCount || 0);
const countIsSingle = computed(() => plannedCount.value <= 1);
const originalTotal = computed(() => originalQuestions.value.length);
const remainingCount = computed(() => editableQuestions.value.length);
const deletedCount = computed(() => Math.max(0, originalTotal.value - remainingCount.value));
const hasServerQuestions = computed(() => originalTotal.value > 0);
const checkedCount = computed(() => checked.value.filter(Boolean).length);
const isIndeterminate = computed(() => checkedCount.value > 0 && checkedCount.value < remainingCount.value);
const allChecked = computed({
  get: () => remainingCount.value > 0 && checkedCount.value === remainingCount.value,
  set: (v: boolean) => {
    checked.value = editableQuestions.value.map(() => !!v);
  }
});
const toggleAll = (v: boolean) => {
  checked.value = editableQuestions.value.map(() => !!v);
};
const onCheck = (idx: number, v: boolean) => {
  checked.value[idx] = !!v;
};
const removeQuestion = (idx: number) => {
  if (actionResolved.value) return;
  editableQuestions.value.splice(idx, 1);
  checked.value.splice(idx, 1);
};
const batchDelete = () => {
  if (actionResolved.value) return;
  const keep: any[] = [];
  const keepChecked: boolean[] = [];
  editableQuestions.value.forEach((q: any, i: number) => {
    if (!checked.value[i]) {
      keep.push(q);
      keepChecked.push(false);
    }
  });
  const removed = editableQuestions.value.length - keep.length;
  editableQuestions.value = keep;
  checked.value = keepChecked.length ? keepChecked.map(() => false) : [];
  // 批量删后默认全不选，避免误删
  if (removed > 0) ElMessage.success(`已移除 ${removed} 道题目`);
};
const restoreAll = () => {
  if (actionResolved.value) return;
  syncEditableFromArgs();
  ElMessage.success(`已恢复全部 ${originalTotal.value} 道题目`);
};
const editableExamTypeSummary = computed(() => {
  const qs = editableQuestions.value;
  if (!qs || qs.length === 0) return `已删除全部题目，可恢复后重新选择`;
  const label: Record<string, string> = { single: '单选', multiple: '多选', judge: '判断', fill: '填空', short: '简答' };
  const counts: Record<string, number> = {};
  for (const q of qs) counts[String(q?.type)] = (counts[String(q?.type)] || 0) + 1;
  const parts = Object.entries(counts).map(([t, n]) => `${n}题${label[t] || t}`);
  return `共 ${qs.length} 题 · ` + parts.join(' + ');
});

// 确认入库即时态：一点就禁用防连点，父级成功（actionResolved）或失败（executeNonce）时复位
const confirming = ref(false);
const execElapsed = ref(0);
let execTimer: number | null = null;
const startExecElapsed = () => {
  stopExecElapsed();
  execElapsed.value = 0;
  execTimer = window.setInterval(() => {
    execElapsed.value += 1;
  }, 1000);
};
const stopExecElapsed = () => {
  if (execTimer !== null) {
    window.clearInterval(execTimer);
    execTimer = null;
  }
};
let confirmTimer: number | null = null;
const armConfirmReset = () => {
  if (confirmTimer !== null) window.clearTimeout(confirmTimer);
  confirmTimer = window.setTimeout(() => {
    confirming.value = false;
    confirmTimer = null;
  }, 60000);
};
watch(
  () => actionResolved.value,
  (v) => {
    if (v) {
      confirming.value = false;
      stopExecElapsed();
      if (confirmTimer !== null) {
        window.clearTimeout(confirmTimer);
        confirmTimer = null;
      }
    }
  }
);
watch(
  () => props.message.executeNonce,
  (v) => {
    if (v) {
      confirming.value = false;
      stopExecElapsed();
    }
  }
);
onUnmounted(() => {
  if (confirmTimer !== null) window.clearTimeout(confirmTimer);
  stopExecElapsed();
});

const handleConfirmQuestionDraft = () => {
  if (confirming.value || fetchingQuestions.value || actionResolved.value) return;
  const remaining = editableQuestions.value
    .map((q: any) => ({ ...q, title: String(q?.title || '').trim() }))
    .filter((q: any) => q.title);
  if (remaining.length === 0) {
    ElMessage.warning('请至少保留1道题目后再确认入库');
    return;
  }
  confirming.value = true;
  startExecElapsed();
  armConfirmReset();
  const mergedArguments = {
    ...toolArgs.value,
    questions: remaining,
    count: remaining.length,
    deleted_count: deletedCount.value,
    category_id: questionForm.value.category_id
  };
  emit('confirm', {
    ...props.message,
    arguments: mergedArguments
  });
};

const formatQuestion = (a: any) => {
  if (!a) return { title: '', typeLabel: '', difficulty: '', score: 0, options: [], answerText: '' };
  const typeMap: Record<string, string> = { single: '单选题', multiple: '多选题', judge: '判断题', fill: '填空题', short: '简答题' };
  const rawAns = Array.isArray(a.answer) ? a.answer.map((x: any) => String(x ?? '').trim()) : (a.answer ? [String(a.answer).trim()] : []);
  const ansSet = new Set(rawAns.map((s: string) => s.toUpperCase()));
  const rawOpts = Array.isArray(a.options) ? a.options : [];
  const options = rawOpts.map((o: any, i: number) => {
    const label = String(o.key ?? String.fromCharCode(65 + i));
    const text = String(o.text ?? o.content ?? '');
    const correct = ansSet.has(label.toUpperCase()) || ansSet.has(text.toUpperCase()) || o.is_correct === true;
    return { label, text, correct };
  });
  return {
    title: String(a.title || '（无题干）'),
    typeLabel: typeMap[String(a.type)] || String(a.type || '题目'),
    difficulty: String(a.difficulty || 'medium'),
    score: a.score ?? 10,
    options,
    answerText: rawAns.join('、') || '—'
  };
};

const singleQuestionPreview = computed(() => formatQuestion(toolArgs.value));

const questions = computed(() => toolArgs.value?.questions || []);
const examTypeSummary = computed(() => {
  const qs = (examDisplayQuestions.value.length > 0 ? examDisplayQuestions.value : questions.value) as any[];
  if (!qs || qs.length === 0) {
    const specs = toolArgs.value?.specs || [];
    const label: Record<string, string> = { single: '单选', multiple: '多选', judge: '判断', fill: '填空', short: '简答' };
    const parts = specs.map((sp: any) => `${sp.count || 0}题${label[sp.q_type] || sp.q_type}`);
    return `共 ${(specs.reduce((s: number, it: any) => s + (it.count || 0), 0))} 题 · ` + (parts.join(' + ') || '待配置');
  }
  const label: Record<string, string> = { single: '单选', multiple: '多选', judge: '判断', fill: '填空', short: '简答' };
  const counts: Record<string, number> = {};
  for (const q of qs) counts[String(q?.type)] = (counts[String(q?.type)] || 0) + 1;
  const parts = Object.entries(counts).map(([t, n]) => `${n}题${label[t] || t}`);
  return `共 ${qs.length} 题 · ` + parts.join(' + ');
});

const hasShortQuestion = computed(() =>
  examDisplayQuestions.value.some((q: any) =>
    ['short', 'essay', 'subjective', 'qa'].includes(String(q?.type || '').toLowerCase())
  )
);

const examForm = ref({
  category_id: toolArgs.value?.category_id || null as number | null,
  timeRange: [] as string[],
  is_timed: toolArgs.value?.is_timed ?? true,
  time_limit: toolArgs.value?.time_limit || 30,
  grading_mode: (toolArgs.value?.grading_mode as string) || 'ai_auto'
});

const handleConfirm = () => {
  if (confirming.value || fetchingExam.value || actionResolved.value) return;
  confirming.value = true;
  startExecElapsed();
  armConfirmReset();
  const mergedArguments: any = {
    ...toolArgs.value,
    category_id: examForm.value.category_id,
    is_timed: examForm.value.is_timed,
    time_limit: examForm.value.time_limit,
    grading_mode: examForm.value.grading_mode,
    start_time: examForm.value.timeRange?.[0] || null,
    deadline: examForm.value.timeRange?.[1] || null
  };
  // 组卷兜底预览的题目一并带上，后端优先入库该明细
  if (examEditableQuestions.value.length > 0) {
    mergedArguments.questions = cloneQuestions(examEditableQuestions.value);
  }
  emit('confirm', {
    ...props.message,
    arguments: mergedArguments
  });
};
</script>

<style scoped>
.collapse-title-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  width: 100%;
  padding: 8px 0;
  line-height: 1.4;
}

.title-text {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  word-break: break-word;
}

.draft-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 10px;
  margin: 8px 0 10px;
}

.toolbar-hint {
  font-size: 12px;
  color: #94a3b8;
}

.title-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.score-badge {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.tool-card {
  margin-top: 12px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #fee2e2;
  width: 100%;
  max-width: 580px;
}

.tool-card.med-risk {
  border-color: #cffafe;
}

.tool-card.low-risk {
  border-color: #e2e8f0;
}

.tool-card__header {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #fecaca 0%, #fff1f2 100%);
  border-bottom: 1px solid #fee2e2;
}

.tool-card.med-risk .tool-card__header {
  background: linear-gradient(135deg, #a5f3fc 0%, #ecfeff 100%);
  border-bottom-color: #cffafe;
}

.tool-card.low-risk .tool-card__header {
  background: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%);
  border-bottom-color: #e2e8f0;
}

.tool-card__icon {
  font-size: 16px;
  display: flex;
  align-items: center;
}

.tool-card__title {
  font-weight: 700;
  color: #1e293b;
  font-size: 14px;
  flex: 1;
}

.tool-card__badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  background: #f87171;
  color: #fff;
}

.tool-card__badge.resolved {
  background: #10b981;
}

.tool-card__body {
  padding: 16px;
}

.tool-card__desc {
  font-size: 13px;
  color: #334155;
  line-height: 1.6;
  margin-bottom: 12px;
}

.exam-draft-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #334155;
}

.exam-draft-title {
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 6px;
}

.exam-draft-summary {
  color: #0284c7;
  font-weight: 600;
  margin-bottom: 8px;
}

.exam-link {
  color: #0284c7;
  cursor: pointer;
  font-weight: 600;
}

.exam-link:hover {
  text-decoration: underline;
}

.draft-preview {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #334155;
}

.draft-title {
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
  line-height: 1.6;
}

.draft-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.src-tag-clickable {
  cursor: pointer;
  transition: all 0.2s;
}

.src-tag-clickable:hover {
  opacity: 0.85;
  transform: translateY(-1px);
}

.draft-opts {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
}

.draft-opt {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 6px 10px;
  color: #64748b;
}

.draft-opt.correct {
  background-color: #f0fdf4;
  border-color: #86efac;
  color: #166534;
  font-weight: 600;
}

.draft-opt-key {
  font-weight: 800;
}

.draft-opt-mark {
  margin-left: auto;
}

.draft-row {
  line-height: 1.7;
}

.draft-label {
  font-weight: 700;
  color: #475569;
}
.draft-explanation {
  background: #fffbeb;
  border-left: 3px solid #fde68a;
  padding: 6px 10px;
  border-radius: 6px;
  color: #78350f;
}
.draft-explanation .draft-label {
  color: #b45309;
}

.action-code pre {
  margin: 0 0 16px 0;
  padding: 10px;
  background: #f8fafc;
  border-radius: 6px;
  font-size: 12px;
  color: #475569;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.action-footer {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-confirm {
  width: 100%;
  padding: 10px;
  background: #ef4444;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-confirm:hover {
  background: #dc2626;
}

.btn-confirm-medium {
  width: 100%;
  padding: 10px;
  background: #0284c7;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-confirm-medium:hover {
  background: #0369a1;
}

.btn-cancel {
  width: 100%;
  padding: 10px;
  background: #fff;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #f8fafc;
  border-color: #94a3b8;
}
</style>
