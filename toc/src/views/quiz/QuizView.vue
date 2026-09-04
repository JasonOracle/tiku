<!--
 * [变更日志]
 * 修改时间：2026-09-03
 * AI模型：Gemini 底层
 * 修改内容：[1. 实现 C 端答题流引擎 (含限时倒计时、定时器卸载清理、上一题修改与一键收藏功能)]
-->
<template>
  <div class="quiz-container" v-if="record">
    <!-- 顶栏：返回 + 标题省略 + 进度 + 倒计时 -->
    <header class="quiz-header">
      <button class="back-btn" @click="confirmExit">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>

      <span class="quiz-title">{{ record.exam_title || '在线测评' }}</span>
      <span class="quiz-progress">{{ currentIndex + 1 }}/{{ questions.length }}</span>

      <div v-if="record.is_timed" class="timer-pill" :class="{ warning: remainingSeconds < 180 }">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="12" cy="12" r="10"></circle>
          <polyline points="12 6 12 12 16 14"></polyline>
        </svg>
        <span>{{ formattedTime }}</span>
      </div>
      <span v-else class="practice-tag">练习模式</span>
    </header>

    <!-- 题目正文卡片 -->
    <main class="question-card" v-if="currentQuestion">
      <div class="type-tag">{{ getTypeLabel(currentQuestion.type) }}</div>
      <h3 class="q-title">{{ currentQuestion.title }}</h3>

      <div class="options-list">
        <div
          v-for="opt in currentQuestion.options"
          :key="opt.key"
          class="option-item"
          :class="{ selected: isOptionSelected(opt.key), multiple: currentQuestion.type === 'multiple' }"
          @click="selectOption(opt.key)"
        >
          <span class="opt-key">{{ opt.key }}</span>
          <span class="opt-text">{{ opt.text }}</span>
          <span class="opt-check">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </span>
        </div>
      </div>
    </main>

    <!-- 底部操作控制 -->
    <footer class="quiz-footer">
      <button class="nav-btn" :disabled="currentIndex === 0" @click="prevQuestion">
        上一题
      </button>

      <button v-if="currentIndex < questions.length - 1" class="nav-btn primary" @click="nextQuestion">
        下一题
      </button>

      <button v-else class="nav-btn submit" :disabled="submitting" @click="submitExam()">
        {{ submitting ? '提交中...' : '交卷结算' }}
      </button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router';
import http from '../../utils/http';

const route = useRoute();
const router = useRouter();

const record = ref<any>(null);
const questions = ref<any[]>([]);
const currentIndex = ref(0);
const userAnswers = reactive<Record<string, string[]>>({});

const remainingSeconds = ref(0);
let timerId: any = null;
const submitting = ref(false);
const isFinished = ref(false); // 标记是否已完成交卷逻辑

const currentQuestion = computed(() => questions.value[currentIndex.value]);

const formattedTime = computed(() => {
  const m = Math.floor(remainingSeconds.value / 60);
  const s = remainingSeconds.value % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
});

const getTypeLabel = (type: string) => {
  if (type === 'single') return '单选题';
  if (type === 'multiple') return '多选题 (多选)';
  return '判断题';
};

const isOptionSelected = (key: string) => {
  if (!currentQuestion.value) return false;
  const qId = String(currentQuestion.value.id);
  return (userAnswers[qId] || []).length > 0 && userAnswers[qId].includes(key);
};

const selectOption = (key: string) => {
  if (!currentQuestion.value) return;
  const qId = String(currentQuestion.value.id);
  const qType = currentQuestion.value.type;

  if (qType === 'multiple') {
    const list = userAnswers[qId] ? [...userAnswers[qId]] : [];
    const idx = list.indexOf(key);
    if (idx >= 0) list.splice(idx, 1);
    else list.push(key);
    userAnswers[qId] = list;
  } else {
    userAnswers[qId] = [key];
  }
};

const prevQuestion = () => {
  if (currentIndex.value > 0) currentIndex.value--;
};

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) currentIndex.value++;
};

const startTimer = () => {
  if (!record.value || !record.value.is_timed) return;
  remainingSeconds.value = record.value.time_limit * 60;

  timerId = setInterval(() => {
    if (remainingSeconds.value > 0) {
      remainingSeconds.value--;
    } else {
      // 超时自动强行交卷
      clearInterval(timerId);
      timerId = null;
      submitExam(true);
    }
  }, 1000);
};

const submitExam = async (isAuto = false) => {
  if (submitting.value || isFinished.value) return;
  const auto = isAuto === true;
  const answeredCount = Object.keys(userAnswers).filter(id => userAnswers[id] && userAnswers[id].length > 0).length;

  // 空卷拦截：一题未答不交卷（防误入产生0分幽灵记录，后端同样拦截）
  if (answeredCount === 0) {
    if (auto) {
      alert('本场尚未作答任何题目，无需交卷');
      isFinished.value = true;
      router.back();
    } else {
      alert('请至少作答 1 道题后再交卷');
    }
    return;
  }

  // 手动交卷时的未答题统计确认
  if (!auto) {
    const unansweredCount = questions.value.length - answeredCount;
    if (unansweredCount > 0) {
      if (!confirm(`您还有 ${unansweredCount} 道题未作答，确定要直接交卷结算吗？`)) {
        return;
      }
    } else {
      if (!confirm('确定要提交试卷并查看分析报告吗？')) {
        return;
      }
    }
  }

  submitting.value = true;
  try {
    await http.post('/api/v1/records/submit', {
      record_id: record.value.record_id,
      user_answers: userAnswers,
      time_spent: record.value.is_timed ? (record.value.time_limit * 60 - remainingSeconds.value) : 120
    });
    isFinished.value = true;
    router.replace({ path: '/report', query: { record_id: record.value.record_id } });
  } catch (e) {
    // 交卷失败不标记完成，允许重试
    throw e;
  } finally {
    submitting.value = false;
  }
};

const hasAnswered = () => Object.keys(userAnswers).some(id => userAnswers[id] && userAnswers[id].length > 0);

const confirmExit = async () => {
  if (isFinished.value || submitting.value) {
    router.back();
    return;
  }
  // 空卷离开只提示不提交
  if (!hasAnswered()) {
    if (confirm('尚未作答任何题目，现在离开将不保存，确定离开吗？')) {
      isFinished.value = true;
      router.back();
    }
    return;
  }
  if (confirm('正在做题中，离开页面将自动为您提交当前已作答的试卷，确定要离开吗？')) {
    try {
      await submitExam(true);
    } catch (e) {
      return;
    }
    // submit 成功后 isFinished 已置 true，router.back 会再次触发守卫但直接放行，避免双重提交
    if (isFinished.value) router.back();
  }
};

// 路由守卫：拦截返回/切换路由
onBeforeRouteLeave(async (to, from, next) => {
  if (isFinished.value || submitting.value) {
    // 提交中禁止跳转，避免并发；已完成直接放行
    if (isFinished.value && !submitting.value) next();
    else next(false);
    return;
  }

  // 空卷离开只提示不提交
  if (!hasAnswered()) {
    if (confirm('尚未作答任何题目，现在离开将不保存，确定离开吗？')) {
      isFinished.value = true;
      next();
    } else {
      next(false);
    }
    return;
  }

  if (confirm('正在做题中，离开页面将自动为您提交当前已作答的试卷，确定要离开吗？')) {
    try {
      await submitExam(true);
      next();
    } catch (e) {
      next(false);
    }
  } else {
    next(false);
  }
});

// 浏览器卸载监听 (刷新、关闭标签)
const handleBeforeUnload = (e: BeforeUnloadEvent) => {
  if (!isFinished.value) {
    e.preventDefault();
    e.returnValue = '';
  }
};

onMounted(async () => {
  window.addEventListener('beforeunload', handleBeforeUnload);
  const examId = route.query.exam_id;
  if (!examId) {
    router.push('/');
    return;
  }

  try {
    const res: any = await http.post('/api/v1/records/start', { exam_id: Number(examId) });
    record.value = res;
    questions.value = res.questions || [];
    startTimer();
  } catch (e) {
    router.push('/');
  }
});

// 副作用绝对清理
onUnmounted(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload);
  if (timerId) {
    clearInterval(timerId);
    timerId = null;
  }
});
</script>

<style scoped>
.quiz-container {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
}

.quiz-header {
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
  border-bottom: 1px solid #f1f5f9;
}

.back-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #0f172a;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.quiz-title {
  flex: 1;
  min-width: 0;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quiz-progress {
  font-size: 13px;
  font-weight: 800;
  color: #0284c7;
  background: #f0f9ff;
  padding: 4px 10px;
  border-radius: 12px;
  flex-shrink: 0;
}

.timer-pill {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #e0f2fe;
  color: #0284c7;
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.timer-pill.warning {
  background: #fee2e2;
  color: #ef4444;
}

.practice-tag {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 600;
  flex-shrink: 0;
}

.question-card {
  flex: 1;
  padding: 24px 20px;
}

.type-tag {
  display: inline-block;
  background: #e0f2fe;
  color: #0284c7;
  font-size: 12px;
  font-weight: 700;
  padding: 5px 14px;
  border-radius: 14px;
  margin-bottom: 14px;
}

.q-title {
  margin: 0 0 24px;
  font-size: 21px;
  color: #0f172a;
  line-height: 1.5;
  font-weight: 800;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  background: white;
  border: 2px solid #edf1f7;
  border-radius: 20px;
  padding: 18px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
}

.option-item.selected {
  border-color: #0284c7;
  background: #f0f9ff;
  box-shadow: 0 4px 16px rgba(2, 132, 199, 0.18);
}

.opt-key {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #eef2f7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 16px;
  color: #334155;
  flex-shrink: 0;
}

.option-item.multiple .opt-key { border-radius: 12px; }

.option-item.selected .opt-key {
  background: #0284c7;
  color: white;
}

.opt-text {
  flex: 1;
  font-size: 16px;
  color: #334155;
  font-weight: 600;
}

.opt-check {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: transparent;
  flex-shrink: 0;
}

.option-item.multiple .opt-check { border-radius: 10px; }

.option-item.selected .opt-check {
  background: #0284c7;
  border-color: #0284c7;
  color: white;
}

.quiz-footer {
  padding: 14px 20px 20px;
  background: white;
  border-top: 1px solid #f1f5f9;
  display: flex;
  gap: 12px;
}

.nav-btn {
  flex: 1;
  height: 54px;
  border-radius: 18px;
  border: 1.5px solid #e2e8f0;
  background: white;
  font-weight: 700;
  font-size: 16px;
  color: #334155;
  cursor: pointer;
}

.nav-btn:disabled { opacity: 0.4; }

.nav-btn.primary {
  background: linear-gradient(135deg, #0284c7, #6366f1);
  color: white;
  border: none;
  box-shadow: 0 6px 18px rgba(2, 132, 199, 0.35);
}

.nav-btn.submit {
  background: linear-gradient(135deg, #10b981, #14b8a6);
  color: white;
  border: none;
  box-shadow: 0 6px 18px rgba(16, 185, 129, 0.35);
}
</style>
