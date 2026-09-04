/**
 * [变更日志]
 * 修改时间：2026-09-04
 * AI模型：Gemini 系列
 * 修改内容：[1. 完全对齐 MBTI UI 规范：修复顶部饰条重叠Bug，选项采用纯色/刷色无边框设计; 2. 上一题/下一题移入卡片内或悬浮操作流]
 */
<template>
  <div class="quiz-container" v-if="record">
    <!-- 顶栏：返回 + 标题 + 倒计时 -->
    <header class="quiz-header">
      <button class="back-btn" @click="confirmExit">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>

      <span class="quiz-title">{{ record.exam_title || '在线测评' }}</span>

      <div class="header-right">
        <div v-if="record.is_timed" class="timer-pill" :class="{ warning: remainingSeconds < 180 }">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          <span>{{ formattedTime }}</span>
        </div>
        <span v-else class="practice-tag">练习模式</span>
      </div>
    </header>

    <!-- 主答题卡片区域 (对齐 MBTI 布局) -->
    <main class="main-ctx">
      <div class="answer-con" v-if="currentQuestion">
        <!-- 顶部装饰挂条 (绝对定位上浮，间距与负 margin 匹配) -->
        <div class="bar"></div>

        <!-- 进度与统计 -->
        <div class="statis-con">
          <div class="statis">
            <span class="curr">{{ currentIndex + 1 }}</span>
            <span class="total">/{{ questions.length }}</span>
          </div>
          <div class="statis-progress">
            <div class="progress-inner" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>

        <!-- 题型与题目正文 (题目未收藏时显示收藏按钮，已收藏时隐藏) -->
        <div class="question">
          <div class="question-header">
            <span class="type-badge">{{ getTypeLabel(currentQuestion.type) }}</span>
            <button v-if="!isCurrentFav" class="q-fav-btn" @click="toggleFavorite" title="收藏此题">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              <span>收藏此题</span>
            </button>
          </div>
          <p class="q-text">{{ currentQuestion.title }}</p>
        </div>

        <!-- 选项列表 (无外边框，选中刷色填充) -->
        <div class="options">
          <div
            v-for="opt in currentQuestion.options"
            :key="opt.key"
            class="option"
            :class="{ 'option-active': isOptionSelected(opt.key) }"
            @click="selectOption(opt.key)"
          >
            <span class="opt-prefix">{{ opt.key }}</span>
            <span class="opt-content">{{ opt.text }}</span>
            <span class="opt-icon" v-if="isOptionSelected(opt.key)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
          </div>
        </div>

        <!-- 底部操作流 (包含上一题 / 下一题 / 交卷) -->
        <div class="action">
          <div v-if="currentIndex > 0" class="action-item action-left" @click="prevQuestion">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
            <span>上一题</span>
          </div>
          <div v-else></div>

          <div v-if="currentIndex < questions.length - 1" class="action-item action-right" @click="nextQuestion">
            <span>下一题</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>

          <button v-else class="action-item action-report" :disabled="submitting" @click="handleManualSubmit">
            {{ submitting ? '提交中...' : '交卷结算' }}
          </button>
        </div>
      </div>
    </main>

    <!-- 通用视觉高级弹窗 -->
    <AppModal
      v-model="modalVisible"
      :title="modalTitle"
      :message="modalMessage"
      :type="modalType"
      :showCancel="modalShowCancel"
      :confirmText="modalConfirmText"
      @confirm="onModalConfirm"
      @cancel="onModalCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router';
import http from '../../utils/http';
import AppModal from '../../components/AppModal.vue';

const route = useRoute();
const router = useRouter();

const record = ref<any>(null);
const questions = ref<any[]>([]);
const currentIndex = ref(0);
const userAnswers = reactive<Record<string, string[]>>({});
const remainingSeconds = ref(0);
let timerId: any = null;
const submitting = ref(false);
const isFinished = ref(false);
const recordIdForSubmit = ref<number | null>(null);
const startTimeForTimer = ref<string>('');
const favQuestionIds = ref<Set<number>>(new Set());

// 通用 Modal 响应状态
const modalVisible = ref(false);
const modalTitle = ref('提示');
const modalMessage = ref('');
const modalType = ref<'info' | 'warning' | 'success' | 'danger'>('info');
const modalShowCancel = ref(true);
const modalConfirmText = ref('确定');
const pendingAction = ref<(() => void) | null>(null);
const pendingCancelAction = ref<(() => void) | null>(null);

const showAppModal = (
  msg: string,
  type: 'info' | 'warning' | 'success' | 'danger' = 'info',
  title = '提示',
  showCancel = false,
  confirmText = '确定',
  onConfirm?: () => void,
  onCancel?: () => void
) => {
  modalTitle.value = title;
  modalMessage.value = msg;
  modalType.value = type;
  modalShowCancel.value = showCancel;
  modalConfirmText.value = confirmText;
  pendingAction.value = onConfirm || null;
  pendingCancelAction.value = onCancel || null;
  modalVisible.value = true;
};

const onModalConfirm = () => {
  if (pendingAction.value) {
    pendingAction.value();
    pendingAction.value = null;
  }
};

const onModalCancel = () => {
  if (pendingCancelAction.value) {
    pendingCancelAction.value();
    pendingCancelAction.value = null;
  }
};

const currentQuestion = computed(() => questions.value[currentIndex.value]);

const progressPercent = computed(() => {
  if (!questions.value.length) return 0;
  return Math.round(((currentIndex.value + 1) / questions.value.length) * 100);
});

const formattedTime = computed(() => {
  const m = Math.floor(remainingSeconds.value / 60);
  const s = remainingSeconds.value % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
});

const getTypeLabel = (type: string) => {
  if (type === 'single') return '单选题';
  if (type === 'multiple') return '多选题';
  return '判断题';
};

const isOptionSelected = (key: string) => {
  if (!currentQuestion.value) return false;
  const qId = currentQuestion.value.id;
  const selected = userAnswers[qId] || [];
  return selected.includes(key);
};

const selectOption = (key: string) => {
  if (!currentQuestion.value) return;
  const qId = currentQuestion.value.id;
  const qType = currentQuestion.value.type;

  if (qType === 'single' || qType === 'true_false') {
    userAnswers[qId] = [key];
    if (currentIndex.value < questions.value.length - 1) {
      setTimeout(() => {
        currentIndex.value++;
      }, 250);
    }
  } else {
    if (!userAnswers[qId]) {
      userAnswers[qId] = [];
    }
    const idx = userAnswers[qId].indexOf(key);
    if (idx > -1) {
      userAnswers[qId].splice(idx, 1);
    } else {
      userAnswers[qId].push(key);
    }
  }
};

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  }
};

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++;
  }
};

const confirmExit = () => {
  showAppModal(
    '确定要离开答题页面吗？未提交的答题进度可能会丢失。',
    'warning',
    '离开确认',
    true,
    '离开',
    () => {
      isFinished.value = true;
      router.back();
    }
  );
};

const isCurrentFav = computed(() => {
  if (!currentQuestion.value) return false;
  return favQuestionIds.value.has(currentQuestion.value.id);
});

const loadUserFavorites = async () => {
  try {
    const res: any = await http.get('/api/v1/favorites', { params: { size: 100 } });
    const items = res?.items || res || [];
    const ids = new Set<number>();
    items.forEach((item: any) => {
      if (item.question_id) ids.add(item.question_id);
    });
    favQuestionIds.value = ids;
  } catch (e) {}
};

const toggleFavorite = async () => {
  if (!currentQuestion.value) return;
  const qId = currentQuestion.value.id;
  try {
    if (favQuestionIds.value.has(qId)) {
      await http.delete(`/api/v1/favorites/${qId}`);
      favQuestionIds.value.delete(qId);
      showAppModal('已从收藏夹中移除', 'success', '提示');
    } else {
      await http.post('/api/v1/favorites', { question_id: qId });
      favQuestionIds.value.add(qId);
      showAppModal('收藏题目成功！', 'success', '成功');
    }
  } catch (err: any) {
    const detail = err?.response?.data?.detail;
    showAppModal(typeof detail === 'string' ? detail : '操作失败', 'danger', '错误');
  }
};

const handleManualSubmit = () => {
  const answeredCount = Object.keys(userAnswers).filter(
    (key) => userAnswers[key] && userAnswers[key].length > 0
  ).length;

  if (answeredCount < questions.value.length) {
    const unAnswered = questions.value.length - answeredCount;
    showAppModal(
      `您还有 ${unAnswered} 道题未作答，确定要直接交卷结算吗？`,
      'warning',
      '未作答提示',
      true,
      '直接交卷',
      () => {
        executeSubmit();
      }
    );
  } else {
    executeSubmit();
  }
};

const executeSubmit = async () => {
  if (submitting.value || isFinished.value) return;
  submitting.value = true;
  try {
    const formattedUserAnswers: Record<string, string[]> = {};
    questions.value.forEach((q) => {
      formattedUserAnswers[String(q.id)] = userAnswers[q.id] || [];
    });

    const startTimeMs = startTimeForTimer.value 
      ? new Date(startTimeForTimer.value.replace(' ', 'T')).getTime() 
      : Date.now();
    const timeSpent = Math.max(1, Math.floor((Date.now() - (isNaN(startTimeMs) ? Date.now() : startTimeMs)) / 1000));

    const res: any = await http.post(`/api/v1/records/submit`, {
      record_id: recordIdForSubmit.value,
      user_answers: formattedUserAnswers,
      time_spent: timeSpent
    });

    isFinished.value = true;
    router.replace(`/report?record_id=${res.record_id || recordIdForSubmit.value}`);
  } catch (err: any) {
    submitting.value = false;
    const detail = err?.response?.data?.detail;
    let errorMsg = '交卷失败，请重试';
    if (typeof detail === 'string') {
      errorMsg = detail;
    } else if (Array.isArray(detail)) {
      errorMsg = detail.map((d: any) => d.msg || JSON.stringify(d)).join('; ');
    } else if (detail && typeof detail === 'object') {
      errorMsg = JSON.stringify(detail);
    } else if (err?.message) {
      errorMsg = err.message;
    }
    showAppModal(errorMsg, 'danger', '交卷失败');
  }
};

const startTimer = () => {
  if (!record.value || !record.value.is_timed) return;
  const limitSeconds = (record.value.time_limit || 30) * 60;
  
  let elapsed = 0;
  if (startTimeForTimer.value) {
    const parsedStart = new Date(startTimeForTimer.value.replace(' ', 'T')).getTime();
    if (!isNaN(parsedStart)) {
      elapsed = Math.max(0, Math.floor((Date.now() - parsedStart) / 1000));
    }
  }

  if (elapsed >= limitSeconds) {
    elapsed = 0;
  }

  remainingSeconds.value = Math.max(1, limitSeconds - elapsed);

  if (timerId) clearInterval(timerId);
  timerId = setInterval(() => {
    if (remainingSeconds.value > 0) {
      remainingSeconds.value--;
    } else {
      clearInterval(timerId);
      timerId = null;
      executeSubmit();
    }
  }, 1000);
};

onMounted(async () => {
  const examId = route.query.exam_id;
  if (!examId) {
    isFinished.value = true;
    router.push('/');
    return;
  }
  try {
    const startRes: any = await http.post('/api/v1/records/start', { exam_id: Number(examId) });
    record.value = startRes;
    
    let loadedQuestions = startRes.questions || [];
    if (startRes.is_random && loadedQuestions.length > 1) {
      const shuffled = [...loadedQuestions];
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      loadedQuestions = shuffled;
    }
    
    questions.value = loadedQuestions;
    recordIdForSubmit.value = startRes.record_id;
    startTimeForTimer.value = startRes.start_time;

    loadUserFavorites();
    startTimer();
  } catch (err) {
    isFinished.value = true;
    router.push('/');
  }
});

onUnmounted(() => {
  if (timerId) {
    clearInterval(timerId);
    timerId = null;
  }
});

onBeforeRouteLeave((to, from, next) => {
  if (isFinished.value) {
    next();
  } else {
    showAppModal(
      '离开页面将丢失未保存的答题进度，确定离开吗？',
      'warning',
      '离开确认',
      true,
      '确定离开',
      () => {
        isFinished.value = true;
        next();
      },
      () => {
        next(false);
      }
    );
  }
});
</script>

<style scoped>
.quiz-container {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: #ebf6fe;
  display: flex;
  flex-direction: column;
}

.quiz-header {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
}

.back-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #0f172a;
  padding: 0;
  display: flex;
  align-items: center;
}

.quiz-title {
  flex: 1;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
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
  font-weight: 700;
}

.fav-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.2s ease;
}

.fav-btn.active {
  background: #fffbe0;
  border-color: #fde68a;
  color: #f59e0b;
}

.practice-tag {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 600;
}

.main-ctx {
  flex: 1;
  padding: 32px 16px 24px;
}

.answer-con {
  position: relative;
  background: #ffffff;
  border-radius: 24px;
  padding: 36px 20px 24px;
  box-shadow: 0 10px 30px rgba(41, 60, 95, 0.08);
}

.bar {
  position: absolute;
  top: -8px;
  left: 16px;
  right: 16px;
  height: 16px;
  background: linear-gradient(90deg, #aab0ff, #7e6dff);
  border-radius: 10px;
  z-index: 1;
}

.statis-con {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 20px;
}

.statis {
  font-size: 26px;
  font-weight: 800;
  color: #111111;
  line-height: 1;
}

.statis .curr { color: #0f172a; }
.statis .total {
  font-size: 15px;
  color: #999999;
  font-weight: 400;
  margin-left: 2px;
}

.statis-progress {
  flex: 1;
  height: 12px;
  background: #f4f4f4;
  border-radius: 10px;
  overflow: hidden;
}

.progress-inner {
  height: 100%;
  background: linear-gradient(90deg, #ffe958, #ffce09);
  border-radius: 10px;
  transition: width 0.4s ease;
}

.question { margin-bottom: 24px; }

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.type-badge {
  display: inline-block;
  background: #e0f2fe;
  color: #0284c7;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 8px;
}

.q-fav-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.q-fav-btn.active {
  background: #fffbe0;
  border-color: #fde68a;
  color: #d97706;
}

.q-text {
  font-size: 17px;
  font-weight: 700;
  color: #111111;
  line-height: 1.5;
  margin: 0;
}

/* 选项（完全匹配 MBTI：无外框线，纯背景与黄色刷色填充） */
.options {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 30px;
}

.option {
  --fill-w: 0%;
  position: relative;
  background: #f8f8f8 linear-gradient(90deg, #ffe958, #ffce09) 0 0 / var(--fill-w) 100% no-repeat;
  border-radius: 14px;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  font-weight: 700;
  color: #555555;
  cursor: pointer;
  transition: color 0.3s ease, background-size 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
}

.option.option-active {
  --fill-w: 100%;
  color: #111111;
}

.opt-prefix {
  font-size: 16px;
  font-weight: 800;
  color: inherit;
}

.opt-content {
  flex: 1;
  line-height: 1.4;
  color: inherit;
}

.opt-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #111111;
}

/* 底部操作区（对齐 MBTI 的左右轻量级按钮布局） */
.action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 15px;
  font-weight: 700;
  color: #293c5f;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 8px 12px;
}

.action-item:active {
  opacity: 0.7;
}

.action-report {
  background: linear-gradient(90deg, #7f84fe, #4fa7ff);
  color: white;
  padding: 10px 24px;
  border-radius: 20px;
  box-shadow: 0 4px 14px rgba(127, 132, 254, 0.35);
}
</style>
