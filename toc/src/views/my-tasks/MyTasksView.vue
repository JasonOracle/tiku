<!--
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗重写：待办/已提交两态，直接对接成员任务接口，旧三态/解析锁体系已删除]
-->
<template>
  <div class="page">
    <NavBar title="我的任务" />
    <div class="content">
      <div class="tabs">
        <button v-for="t in tabs" :key="t.key" class="tab" :class="{ active: activeTab === t.key }" @click="activeTab = t.key">
          {{ t.label }}
          <span class="count">{{ grouped[t.key].length }}</span>
        </button>
      </div>

      <div v-if="loading" class="state-tip">加载中...</div>
      <div v-else-if="grouped[activeTab].length === 0" class="state-tip">
        <p class="empty-icon">📭</p>
        <p>{{ emptyText[activeTab] }}</p>
      </div>

      <div v-else class="cards">
        <div v-for="c in grouped[activeTab]" :key="c.task_id" class="exam-card">
          <div class="card-body">
            <div class="card-title">{{ c.title }}</div>
            <div class="card-meta">
              <span v-if="c.deadline">截止 {{ fmt(c.deadline) }}</span>
              <span v-if="c.status && c.status !== 'pending'" class="attempts">{{ statusLabel(c.status) }}</span>
            </div>
            <div class="card-foot">
              <template v-if="activeTab === 'pending'">
                <button class="btn primary" @click="startTask(c)">开始任务</button>
              </template>
              <template v-else>
                <span class="status-tag" :class="c.status === 'verified' ? 'pass' : 'grading'">
                  {{ statusLabel(c.status) }}
                </span>
                <span v-if="c.score != null" class="score">{{ c.score }} 分</span>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
    <TabBar active="mytasks" />
    <AppModal ref="modalRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import NavBar from '../../components/NavBar.vue';
import TabBar from '../../components/TabBar.vue';
import AppModal from '../../components/AppModal.vue';
import http from '../../utils/http';

const router = useRouter();
const loading = ref(true);
const modalRef = ref<any>(null);

const tabs = [
  { key: 'pending', label: '待办' },
  { key: 'done', label: '已提交' }
] as const;
const activeTab = ref<'pending' | 'done'>('pending');
const emptyText: Record<string, string> = {
  pending: '当前没有待办任务',
  done: '还没有提交记录'
};
const grouped = reactive<Record<string, any[]>>({ pending: [], done: [] });

const fmt = (s?: string | null) => (s ? String(s).replace('T', ' ').slice(0, 16) : '');

const statusLabel = (s: string) => {
  if (s === 'verified') return '已核验';
  if (s === 'pending_verification') return '核验中';
  if (s === 'submitted') return '已提交';
  return '待办';
};

const load = async () => {
  loading.value = true;
  try {
    const res: any = await http.get('/api/v1/member/member-tasks');
    const items = res.items || [];
    grouped.pending = items.filter((i: any) => i.status === 'pending');
    grouped.done = items.filter((i: any) => i.status !== 'pending');
  } finally {
    loading.value = false;
  }
};

const startTask = (c: any) => {
  router.push({ path: '/task', query: { task_id: c.task_id } });
};

onMounted(load);
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f6f7fb;
  padding-bottom: 110px;
}

.content {
  padding: 12px 16px;
  max-width: 480px;
  margin: 0 auto;
}

.tabs {
  display: flex;
  background: #ffffff;
  border-radius: 14px;
  padding: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  margin-bottom: 14px;
}

.tab {
  flex: 1;
  border: none;
  background: transparent;
  padding: 9px 0;
  font-size: 14px;
  color: #6b7280;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.tab.active {
  background: #0062ff;
  color: #fff;
  font-weight: 700;
}

.count {
  font-size: 11px;
  opacity: 0.8;
}

.state-tip {
  text-align: center;
  color: #9ca3af;
  padding: 60px 0;
  font-size: 14px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 8px;
}

.cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.exam-card {
  background: #fff;
  border-radius: 16px;
  padding: 14px;
  display: flex;
  gap: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.card-cover {
  flex-shrink: 0;
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.attempts {
  color: #0062ff;
  font-weight: 600;
}

.card-foot {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  border: none;
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn.primary {
  background: linear-gradient(135deg, #0062ff, #0047cc);
  color: #fff;
}

.status-tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 999px;
  font-weight: 600;
}

.status-tag.pass {
  background: #dcfce7;
  color: #16a34a;
}

.status-tag.grading {
  background: #fef3c7;
  color: #b45309;
}

.score {
  font-size: 14px;
  font-weight: 800;
  color: #111827;
}
</style>
