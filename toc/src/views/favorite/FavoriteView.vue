<!--
 * [变更日志]
 * 修改时间：2026-09-03
 * AI模型：Gemini 底层
 * 修改内容：[1. 实现 C 端个人题目收藏夹列表与解析复习组件]
-->
<template>
  <div class="fav-container">
    <header class="top-bar">
      <button class="back-btn" @click="router.push('/')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>
      <span class="title">我的收藏夹</span>
    </header>

    <main class="fav-list">
      <div v-if="favorites.length === 0" class="empty-state">
        <p>暂无收藏题目</p>
      </div>

      <div v-for="fav in favorites" :key="fav.id" class="fav-card">
        <div class="card-top">
          <span class="q-id">题目 ID #{{ fav.question_id }}</span>
          <button class="remove-btn" @click="removeFavorite(fav.question_id)">移除收藏</button>
        </div>

        <h4 class="q-title">{{ fav.question?.title }}</h4>

        <div class="ans-badge">
          正确答案：{{ fav.question?.answer ? fav.question.answer.join(', ') : '暂无' }}
        </div>

        <p v-if="fav.question?.explanation" class="exp">
          解析：{{ fav.question.explanation }}
        </p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import http from '../../utils/http';

const router = useRouter();
const favorites = ref<any[]>([]);

const loadFavorites = async () => {
  try {
    const res: any = await http.get('/api/v1/favorites');
    favorites.value = res.items || [];
  } catch (e) {}
};

const removeFavorite = async (questionId: number) => {
  await http.delete(`/api/v1/favorites/${questionId}`);
  loadFavorites();
};

onMounted(() => {
  loadFavorites();
});
</script>

<style scoped>
.fav-container {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: #f8fafc;
}

.top-bar {
  padding: 16px 20px;
  background: white;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.back-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #0284c7;
}

.title {
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
}

.fav-list {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.fav-card {
  background: white;
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.q-id {
  font-size: 12px;
  font-weight: 700;
  color: #0284c7;
}

.remove-btn {
  background: transparent;
  border: none;
  color: #ef4444;
  font-size: 12px;
  cursor: pointer;
}

.q-title {
  margin: 10px 0;
  font-size: 15px;
  color: #1e293b;
}

.ans-badge {
  background: #e0f2fe;
  color: #0284c7;
  display: inline-block;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
}

.exp {
  margin: 10px 0 0;
  font-size: 13px;
  color: #64748b;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #94a3b8;
}
</style>
