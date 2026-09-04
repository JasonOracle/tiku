<!--
 * [变更日志]
 * 修改时间：2026-09-04
 * AI模型：OpenCode
 * 修改内容：[1. 按 首页.png 还原：头像Header/Hero蓝紫渐变/分类图标Pill/试卷卡三栏+封面/浮动TabBar(首页/个人中心); 2. Hero改绑推荐卷，Banner>0时轮播替代]
-->
<template>
  <div class="mobile-container">
    <!-- Header：头像圆 -->
    <header class="top-bar">
      <div class="avatar-circle" @click="handleUserClick">
        <span v-if="username">{{ username.substring(0, 1).toUpperCase() }}</span>
        <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
      </div>
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
      <div v-for="exam in exams" :key="exam.id" class="exam-card">
        <div class="card-body">
          <span class="mode-badge" :class="exam.is_timed ? 'timed' : 'practice'">
            {{ exam.is_timed ? `${exam.time_limit}分钟限时` : '练习模式' }}
          </span>
          <h3 class="exam-title">{{ exam.title }}</h3>
          <div class="meta-row">
            <span class="meta-item">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              <span class="meta-lbl">题目</span><strong>{{ exam.question_count }} 题</strong>
            </span>
            <span class="meta-item">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 21h8M12 17v4M7 4h10v6a5 5 0 0 1-10 0V4z"/></svg>
              <span class="meta-lbl">总分</span><strong>{{ exam.total_score }} 分</strong>
            </span>
            <span class="meta-item">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="0.5" fill="currentColor"/></svg>
              <span class="meta-lbl">及格</span><strong>{{ exam.pass_score }} 分</strong>
            </span>
          </div>
        </div>
        <div class="card-side">
          <CoverArt :cover="exam.cover_url || 'preset:1'" width="86px" height="104px" />
          <button class="start-btn" @click="startExam(exam.id)">开始做题 ›</button>
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

const startExam = (examId?: number) => {
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
  padding-bottom: 100px;
  box-sizing: border-box;
  font-family: 'Plus Jakarta Sans', 'Outfit', system-ui, sans-serif;
}

.top-bar { padding: 14px 20px 4px; display: flex; align-items: center; }

.avatar-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #38bdf8, #6366f1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  border: 2px solid white;
}

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

.exam-list { padding: 0 20px; display: flex; flex-direction: column; gap: 14px; }

.exam-card {
  background: white;
  border-radius: 22px;
  padding: 16px;
  display: flex;
  gap: 12px;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
}

.card-body { flex: 1; min-width: 0; }

.mode-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 8px;
  display: inline-block;
}

.mode-badge.timed { background: #fee2e2; color: #ef4444; }
.mode-badge.practice { background: #e0f2fe; color: #0284c7; }

.exam-title {
  margin: 8px 0 10px;
  font-size: 17px;
  color: #0f172a;
  font-weight: 800;
  line-height: 1.35;
}

.meta-row { display: flex; gap: 14px; }

.meta-item { display: flex; align-items: center; gap: 4px; font-size: 12px; color: #64748b; }
.meta-item svg { color: #0284c7; }
.meta-lbl { color: #94a3b8; }
.meta-item strong { color: #334155; font-weight: 700; }

.card-side { display: flex; flex-direction: column; align-items: flex-end; gap: 10px; flex-shrink: 0; }

.start-btn {
  background: linear-gradient(135deg, #0284c7, #6366f1);
  color: white;
  border: none;
  padding: 9px 16px;
  border-radius: 13px;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
}
</style>
