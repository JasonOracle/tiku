<!--
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗：对接成员收藏新接口并移除答案展示（防泄漏），旧收藏体系已删除]
-->
<template>
  <div class="fav-container">
    <NavBar title="我的资源收藏" />

    <main class="fav-list">
      <div v-if="favorites.length === 0" class="empty-state">
        <div class="empty-icon">⭐</div>
        <p>暂无收藏条目</p>
      </div>

      <div v-for="fav in favorites" :key="fav.id" class="fav-card">
        <div class="card-thumb">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        </div>

        <div class="card-info">
          <div class="card-badge-row">
            <span class="q-badge">条目 #{{ fav.resource_id }}</span>
            <span class="type-tag" v-if="fav.type">
              {{ getTypeLabel(fav.type) }}
            </span>
          </div>

          <h3 class="q-title">{{ fav.title || fav.content || '条目信息已载入' }}</h3>
        </div>

        <div class="card-action">
          <button class="remove-btn" @click="removeFavorite(fav.resource_id)" title="取消收藏">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import http from '../../utils/http';
import NavBar from '../../components/NavBar.vue';

const router = useRouter();
const favorites = ref<any[]>([]);

const getTypeLabel = (type: string) => {
  if (type === 'single') return '单选题';
  if (type === 'multiple') return '多选题';
  if (type === 'fill') return '填空题';
  if (type === 'short') return '简答题';
  return '判断题';
};

const loadFavorites = async () => {
  try {
    const res: any = await http.get('/api/v1/member/favorites');
    favorites.value = res.items || [];
  } catch (e) {}
};

const removeFavorite = async (resourceId: number) => {
  await http.delete(`/api/v1/member/favorites/${resourceId}`);
  loadFavorites();
};

onMounted(() => {
  loadFavorites();
});
</script>

<style scoped>
.fav-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #eef4ff 0%, #f8fafc 40%);
  padding-bottom: 30px;
}

.fav-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.fav-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 16px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.04), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-thumb {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #fffbe0 0%, #fef3c7 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.9), 0 4px 10px rgba(245, 158, 11, 0.12);
}

.card-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-badge-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.q-badge {
  font-size: 11px;
  font-weight: 700;
  color: #0284c7;
  background: #f0f9ff;
  padding: 2px 8px;
  border-radius: 6px;
}

.type-tag {
  font-size: 11px;
  font-weight: 700;
  color: #6366f1;
  background: #eef2ff;
  padding: 2px 8px;
  border-radius: 6px;
}

.q-title {
  margin: 4px 0 2px;
  font-size: 15px;
  color: #0f172a;
  font-weight: 800;
  line-height: 1.4;
}

.meta-chips {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.chip.green {
  background: #f0fdf4;
  border: 1px solid #dcfce7;
  padding: 3px 10px;
  border-radius: 8px;
  display: inline-flex;
  gap: 6px;
  align-items: center;
}

.chip-label {
  color: #166534;
  font-size: 11px;
  font-weight: 600;
}

.chip-val {
  color: #15803d;
  font-weight: 800;
  font-size: 12px;
}

.exp-text {
  margin: 6px 0 0;
  font-size: 12px;
  color: #64748b;
  background: #f8fafc;
  padding: 8px 10px;
  border-radius: 8px;
  line-height: 1.45;
}

.card-action {
  flex-shrink: 0;
}

.remove-btn {
  background: #fff1f2;
  color: #e11d48;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.remove-btn:active {
  transform: scale(0.9);
}

.empty-state {
  text-align: center;
  padding: 80px 0;
  color: #94a3b8;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}
</style>
