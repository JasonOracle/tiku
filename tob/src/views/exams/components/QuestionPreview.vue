<!--
  * [变更日志]
  * 修改时间：2026-09-08
  * AI模型：Gemini 系列
  * 修改内容：[增加 getOptKey 容错机制: 兼容 options 项中 key/label/value 或空 key 场景，自动按序号补齐 ABCDEF 标识，杜绝空中括号问题]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[v1.2 Step4 新建: 题目透亮预览 QuestionPreview (选项与正确答案绿色高亮/判断徽章/填空简答案例紧凑展示, 普通组卷与 AI 审阅共用)]
-->
<template>
  <div class="q-preview">
    <!-- 单选/多选：普通选项灰色小标签，正确答案绿色高亮并前置 ✔ -->
    <div v-if="q.type === 'single' || q.type === 'multiple'" class="opts-list">
      <span
        v-for="(opt, oIdx) in q.options || []"
        :key="getOptKey(opt, oIdx)"
        class="opt-chip"
        :class="{ 'opt-correct': isCorrectOpt(getOptKey(opt, oIdx)) }"
      >
        <template v-if="isCorrectOpt(getOptKey(opt, oIdx))">✔ [{{ getOptKey(opt, oIdx) }}] {{ opt.text }}</template>
        <template v-else>[{{ getOptKey(opt, oIdx) }}] {{ opt.text }}</template>
      </span>
      <span v-if="!(q.options || []).length" class="muted">暂无选项</span>
    </div>

    <!-- 判断题：绿色 [✔ 正确] 或红色 [✖ 错误] -->
    <div v-else-if="q.type === 'judge'" class="opts-list">
      <el-tag v-if="judgeVerdict" type="success" size="small" effect="dark">✔ 正确</el-tag>
      <el-tag v-else type="danger" size="small" effect="dark">✖ 错误</el-tag>
      <span
        v-for="(opt, oIdx) in q.options || []"
        :key="getOptKey(opt, oIdx)"
        class="opt-chip"
        :class="{ 'opt-correct': isCorrectOpt(getOptKey(opt, oIdx)) }"
      >
        <template v-if="isCorrectOpt(getOptKey(opt, oIdx))">✔ [{{ getOptKey(opt, oIdx) }}] {{ opt.text }}</template>
        <template v-else>[{{ getOptKey(opt, oIdx) }}] {{ opt.text }}</template>
      </span>
    </div>

    <!-- 填空题：紧凑标准答案 -->
    <div v-else-if="q.type === 'fill'" class="compact-answer">
      <span class="compact-label">标准答案：</span>
      <span>{{ fillAnswerText }}</span>
    </div>

    <!-- 简答题：紧凑标准答案/采分要点 -->
    <div v-else-if="q.type === 'short'" class="compact-answer">
      <span class="compact-label">参考答案：</span>
      <span>{{ shortAnswerText }}</span>
      <span v-if="(q.grading_points || []).length" class="compact-label" style="margin-left: 8px">采分点：</span>
      <span>{{ (q.grading_points || []).join('；') }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  question: any;
}>();

const q = computed(() => props.question || {});

const getOptKey = (opt: any, index: number): string => {
  if (!opt) return 'ABCDEF'[index] || 'A';
  const raw = opt.key || opt.label || opt.value || '';
  if (String(raw).trim()) return String(raw).trim().toUpperCase();
  return 'ABCDEF'[index] || `Opt${index + 1}`;
};

const normSet = (arr: any[]): Set<string> => {
  const list = Array.isArray(arr) ? arr : [];
  return new Set(list.map((x) => String(x ?? '').trim().toUpperCase()).filter(Boolean));
};

const answerSet = computed(() => normSet(q.value.answer));

const isCorrectOpt = (key: string): boolean => {
  return answerSet.value.has(String(key ?? '').trim().toUpperCase());
};

// 判断题裁决：正确答案选项文本含 错/误/否/False 即判错误，否则判正确
const judgeVerdict = computed(() => {
  const opts = q.value.options || [];
  const correctTexts = opts.filter((o: any) => isCorrectOpt(o.key)).map((o: any) => String(o.text || ''));
  constHaystack = correctTexts.join(' ') + ' ' + (q.value.answer || []).join(' ');
  return !/[错误否]|FALSE/i.test(constHaystack);
});

const fillAnswerText = computed(() => {
  const ans = q.value.answer || [];
  return ans
    .map((b: any) => (Array.isArray(b) ? b.join('/') : String(b)))
    .join(' | ');
});

const shortAnswerText = computed(() => {
  const ans = q.value.answer || [];
  return Array.isArray(ans) ? ans[0] || '' : String(ans);
});
</script>

<style scoped>
.q-preview {
  margin-top: 4px;
}
.opts-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.opt-chip {
  background: #f8fafc;
  padding: 2px 8px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 12px;
}
.opt-correct {
  background-color: #f0fdf4;
  border: 1px solid #86efac;
  color: #166534;
  font-weight: 600;
}
.compact-answer {
  font-size: 12px;
  color: #475569;
  line-height: 1.6;
}
.compact-label {
  font-weight: 700;
  color: #0369a1;
}
.muted {
  color: #94a3b8;
  font-size: 12px;
}
</style>
