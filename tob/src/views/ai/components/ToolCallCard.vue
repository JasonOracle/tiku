<!--
 * [变更日志]
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
        请确认是否执行刚才的操作 ({{ toolName }})
      </div>
      <div v-else class="tool-card__desc">
        风险等级: <strong :style="{ color: riskColor }">{{ riskLabel }}风险</strong><br/>
        有效期: 5 分钟
      </div>

      <!-- 组卷确认卡 -->
      <div v-if="toolName === 'create_exam_draft'" class="exam-draft-card">
        <div class="exam-draft-title">AI 智能组卷确认</div>
        <div class="exam-draft-summary">{{ examTypeSummary }}</div>
        <el-collapse v-if="questions.length > 0">
          <el-collapse-item
            v-for="(q, qi) in questions"
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
          <button class="btn-confirm-medium" @click="handleConfirm">确认创建试卷</button>
          <button class="btn-cancel" @click="$emit('cancel', message)">取消</button>
        </div>
        <div v-else class="tool-card__desc">
          试卷草稿已创建，可前往<a class="exam-link" href="#/tasks">试卷管理</a>查看
        </div>
      </div>

      <!-- 新建题目卡 -->
      <div v-else-if="toolName === 'create_question_draft'" class="draft-preview">
        <div class="draft-title">{{ toolArgs?.title || 'AI 批量出题' }}</div>
        <div class="draft-meta">
          <el-tag size="small" type="primary">{{ singleQuestionPreview.typeLabel }}</el-tag>
          <span>难度 {{ singleQuestionPreview.difficulty }} · {{ singleQuestionPreview.score }} 分</span>
        </div>
        <div v-if="singleQuestionPreview.options.length" class="draft-opts">
          <div
            v-for="(opt, oi) in singleQuestionPreview.options"
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
          <span class="draft-label">正确答案:</span> {{ singleQuestionPreview.answerText }}
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

      <div v-if="!actionResolved && toolName !== 'create_exam_draft' && toolName !== 'delete_exam'" class="action-footer">
        <button class="btn-confirm-medium" @click="handleConfirm">
          确认执行
        </button>
        <button class="btn-cancel" @click="$emit('cancel', message)">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { MagicStick, Delete } from '@element-plus/icons-vue';
import request from '../../../utils/request';

export interface ToolCallMessage {
  role: 'assistant';
  actionRequired?: boolean;
  toolName?: string;
  toolCallId?: string;
  arguments?: any;
  riskLevel?: string;
  actionResolved?: boolean;
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

onMounted(async () => {
  if (categories.value.length === 0) {
    try {
      const res: any = await request.get('/api/v1/admin/categories', { params: { target_type: 'task' } });
      categories.value = Array.isArray(res) ? res : (res.items || []);
    } catch (e) {
      categories.value = [];
    }
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
const toolArgs = computed(() => props.message.arguments || {});
const actionResolved = computed(() => props.message.actionResolved || false);

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
  const qs = questions.value;
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
  questions.value.some((q: any) =>
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
  const mergedArguments = {
    ...toolArgs.value,
    category_id: examForm.value.category_id,
    is_timed: examForm.value.is_timed,
    time_limit: examForm.value.time_limit,
    grading_mode: examForm.value.grading_mode,
    start_time: examForm.value.timeRange?.[0] || null,
    deadline: examForm.value.timeRange?.[1] || null
  };
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
