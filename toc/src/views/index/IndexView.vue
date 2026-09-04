<!--
 * [变更日志]
 * 修改时间：2026-09-04
 * AI模型：Gemini 系列
 * 修改内容：[1. 现代扁平拟物风格重构首页试卷列表：左侧精简封面微框，中间平铺展示模式与轻量指标，右侧蓝紫渐变做题胶囊按钮; 2. 解决原列表高占比挤压、竖向对齐噪音与覆盖错位问题]
 -->
<template>
  <div class="mobile-container">
    <!-- Header：居中程序名 -->
    <header class="top-bar centered">
      <h1 class="app-title">题库</h1>
    </header>

    <!-- Banner 轮播（有配置时替代 Hero） -->
    <BannerCarousel v-if="banners.length" :items="banners" :interval="bannerInterval" />

    <!-- Hero 精选推荐卡片（无 Banner 时回退） -->
    <section v-else class="hero-section">
      <div class="hero-card">
        <div class="hero-main">
          <div class="hero-tag"><span class="diamond">◆</span> FEATURED</div>
          <h2 class="hero-title">{{ heroExam?.title || '2026 消防安全与自救知识全能测评' }}</h2>
          <p class="hero-desc">{{ heroDesc }}</p>
          <button class="hero-btn" @click="startExam(heroExam?.id)">
            立即挑战
            <span class="arrow-circle">→</span>
          </button>
        </div>
        <div class="hero-art">
          <CoverArt :cover="heroExam?.cover_url || 'preset:1'" width="120px" height="150px" />
        </div>
      </div>
    </section>

    <!-- 分类横向滚动 Pill -->
    <nav class="category-scroll">
      <button class="cat-pill" :class="{ active: selectedCat === null }" @click="selectCategory(null)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/></svg>
        全部精选
      </button>
      <button
        v-for="(cat, i) in categories"
        :key="cat.id"
        class="cat-pill"
        :class="{ active: selectedCat === cat.id }"
        @click="selectCategory(cat.id)"
      >
        <span v-html="catIcon(i)"></span>
        {{ cat.name }}
      </button>
    </nav>

    <!-- 试卷列表 -->
    <main class="exam-list">
      <div v-for="exam in exams" :key="exam.id" class="exam-card" @click="startExam(exam.id)">
        <div class="card-thumb">
          <CoverArt :cover="exam.cover_url || 'preset:1'" width="56px" height="56px" />
        </div>
        <div class="card-info">
          <div class="card-badge-row">
            <span class="mode-tag" :class="exam.is_timed ? 'timed' : 'practice'">
              <svg v-if="exam.is_timed" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
              {{ exam.is_timed ? `${exam.time_limit}分钟限时` : '练习模式' }}
            </span>
          </div>
          <h3 class="exam-title">{{ exam.title }}</h3>
          <div class="meta-chips">
            <span class="chip">
              <span class="chip-label">题目</span>
              <span class="chip-val">{{ exam.question_count }}题</span>
            </span>
            <span class="chip-dot">•</span>
            <span class="chip">
              <span class="chip-label">总分</span>
              <span class="chip-val">{{ exam.total_score }}分</span>
            </span>
            <span class="chip-dot">•</span>
            <span class="chip">
              <span class="chip-label">及格</span>
              <span class="chip-val">{{ exam.pass_score }}分</span>
            </span>
          </div>
        </div>
        <div class="card-action">
          <button class="action-btn" @click.stop="startExam(exam.id)">
            <span>做题</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>
      </div>
    </main>

    <TabBar active="home" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import http from '../../utils/http';
import { useUserStore } from '../../store/user';
import TabBar from '../../components/TabBar.vue';
import BannerCarousel from '../../components/BannerCarousel.vue';
import CoverArt from '../../components/CoverArt.vue';

const router = useRouter();
const userStore = useUserStore();

const username = computed(() => userStore.username);
const categories = ref<any[]>([]);
const exams = ref<any[]>([]);
const selectedCat = ref<number | null>(null);
const banners = ref<any[]>([]);
const bannerInterval = ref(4);

const CAT_ICONS = [
  '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2c1 4-2 5-2 8a4 4 0 0 0 8 0c0-2-1-3-1-3s3 2 3 6a7 7 0 0 1-14 0c0-5 5-7 6-11z"/></svg>',
  '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>',
  '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.5 2.5L16 9.5"/></svg>',
  '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.5" y2="9.5"/><line x1="15" y1="9" x2="14.5" y2="9.5"/></svg>'
];
const catIcon = (i: number) => CAT_ICONS[i % CAT_ICONS.length];

const heroExam = computed(() => exams.value.find((e) => e.is_recommended) || exams.value[0] || null);
const heroDesc = computed(() => {
  if (!heroExam.value) return '精选试卷等你来战';
  return heroExam.value.is_timed ? `限时 ${heroExam.value.time_limit} 分钟闭卷测试` : '不限时练习，随时开刷';
});

const loadBanners = async () => {
  try {
    const res: any = await http.get('/api/v1/banners');
    banners.value = res.items || [];
    bannerInterval.value = res.interval_seconds || 4;
  } catch (e) {
    banners.value = [];
  }
};

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
  } catch (e) {}
};

const selectCategory = (catId: number | null) => {
  selectedCat.value = catId;
  loadExams();
};

const handleUserClick = () => {
  router.push(userStore.token ? '/profile' : '/login');
};

const startExam = async (examId?: number) => {
  if (!examId) return;
  if (!userStore.token) {
    router.push('/login');
    return;
  }
  router.push({ path: '/quiz', query: { exam_id: examId } });
};

onMounted(() => {
  loadBanners();
  loadCategories();
  loadExams();
});
</script>

<style scoped>
.mobile-container {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(180deg, #eef4ff 0%, #f8fafc 40%);
  padding-bottom: 140px; /* 增加底部安全区防止导航遮挡 */
  box-sizing: border-box;
  font-family: 'Plus Jakarta Sans', 'Outfit', system-ui, sans-serif;
}

.top-bar { padding: 14px 20px 4px; display: flex; align-items: center; }

.app-title { font-size: 20px; font-weight: 800; color: #0f172a; margin: 0; }

.top-bar.centered { justify-content: center; }

.hero-section { padding: 10px 20px 0; }

.hero-card {
  background: linear-gradient(120deg, #38bdf8 0%, #6366f1 60%, #a855f7 100%);
  border-radius: 26px;
  padding: 22px;
  color: white;
  display: flex;
  gap: 12px;
  box-shadow: 0 14px 34px rgba(99, 102, 241, 0.35);
  position: relative;
  overflow: hidden;
}

.hero-main { flex: 1; min-width: 0; }

.hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid rgba(255, 255, 255, 0.55);
  padding: 4px 12px;
  border-radius: 14px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1px;
}

.diamond { font-size: 10px; }

.hero-title {
  margin: 12px 0 8px;
  font-size: 21px;
  font-weight: 800;
  line-height: 1.35;
}

.hero-desc { font-size: 13px; opacity: 0.92; margin: 0 0 16px; }

.hero-btn {
  background: white;
  color: #0284c7;
  border: none;
  padding: 10px 10px 10px 20px;
  border-radius: 18px;
  font-weight: 800;
  font-size: 15px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.arrow-circle {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
}

.hero-art { flex-shrink: 0; align-self: center; opacity: 0.95; }

.category-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 16px 20px;
  scrollbar-width: none;
}
.category-scroll::-webkit-scrollbar { display: none; }

.cat-pill {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: white;
  border: 1px solid #eef2f7;
  padding: 9px 16px;
  border-radius: 18px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.cat-pill.active {
  background: linear-gradient(135deg, #0284c7, #6366f1);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);
}

.exam-list {
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.exam-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.04), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
}

.exam-card:active {
  transform: scale(0.985);
  box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.03);
}

.card-thumb {
  width: 62px;
  height: 62px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: 3px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.9), 0 4px 10px rgba(99, 102, 241, 0.06);
}

.card-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.card-badge-row {
  display: flex;
  align-items: center;
}

.mode-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
}

.mode-tag.timed {
  background: #fff1f2;
  color: #e11d48;
}

.mode-tag.practice {
  background: #f0f9ff;
  color: #0284c7;
}

.exam-title {
  margin: 3px 0 2px;
  font-size: 15px;
  color: #0f172a;
  font-weight: 800;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta-chips {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.chip-label {
  color: #94a3b8;
  font-size: 11px;
}

.chip-val {
  color: #334155;
  font-weight: 700;
  font-size: 12px;
}

.chip-dot {
  color: #cbd5e1;
  font-size: 10px;
}

.card-action {
  flex-shrink: 0;
  align-self: center;
}

.action-btn {
  background: linear-gradient(135deg, #0284c7 0%, #6366f1 100%);
  color: #ffffff;
  border: none;
  padding: 8px 14px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.28);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.action-btn:active {
  transform: scale(0.95);
}
</style>
