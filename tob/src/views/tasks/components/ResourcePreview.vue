<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Codex 3
 * 修改内容：[恢复答案解析展示区块：题目预览底部新增琥珀色「答案解析」卡片，explanation 为空时不渲染，兼容 B 端题目管理/AI 出题/AI 组卷审阅清单与试卷审阅]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[根据用户最新明确规范：彻底移除所有试题预览中的「踩分点」与「文字解析」模块，无论简答还是客观题均仅保留标准答案与选项高亮]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 底层
 * 修改内容：[1. 彻底解决 AI 试卷审阅试题选项与正确答案不展示问题：增强 options 容错解析，兼容对象数组、字符串数组及纯文本; 2. 增强 answer/correct_answer 兼容提取; 3. 修复 judgeVerdict 中未声明变量 constHaystack 运行时引用异常]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗：属性 question 更名为 resource，旧题库词汇已删除]
 -->
<template>
  <div class="q-preview">
    <!-- 单选/多选：普通选项灰色小标签，正确答案绿色高亮并前置 ✔ -->
    <div v-if="normalizedType === 'single' || normalizedType === 'multiple'" class="opts-list">
      <span
        v-for="(opt, oIdx) in normalizedOptions"
        :key="opt.key || oIdx"
        class="opt-chip"
        :class="{ 'opt-correct': isCorrectOpt(opt.key) }"
      >
        <template v-if="isCorrectOpt(opt.key)">✔ [{{ opt.key }}] {{ opt.text }}</template>
        <template v-else>[{{ opt.key }}] {{ opt.text }}</template>
      </span>
      <span v-if="!normalizedOptions.length" class="muted">暂无选项</span>
    </div>

    <!-- 判断题：绿色 [✔ 正确] 或红色 [✖ 错误] -->
    <div v-else-if="normalizedType === 'judge'" class="opts-list">
      <el-tag v-if="judgeVerdict" type="success" size="small" effect="dark">✔ 正确</el-tag>
      <el-tag v-else type="danger" size="small" effect="dark">✖ 错误</el-tag>
      <span
        v-for="(opt, oIdx) in normalizedOptions"
        :key="opt.key || oIdx"
        class="opt-chip"
        :class="{ 'opt-correct': isCorrectOpt(opt.key) }"
      >
        <template v-if="isCorrectOpt(opt.key)">✔ [{{ opt.key }}] {{ opt.text }}</template>
        <template v-else>[{{ opt.key }}] {{ opt.text }}</template>
      </span>
    </div>

    <!-- 填空题：紧凑标准答案 -->
    <div v-else-if="normalizedType === 'fill'" class="compact-answer">
      <span class="compact-label">标准答案：</span>
      <span>{{ fillAnswerText }}</span>
    </div>

    <!-- 简答题：紧凑标准答案（供人工或AI参考审核） -->
    <div v-else-if="normalizedType === 'short'" class="compact-answer">
      <span class="compact-label">标准答案：</span>
      <span>{{ shortAnswerText }}</span>
    </div>

    <!-- 答案解析：全题型通用，选填字段，有内容才渲染 -->
    <div v-if="explanationText" class="explanation-block">
      <span class="explanation-label">答案解析</span>
      <p class="explanation-text">{{ explanationText }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  resource: any;
}>();

const q = computed(() => props.resource || {});

// 答案解析：直读 explanation 字段（后端 _res_out 与 AI 生成接口均已透传）
const explanationText = computed(() => {
  const raw = q.value.explanation;
  if (!raw) return '';
  if (typeof raw === 'string') return raw.trim();
  if (Array.isArray(raw)) return raw.filter(Boolean).join(' ');
  return String(raw);
});

// 统一规范化题型
const normalizedType = computed(() => {
  const t = String(q.value.type || 'single').toLowerCase();
  if (t === 'single' || t === 'single_choice') return 'single';
  if (t === 'multiple' || t === 'multiple_choice') return 'multiple';
  if (t === 'judge' || t === 'judgment' || t === 'boolean') return 'judge';
  if (t === 'fill' || t === 'fill_in' || t === 'blank') return 'fill';
  if (t === 'short' || t === 'short_answer' || t === 'essay') return 'short';
  return 'single';
});

// 规范化题目选项：兼容对象列表 [{key, text}]、字符串列表 ['A. 3-5分钟'] 以及 JSON 字符串
const normalizedOptions = computed(() => {
  let raw = q.value.options;
  if (!raw) return [];
  if (typeof raw === 'string') {
    try {
      raw = JSON.parse(raw);
    } catch {
      return [];
    }
  }
  if (!Array.isArray(raw)) return [];

  const defaultKeys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
  return raw.map((item: any, idx: number) => {
    if (typeof item === 'object' && item !== null) {
      const k = String(item.key || item.label || item.value || defaultKeys[idx] || '').trim().toUpperCase();
      const t = String(item.text ?? item.content ?? item.title ?? '').trim();
      return { key: k, text: t };
    }
    const str = String(item).trim();
    const match = str.match(/^([A-Za-z])[\.、\s\-:]+\s*(.*)$/);
    if (match) {
      return {
        key: match[1].toUpperCase(),
        text: match[2].trim()
      };
    }
    return {
      key: defaultKeys[idx] || `Opt${idx + 1}`,
      text: str
    };
  });
});

// 提取规范化答案 Set
const answerSet = computed(() => {
  const raw = q.value.answer ?? q.value.correct_answer;
  if (!raw) return new Set<string>();
  let list: any[] = [];
  if (Array.isArray(raw)) {
    list = raw;
  } else if (typeof raw === 'string') {
    try {
      const parsed = JSON.parse(raw);
      list = Array.isArray(parsed) ? parsed : [raw];
    } catch {
      list = raw.split(/[,，、;；]/).map(s => s.trim()).filter(Boolean);
    }
  } else {
    list = [raw];
  }
  return new Set(list.map((x) => String(x ?? '').trim().toUpperCase()).filter(Boolean));
});

const isCorrectOpt = (key: string): boolean => {
  return answerSet.value.has(String(key ?? '').trim().toUpperCase());
};

// 判断题裁决：正确答案选项文本含 错/误/否/False 即判错误，否则判正确
const judgeVerdict = computed(() => {
  const opts = normalizedOptions.value;
  const correctTexts = opts.filter((o: any) => isCorrectOpt(o.key)).map((o: any) => String(o.text || ''));
  const haystack = correctTexts.join(' ') + ' ' + Array.from(answerSet.value).join(' ');
  return !/[错误否]|FALSE/i.test(haystack);
});

const fillAnswerText = computed(() => {
  const raw = q.value.answer ?? q.value.correct_answer;
  if (!raw) return '暂未设定';
  const ans = Array.isArray(raw) ? raw : [raw];
  return ans
    .map((b: any) => (Array.isArray(b) ? b.join('/') : String(b)))
    .join(' | ');
});

const shortAnswerText = computed(() => {
  const raw = q.value.answer ?? q.value.correct_answer;
  if (!raw) return '暂未设定';
  if (Array.isArray(raw)) return raw[0] || '暂未设定';
  return String(raw);
});
</script>

<style scoped>
.q-preview {
  margin-top: 6px;
}
.opts-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.opt-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  background-color: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  color: #475569;
  font-size: 12px;
  line-height: 1.4;
  transition: all 0.2s ease;
}
.opt-correct {
  background-color: #f0fdf4 !important;
  border: 1px solid #86efac !important;
  color: #166534 !important;
  font-weight: 700 !important;
  box-shadow: 0 1px 3px rgba(22, 101, 52, 0.08);
}
.compact-answer {
  font-size: 13px;
  color: #334155;
  line-height: 1.6;
  background: #f8fafc;
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}
.compact-label {
  font-weight: 700;
  color: #0369a1;
}
.explanation-block {
  margin-top: 10px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 10px 12px;
}
.explanation-label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: #b45309;
  margin-bottom: 4px;
}
.explanation-text {
  font-size: 13px;
  color: #78350f;
  line-height: 1.7;
  margin: 0;
  white-space: pre-wrap;
}
.muted {
  color: #94a3b8;
  font-size: 12px;
}
</style>
