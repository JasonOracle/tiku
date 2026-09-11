/**
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[1. 彻底根除填空题 TypeError: Cannot read properties of undefined (reading '0') 崩溃：规范化兼容 fill/fill_in 与 short/short_answer 枚举，支持正则兼容多下划线切分题干；2. 增加 getFillAnswers 防御性保护兜底，杜绝数组未就绪异常；3. 升级提交答卷逻辑：精准接收接口回传的 record_id 直达报告页，解决提交后页面空白且无法进入已参加的Bug]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[1. 彻底解决做题页面不渲染题目选项Bug：规范化兼容后端 single_choice、multiple_choice、judge 等完整枚举，并加入 getNormalizedOptions 智能解析字符串/对象多格式选项; 2. 移除顶栏练习模式硬编码标签，改为展示不限时; 3. 优化已提交拦截与AppModal挂载层级，防止已提交用户进入白屏]
 * 修改时间：2026-09-11
 * AI模型：Codex 3
 * 修改内容：[1. 新增移动端半屏答题卡抽屉：进度条与底部"答题卡"双入口，方块网格展示全部题目作答状态（白色底+阴影，已答浅蓝，当前题蓝色描边+数字）；点击任意方块跳转对应题目并自动收起弹窗；顶部图例+底部已答/未答统计；纯 CSS 动画无第三方库]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[防作弊：计时锚定服务端 started_at/server_now，删除超限清零后门；用时由服务端结算]
 */
<template>
  <div class="task-page-root">
    <div class="quiz-container" v-if="record">
      <!-- 顶栏：返回 + 标题 + 倒计时 -->
      <header class="quiz-header">
        <button class="back-btn" @click="confirmExit">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>

        <span class="quiz-title">{{ record.title || '在线任务' }}</span>

        <div class="header-right">
          <div v-if="record.is_timed || record.end_time" class="timer-pill" :class="{ warning: remainingSeconds < 180 }">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            <span>{{ formattedTime }}</span>
          </div>
          <span v-else class="practice-tag">不限时作答</span>
        </div>
      </header>

      <!-- 主答题卡片区域 (对齐 MBTI 布局) -->
      <main class="main-ctx">
        <div class="answer-con" v-if="currentQuestion">
          <!-- 顶部装饰挂条 (绝对定位上浮，间距与负 margin 匹配) -->
          <div class="bar"></div>

          <!-- 进度与统计 -->
          <div class="statis-con" @click="toggleQuestionNavigator">
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

        <!-- 客观题选项 (无外边框，选中刷色填充) -->
        <div v-if="isObjective" class="options">
          <div
            v-for="opt in normalizedCurrentOptions"
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

        <!-- 填空题: 题干下划线占位与输入框交替渲染 (兼容2个及以上下划线，使用 getFillAnswers 防御性保护) -->
        <div v-else-if="isFill" class="fill-block">
          <div class="fill-line">
            <template v-for="(seg, idx) in fillSegments" :key="idx">
              <span v-if="seg" class="fill-seg">{{ seg }}</span>
              <input
                v-if="idx < fillSegments.length - 1"
                v-model="getFillAnswers(currentQuestion.id)[idx]"
                class="fill-input"
                type="text"
                placeholder="填空"
                @input="markFillAnswered"
              />
            </template>
          </div>
        </div>

        <!-- 简答题: 多行文本 -->
        <div v-else-if="isShort" class="short-block">
          <textarea
            v-model="shortAnswers[currentQuestion.id]"
            class="short-input"
            rows="6"
            placeholder="在此输入你的答案（主观作答将由管理员/AI 核验，提交后暂不出分）"
          ></textarea>
        </div>

        <!-- 底部操作流 (包含上一题 / 下一题 / 交卷) -->
        <div class="action">
          <div v-if="currentIndex > 0" class="action-item action-left" @click="prevQuestion">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
            <span>上一题</span>
          </div>

          <button class="action-item action-nav-trigger" @click="toggleQuestionNavigator">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="7" height="7" rx="1.5"></rect>
              <rect x="14" y="3" width="7" height="7" rx="1.5"></rect>
              <rect x="3" y="14" width="7" height="7" rx="1.5"></rect>
              <rect x="14" y="14" width="7" height="7" rx="1.5"></rect>
            </svg>
            <span>答题卡</span>
          </button>

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
  </div>

    <!-- 移动端答题卡抽屉：半屏从底部滑入，点击方块跳转对应题目后自动收起 -->
    <Transition name="drawer-mask">
      <div v-if="navigatorVisible" class="nav-mask" @click="closeNavigator"></div>
    </Transition>
    <Transition name="drawer-panel">
      <div v-if="navigatorVisible" class="nav-drawer">
        <div class="nav-handle"></div>
        <div class="nav-title">答题卡</div>
        <div class="nav-legend">
          <span class="legend-item"><i class="swatch swatch-answered"></i>已答</span>
          <span class="legend-item"><i class="swatch swatch-unanswered"></i>未答</span>
          <span class="legend-item"><i class="swatch swatch-current"></i>当前</span>
        </div>
        <div class="nav-grid">
          <button
            v-for="(q, idx) in questions"
            :key="q.id"
            class="nav-cell"
            :class="{
              'nav-cell-answered': isQuestionAnswered(q),
              'nav-cell-current': idx === currentIndex
            }"
            @click="jumpToQuestion(idx)"
          >
            <span class="nav-cell-num">{{ idx + 1 }}</span>
          </button>
        </div>
        <div class="nav-footer">
          <span>已答 {{ answeredCount }} / 未答 {{ questions.length - answeredCount }}</span>
          <span class="nav-footer-total">共 {{ questions.length }} 题</span>
        </div>
      </div>
    </Transition>

    <!-- 通用视觉高级弹窗（置于外层根节点，无论是否开考或拦截均能正常渲染） -->
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
// v1.2 填空/简答作答态
const fillAnswers = reactive<Record<string, string[]>>({});
const shortAnswers = reactive<Record<string, string>>({});
const remainingSeconds = ref(0);
let timerId: any = null;
const submitting = ref(false);
const isFinished = ref(false);
const recordIdForSubmit = ref<number | null>(null);
const taskIdForSubmit = ref<number | null>(null);
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

// 答题卡抽屉状态
const navigatorVisible = ref(false);

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

// 判断某题是否已作答（与交卷判定逻辑保持一致）：客观看选项、填空看逐空、简答看文本
const isQuestionAnswered = (q: any) => {
  const qid = String(q.id);
  if (['fill', 'fill_in'].includes(q.type)) {
    return (fillAnswers[qid] || []).some((v) => (v || '').trim().length > 0);
  }
  if (['short', 'short_answer'].includes(q.type)) {
    return (shortAnswers[qid] || '').trim().length > 0;
  }
  return (userAnswers[qid] || []).length > 0;
};

const answeredCount = computed(() => questions.value.filter((q) => isQuestionAnswered(q)).length);

const toggleQuestionNavigator = () => {
  navigatorVisible.value = true;
};

const closeNavigator = () => {
  navigatorVisible.value = false;
};

// 点击答题卡方块：跳转目标题并自动收起抽屉
const jumpToQuestion = (idx: number) => {
  if (idx < 0 || idx >= questions.value.length) return;
  currentIndex.value = idx;
  closeNavigator();
};

const formattedTime = computed(() => {
  const m = Math.floor(remainingSeconds.value / 60);
  const s = remainingSeconds.value % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
});

const getTypeLabel = (type: string) => {
  if (['single', 'single_choice'].includes(type)) return '单选题';
  if (['multiple', 'multiple_choice'].includes(type)) return '多选题';
  if (['fill', 'fill_in'].includes(type)) return '填空题';
  if (['short', 'short_answer'].includes(type)) return '简答题';
  if (['judge', 'true_false'].includes(type)) return '判断题';
  return '选择题';
};

const isObjective = computed(() => {
  const t = currentQuestion.value?.type;
  return ['single', 'single_choice', 'multiple', 'multiple_choice', 'judge', 'true_false'].includes(t);
});
const isFill = computed(() => ['fill', 'fill_in'].includes(currentQuestion.value?.type));
const isShort = computed(() => ['short', 'short_answer'].includes(currentQuestion.value?.type));

// 规范化当前题目的选项列表：无论后端返回的是对象数组 [{key, text}] 还是字符串数组 ['A. 莫奈', 'B. 马奈']，均准确解构为 {key, text}
const normalizedCurrentOptions = computed((): Array<{ key: string; text: string }> => {
  if (!currentQuestion.value) return [];
  const qType = currentQuestion.value.type;
  const raw = currentQuestion.value.options;
  
  // 判断题若无选项字段，自动智能提供【正确 / 错误】标准客观选项
  if ((!raw || (Array.isArray(raw) && raw.length === 0)) && ['judge', 'true_false'].includes(qType)) {
    return [
      { key: 'A', text: '正确' },
      { key: 'B', text: '错误' }
    ];
  }

  if (!raw) return [];

  let opts = raw;
  if (typeof opts === 'string') {
    try {
      opts = JSON.parse(opts);
    } catch {
      return [];
    }
  }
  if (!Array.isArray(opts)) return [];

  const keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
  return opts.map((item: any, idx: number) => {
    if (typeof item === 'object' && item !== null) {
      const k = String(item.key || item.label || item.value || keys[idx] || '').trim().toUpperCase();
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
      key: keys[idx] || `Opt${idx + 1}`,
      text: str
    };
  });
});

// 填空题: 兼容 2 个及以上连续下划线（如 __, ___, ____）切分题干, 输入框与文字段交替渲染
const fillSegments = computed(() => {
  if (!currentQuestion.value) return [];
  const title = String(currentQuestion.value.title || '');
  return title.split(/_{2,}/);
});

// 防御性获取填空作答数组，彻底杜绝 TypeError: Cannot read properties of undefined (reading '0')
const getFillAnswers = (qId: number | string): string[] => {
  const key = String(qId);
  if (!fillAnswers[key]) {
    const title = String(currentQuestion.value?.title || '');
    const blanks = (title.match(/_{2,}/g) || []).length;
    fillAnswers[key] = Array.from({ length: Math.max(1, blanks) }, () => '');
  }
  return fillAnswers[key];
};

const markFillAnswered = () => {
  // v-model 已双向绑定 fillAnswers; 此钩子预留响应式触发
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

  if (['single', 'single_choice', 'judge', 'true_false'].includes(qType)) {
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
    const res: any = await http.get('/api/v1/member/favorites');
    const items = res?.items || res || [];
    const ids = new Set<number>();
    items.forEach((item: any) => {
      if (item.resource_id) ids.add(item.resource_id);
    });
    favQuestionIds.value = ids;
  } catch (e) {}
};

const toggleFavorite = async () => {
  if (!currentQuestion.value) return;
  const qId = currentQuestion.value.id;
  try {
    if (favQuestionIds.value.has(qId)) {
      await http.delete(`/api/v1/member/favorites/${qId}`);
      favQuestionIds.value.delete(qId);
      showAppModal('已从收藏夹中移除', 'success', '提示');
    } else {
      await http.post('/api/v1/member/favorites', { resource_id: qId });
      favQuestionIds.value.add(qId);
      showAppModal('收藏条目成功！', 'success', '成功');
    }
  } catch (err: any) {
    const detail = err?.response?.data?.detail;
    showAppModal(typeof detail === 'string' ? detail : '操作失败', 'danger', '错误');
  }
};

const handleManualSubmit = () => {
  // 未作答统计: 复用答题卡抽屉的同源判定 isQuestionAnswered（客观选项 + 填空逐空 + 简答文本）
  if (answeredCount.value < questions.value.length) {
    const unAnswered = questions.value.length - answeredCount.value;

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
    // 合并三类作答: 客观选项 / 填空逐空 / 简答文本 → [{resource_id, answer}]
    const answers: Array<{ resource_id: number; answer: any }> = [];
    questions.value.forEach((q) => {
      const qid = String(q.id);
      if (['fill', 'fill_in'].includes(q.type)) {
        const blanks = getFillAnswers(q.id);
        answers.push({ resource_id: q.id, answer: blanks.map((v) => (v == null ? '' : String(v))) });
      } else if (['short', 'short_answer'].includes(q.type)) {
        const text = (shortAnswers[qid] || '').trim();
        answers.push({ resource_id: q.id, answer: text });
      } else {
        answers.push({ resource_id: q.id, answer: userAnswers[q.id] || [] });
      }
    });

    const startTimeMs = startTimeForTimer.value
      ? new Date(startTimeForTimer.value.replace(' ', 'T')).getTime()
      : Date.now();
    const timeSpent = Math.max(1, Math.floor((Date.now() - (isNaN(startTimeMs) ? Date.now() : startTimeMs)) / 1000));

    const res: any = await http.post(`/api/v1/member/task-records/submit`, {
      task_id: taskIdForSubmit.value,
      time_spent: timeSpent,
      answers
    });

    isFinished.value = true;
    // 优先读取提交接口直接回传的 record_id，若无则兜底回查列表或使用本地初始 recordId
    let rid = res?.record_id || res?.data?.record_id || recordIdForSubmit.value;
    if (!rid) {
      try {
        const list: any = await http.get('/api/v1/member/task-records');
        const hit = (list.items || []).find((r: any) => r.task_id === taskIdForSubmit.value);
        if (hit) rid = hit.record_id;
      } catch (e) {}
    }
    router.replace(`/report?record_id=${rid}`);
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
  if (!record.value || (!record.value.is_timed && !record.value.end_time)) return;

  // 服务端权威计时：以服务端开考时刻 started_at + 服务端当前时间 server_now 为锚，
  // 本地仅做时钟偏移校正；改本地时间/伪造用时无法影响服务端结算
  const startedMs = new Date(String(record.value.started_at || '').replace(' ', 'T')).getTime();
  const serverMs = new Date(String(record.value.server_now || '').replace(' ', 'T')).getTime();
  const offset = Date.now() - (isNaN(serverMs) ? Date.now() : serverMs);
  const t0 = isNaN(startedMs) ? Date.now() - offset : startedMs;

  // 常规限时: time_limit - 服务端已耗时
  let byLimit = Infinity;
  if (record.value.is_timed) {
    const limitSeconds = (record.value.time_limit || 30) * 60;
    const elapsed = Math.max(0, Math.floor((Date.now() - offset - t0) / 1000));
    byLimit = Math.max(1, limitSeconds - elapsed);
  }

  // 截止硬边界: 距 end_time 的剩余时长（服务端时钟），取两者较小值
  let byWindow = Infinity;
  if (record.value.end_time) {
    const endMs = new Date(String(record.value.end_time).replace(' ', 'T')).getTime();
    byWindow = Math.floor((endMs - (Date.now() - offset)) / 1000);
  }

  remainingSeconds.value = Math.max(1, Math.min(byLimit, byWindow));

  if (timerId) clearInterval(timerId);
  timerId = setInterval(() => {
    if (remainingSeconds.value > 0) {
      remainingSeconds.value--;
    } else {
      clearInterval(timerId);
      timerId = null;
      // 考试时间到: 自动强制收卷
      executeSubmit();
    }
  }, 1000);
};

onMounted(async () => {
  const taskId = Number(route.query.task_id || route.query.exam_id);
  if (!taskId) {
    isFinished.value = true;
    router.push('/');
    return;
  }
  taskIdForSubmit.value = taskId;
  try {
    const entry: any = await http.get(`/api/v1/member/tasks/${taskId}/entry`);
    if (entry.my_status && entry.my_status !== 'pending') {
      showAppModal('该任务已提交，不可重复作答', 'warning', '提示', false, '查看结果', () => {
        isFinished.value = true;
        router.replace(`/report?record_id=${entry.my_record_id}`);
      });
      return;
    }
    record.value = entry;
    recordIdForSubmit.value = entry.my_record_id ?? null;
    startTimeForTimer.value = new Date().toISOString();

    const loadedQuestions = entry.questions || [];
    questions.value = loadedQuestions;

    // 初始化填空题逐空作答数组 (按题干连续下划线数量兼容)
    loadedQuestions.forEach((q: any) => {
      const qid = String(q.id);
      if (['fill', 'fill_in'].includes(q.type)) {
        const blanks = (String(q.title || '').match(/_{2,}/g) || []).length;
        fillAnswers[qid] = Array.from({ length: Math.max(1, blanks) }, () => '');
      }
      if (['short', 'short_answer'].includes(q.type)) {
        shortAnswers[qid] = '';
      }
    });

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

/* 填空题: 文字与输入框交替一行流式渲染 */
.fill-block {
  margin-bottom: 30px;
}

.fill-line {
  font-size: 16px;
  font-weight: 600;
  color: #111111;
  line-height: 2.4;
  word-break: break-all;
}

.fill-seg {
  white-space: pre-wrap;
}

.fill-input {
  display: inline-block;
  width: 110px;
  margin: 0 4px;
  padding: 6px 10px;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  text-align: center;
  border: none;
  border-bottom: 2.5px solid #ffce09;
  background: #fffdf2;
  outline: none;
  border-radius: 6px 6px 0 0;
}

.fill-input:focus {
  background: #fff8d6;
}

/* 简答题: 多行文本 */
.short-block {
  margin-bottom: 30px;
}

.short-input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  font-size: 15px;
  font-weight: 500;
  color: #0f172a;
  line-height: 1.7;
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  background: #f8fafc;
  resize: none;
  outline: none;
  font-family: inherit;
}

.short-input:focus {
  border-color: #ffce09;
  background: #fffdf2;
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

/* 底部"答题卡"入口按钮：白底轻描边，与交卷结算胶囊形成层级对比 */
.action-nav-trigger {
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  color: #293c5f;
  padding: 9px 18px;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(41, 60, 95, 0.08);
  font-size: 14px;
}

/* 答题卡抽屉（移动端半屏，从底部滑入） */
.nav-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  z-index: 90;
}

.nav-drawer {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 100;
  max-width: 480px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 20px 20px 0 0;
  padding: 10px 18px calc(18px + env(safe-area-inset-bottom));
  box-shadow: 0 -12px 32px rgba(41, 60, 95, 0.18);
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 60vh;
}

.nav-handle {
  width: 44px;
  height: 5px;
  border-radius: 3px;
  background: #e2e8f0;
  margin: 0 auto;
}

.nav-title {
  font-size: 16px;
  font-weight: 800;
  color: #0f172a;
  text-align: center;
}

.nav-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.swatch {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 4px;
}

.swatch-answered {
  background: #dbeafe;
  border: 1.5px solid #93c5fd;
}

.swatch-unanswered {
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 1px 2px rgba(41, 60, 95, 0.08);
}

.swatch-current {
  background: #ffffff;
  border: 2px solid #4fa7ff;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  overflow-y: auto;
  max-height: 260px;
  padding: 4px;
}

.nav-cell {
  position: relative;
  aspect-ratio: 1;
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(41, 60, 95, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.15s ease, background 0.2s ease, border-color 0.2s ease;
  padding: 0;
}

.nav-cell:active {
  transform: scale(0.94);
}

.nav-cell-answered {
  background: #dbeafe;
  border-color: #93c5fd;
}

.nav-cell-current {
  border: 2px solid #4fa7ff;
  background: #eff6ff;
  box-shadow: 0 0 0 3px rgba(79, 167, 255, 0.18);
}

.nav-cell-current.nav-cell-answered {
  background: #dbeafe;
}

.nav-cell-num {
  font-size: 15px;
  font-weight: 800;
  color: #475569;
}

.nav-cell-current .nav-cell-num {
  color: #1d4ed8;
}

.nav-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  border-top: 1px solid #f1f5f9;
  padding-top: 12px;
}

.nav-footer-total {
  color: #64748b;
}

/* 抽屉过渡动画：遮罩淡入淡出 + 面板从底部滑入滑出 */
.drawer-mask-enter-active,
.drawer-mask-leave-active {
  transition: opacity 0.25s ease;
}

.drawer-mask-enter-from,
.drawer-mask-leave-to {
  opacity: 0;
}

.drawer-panel-enter-active,
.drawer-panel-leave-active {
  transition: transform 0.28s cubic-bezier(0.33, 1, 0.68, 1);
}

.drawer-panel-enter-from,
.drawer-panel-leave-to {
  transform: translateY(100%);
}

</style>
