<!--
 * [变更日志]
 * 修改时间：2026-09-03
 * AI模型：Gemini 底层
 * 修改内容：[1. 实现 C 端移动端毛玻璃拟态首页与 Hero 精选试卷推荐; 2. 避免 Emoji 使用标准 SVG 图标]
-->
<template>
  <div class="mobile-container">
    <!-- Header 区域 -->
    <header class="top-bar">
      <div class="user-pill" @click="handleUserClick">
        <div class="avatar-badge">{{ username ? username.substring(0, 1).toUpperCase() : 'U' }}</div>
        <span class="user-name">{{ username || '点击登录' }}</span>
      </div>
      <button class="fav-icon-btn" @click="router.push('/favorite')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
        </svg>
      </button>
    </header>

    <!-- Hero 精选推荐卡片 -->
    <section class="hero-section">
      <div class="hero-card">
        <div class="hero-tag">FEATURED</div>
        <h2 class="hero-title">2026 消防安全与自救知识全能测评</h2>
        <p class="hero-desc">全站近千名用户参与作答，限时 15 分钟闭卷测试</p>
        <button class="hero-btn" @click="startExam(recommendedExamId || 1)">立即挑战</button>
      </div>
    </section>

    <!-- 分类横向滚动 Pill -->
    <nav class="category-scroll">
      <button 
        class="cat-pill" 
        :class="{ active: selectedCat === null }"
        @click="selectCategory(null)"
      >
        全部精选
      </button>
      <button 
        v-for="cat in categories" 
        :key="cat.id"
        class="cat-pill"
        :class="{ active: selectedCat === cat.id }"
        @click="selectCategory(cat.id)"
      >
        {{ cat.name }}
      </button>
    </nav>

    <!-- 试卷列表 -->
    <main class="exam-list">
      <div v-for="exam in exams" :key="exam.id" class="exam-card">
        <div class="card-body">
          <div class="title-row">
            <span class="mode-badge" :class="exam.is_timed ? 'timed' : 'practice'">
              {{ exam.is_timed ? `${exam.time_limit}分钟限时` : '练习模式' }}
            </span>
            <h3 class="exam-title">{{ exam.title }}</h3>
          </div>
          <div class="meta-row">
            <span>题目: {{ exam.question_count || 10 }} 题</span>
            <span>总分: {{ exam.total_score }} 分</span>
            <span>及格: {{ exam.pass_score }} 分</span>
          </div>
        </div>
        <button class="start-btn" @click="startExam(exam.id)">
          开始做题
        </button>
      </div>
    </main>

    <!-- 底部 TabBar -->
    <footer class="bottom-tabbar">
      <button class="tab-item active" @click="router.push('/')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
        </svg>
        <span>首页</span>
      </button>
      <button class="tab-item" @click="router.push('/favorite')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
        </svg>
        <span>收藏夹</span>
      </button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import http from '../../utils/http';
import { useUserStore } from '../../store/user';

const router = useRouter();
const userStore = useUserStore();

const username = computed(() => userStore.username);
const categories = ref<any[]>([]);
const exams = ref<any[]>([]);
const selectedCat = ref<number | null>(null);
const recommendedExamId = ref<number | null>(null);

const loadCategories = async () => {
  try {
    const res: any = await http.get('/api/v1/categories');
    categories.value = res || [];
  } catch (e) {}
};

const loadExams = async () => {
  try {
    const res: any = await http.get('/api/v1/exams', {
      params: { category_id: selectedCat.value }
    });
    exams.value = res.items || [];
    if (exams.value.length > 0) {
      recommendedExamId.value = exams.value[0].id;
    }
  } catch (e) {}
};

const selectCategory = (catId: number | null) => {
  selectedCat.value = catId;
  loadExams();
};

const handleUserClick = () => {
  if (!userStore.token) {
    router.push('/login');
  }
};

const startExam = (examId: number) => {
  if (!userStore.token) {
    router.push('/login');
    return;
  }
  router.push({ path: '/quiz', query: { exam_id: examId } });
};

onMounted(() => {
  loadCategories();
  loadExams();
});
</script>

<style scoped>
.mobile-container {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(180deg, #e0f2fe 0%, #f8fafc 30%);
  padding-bottom: 80px;
  box-sizing: border-box;
  font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
}

.top-bar {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  padding: 6px 14px 6px 6px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  cursor: pointer;
}

.avatar-badge {
  width: 28px;
  height: 28px;
  background: #0284c7;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.fav-icon-btn {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0284c7;
  cursor: pointer;
}

.hero-section {
  padding: 10px 20px;
}

.hero-card {
  background: linear-gradient(135deg, #0284c7 0%, #38bdf8 50%, #818cf8 100%);
  border-radius: 24px;
  padding: 24px;
  color: white;
  box-shadow: 0 12px 30px rgba(2, 132, 199, 0.25);
  position: relative;
  overflow: hidden;
}

.hero-tag {
  background: rgba(255, 255, 255, 0.2);
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1px;
}

.hero-title {
  margin: 12px 0 8px;
  font-size: 20px;
  font-weight: 800;
  line-height: 1.3;
}

.hero-desc {
  font-size: 13px;
  opacity: 0.9;
  margin: 0 0 16px;
}

.hero-btn {
  background: white;
  color: #0284c7;
  border: none;
  padding: 10px 20px;
  border-radius: 14px;
  font-weight: 700;
  cursor: pointer;
}

.category-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 16px 20px;
  scrollbar-width: none;
}

.cat-pill {
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  padding: 8px 16px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

.cat-pill.active {
  background: #0284c7;
  color: white;
  border-color: #0284c7;
}

.exam-list {
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.exam-card {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  padding: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
}

.mode-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 8px;
  margin-bottom: 6px;
  display: inline-block;
}

.mode-badge.timed {
  background: #fee2e2;
  color: #ef4444;
}

.mode-badge.practice {
  background: #e0f2fe;
  color: #0284c7;
}

.exam-title {
  margin: 0;
  font-size: 16px;
  color: #0f172a;
  font-weight: 700;
}

.meta-row {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #64748b;
  margin-top: 8px;
}

.start-btn {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 14px;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  flex-shrink: 0;
}

.bottom-tabbar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  height: 64px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(226, 232, 240, 0.8);
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.tab-item {
  background: transparent;
  border: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #94a3b8;
  font-size: 11px;
  cursor: pointer;
}

.tab-item.active {
  color: #0284c7;
  font-weight: 700;
}
</style>
