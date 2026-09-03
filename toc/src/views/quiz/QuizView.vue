<!--
 * [变更日志]
 * 修改时间：2026-09-03
 * AI模型：Gemini 底层
 * 修改内容：[1. 实现 C 端答题流引擎 (含限时倒计时、定时器卸载清理、上一题修改与一键收藏功能)]
-->
<template>
  <div class="quiz-container" v-if="record">
    <!-- 顶部进度与计时栏 -->
    <header class="quiz-header">
      <button class="back-btn" @click="confirmExit">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>

      <div class="progress-pill">
        <span>第 {{ currentIndex + 1 }} / {{ questions.length }} 题</span>
      </div>

      <div v-if="record.is_timed" class="timer-pill" :class="{ warning: remainingSeconds < 180 }">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <polyline points="12 6 12 12 16 14"></polyline>
        </svg>
        <span>{{ formattedTime }}</span>
      </div>

      <button class="fav-btn" :class="{ active: isCurrentFavorited }" @click="toggleFavorite">
        <svg width="20" height="20" viewBox="0 0 24 24" :fill="isCurrentFavorited ? '#0284c7' : 'none'" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
        </svg>
      </button>
    </header>

    <!-- 进度条 -->
    <div class="progress-bar-bg">
      <div class="progress-bar-fill" :style="{ width: `${((currentIndex + 1) / questions.length) * 100}%` }"></div>
    </div>

    <!-- 题目正文卡片 -->
    <main class="question-card" v-if="currentQuestion">
      <div class="type-tag">{{ getTypeLabel(currentQuestion.type) }}</div>
      <h3 class="q-title">{{ currentQuestion.title }}</h3>

      <div class="options-list">
        <div 
          v-for="opt in currentQuestion.options" 
          :key="opt.key" 
          class="option-item"
          :class="{ selected: isOptionSelected(opt.key) }"
          @click="selectOption(opt.key)"
        >
          <span class="opt-key">{{ opt.key }}</span>
          <span class="opt-text">{{ opt.text }}</span>
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
const favoritedQids = ref<Set<number>>(new Set());

const remainingSeconds = ref(0);
let timerId: any = null;
const submitting = ref(false);
const isFinished = ref(false); // 标记是否已完成交卷逻辑

const currentQuestion = computed(() => questions.value[currentIndex.value]);
const isCurrentFavorited = computed(() => {
  return currentQuestion.value ? favoritedQids.value.has(currentQuestion.value.id) : false;
});

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

const toggleFavorite = async () => {
  if (!currentQuestion.value) return;
  const qId = currentQuestion.value.id;
  if (favoritedQids.value.has(qId)) {
    await http.delete(`/api/v1/favorites/${qId}`);
    favoritedQids.value.delete(qId);
  } else {
    await http.post('/api/v1/favorites', { question_id: qId });
    favoritedQids.value.add(qId);
  }
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
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
}

.back-btn, .fav-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #64748b;
  display: flex;
  align-items: center;
}

.fav-btn.active {
  color: #0284c7;
}

.progress-pill {
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
}

.timer-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #e0f2fe;
  color: #0284c7;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
}

.timer-pill.warning {
  background: #fee2e2;
  color: #ef4444;
}

.progress-bar-bg {
  height: 4px;
  background: #e2e8f0;
  width: 100%;
}

.progress-bar-fill {
  height: 100%;
  background: #0284c7;
  transition: width 0.3s ease;
}

.question-card {
  flex: 1;
  padding: 24px 20px;
}

.type-tag {
  display: inline-block;
  background: #e0f2fe;
  color: #0284c7;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
  margin-bottom: 12px;
}

.q-title {
  margin: 0 0 24px;
  font-size: 18px;
  color: #0f172a;
  line-height: 1.4;
  font-weight: 700;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-item.selected {
  border-color: #0284c7;
  background: #f0f9ff;
}

.opt-key {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  color: #475569;
}

.option-item.selected .opt-key {
  background: #0284c7;
  color: white;
}

.opt-text {
  font-size: 15px;
  color: #334155;
  font-weight: 500;
}

.quiz-footer {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 12px;
}

.nav-btn {
  flex: 1;
  height: 48px;
  border-radius: 14px;
  border: 1px solid #cbd5e1;
  background: white;
  font-weight: 700;
  font-size: 14px;
  color: #475569;
  cursor: pointer;
}

.nav-btn.primary {
  background: #0284c7;
  color: white;
  border: none;
}

.nav-btn.submit {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
}
</style>
