<!--
 * [变更日志]
 * 修改时间：2026-09-06 22:10:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.2 新增"我的测试"页: 顶部三态 Tabs(进行中/未开始/已考试), 按试卷聚合多次作答,
 *          时间硬边界(未开始置灰/进行中倒计时压缩/已结束强制收卷), 解析锁(end_time 未到禁看解析)]
-->
<template>
  <div class="page">
    <NavBar title="我的测试" />
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
        <div v-for="c in grouped[activeTab]" :key="c.exam_id" class="exam-card">
          <div class="card-cover">
            <CoverArt :cover="c.cover_url || 'preset:1'" width="72px" height="72px" />
          </div>
          <div class="card-body">
            <div class="card-title">{{ c.title }}</div>
            <div class="card-meta">
              <span>{{ c.category_name || '未分类' }}</span>
              <span>{{ c.question_count }} 题</span>
              <span>{{ c.total_score }} 分</span>
              <span v-if="c.attempts > 0" class="attempts">已考 {{ c.attempts }} 次</span>
            </div>
            <div class="card-window">
              <span v-if="c.start_time" class="win-text">开始 {{ fmt(c.start_time) }}</span>
              <span v-if="c.end_time" class="win-text">截止 {{ fmt(c.end_time) }}</span>
            </div>
            <div class="card-foot">
              <!-- 未开始 -->
              <template v-if="activeTab === 'upcoming'">
                <button class="btn disabled" disabled>考试未开始</button>
              </template>
              <!-- 进行中 -->
              <template v-else-if="activeTab === 'ongoing'">
                <button v-if="c.my_record_id" class="btn primary" @click="resume(c)">继续作答</button>
                <button v-else class="btn primary" @click="startExam(c)">开始考试</button>
              </template>
              <!-- 已考试 -->
              <template v-else>
                <span v-if="latestLabel(c) === '批阅中'" class="status-tag grading">批阅中</span>
                <span v-else-if="c.latest_passed" class="status-tag pass">已通过</span>
                <span v-else class="status-tag fail">未通过</span>
                <span class="score">{{ c.latest_score }} 分</span>
                <button
                  class="btn ghost"
                  :class="{ disabled: !c.analysis_unlocked }"
                  @click="viewAnalysis(c)"
                >
                  {{ c.analysis_unlocked ? '查看解析' : '解析未开放' }}
                </button>
                <button v-if="c.window_status !== 'ended'" class="btn ghost" @click="startExam(c)">再考一次</button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
    <TabBar active="mytests" />
    <AppModal ref="modalRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import NavBar from '../../components/NavBar.vue';
import TabBar from '../../components/TabBar.vue';
import CoverArt from '../../components/CoverArt.vue';
import AppModal from '../../components/AppModal.vue';
import request from '../../utils/http';

const router = useRouter();
const loading = ref(true);
const modalRef = ref<any>(null);

const tabs = [
  { key: 'ongoing', label: '进行中' },
  { key: 'upcoming', label: '未开始' },
  { key: 'completed', label: '已考试' }
] as const;
const activeTab = ref<'ongoing' | 'upcoming' | 'completed'>('ongoing');
const emptyText: Record<string, string> = {
  ongoing: '当前没有可参与的考试',
  upcoming: '暂无即将开始的考试',
  completed: '还没有已完成的考试记录'
};
const grouped = reactive<Record<string, any[]>>({ ongoing: [], upcoming: [], completed: [] });

const fmt = (s?: string | null) => (s ? String(s).replace('T', ' ').slice(5, 16) : '');

const latestLabel = (c: any) => (c.latest_status === 'pending_grading' ? '批阅中' : c.latest_passed ? '已通过' : '未通过');

const load = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/records/my-tests');
    grouped.ongoing = res.ongoing || [];
    grouped.upcoming = res.upcoming || [];
    grouped.completed = res.completed || [];
  } finally {
    loading.value = false;
  }
};

const startExam = (c: any) => {
  router.push({ path: '/quiz', query: { exam_id: c.exam_id } });
};

const resume = (c: any) => {
  router.push({ path: '/quiz', query: { exam_id: c.exam_id, record_id: c.my_record_id } });
};

const viewAnalysis = async (c: any) => {
  if (!c.analysis_unlocked) {
    modalRef.value?.open?.({
      title: '解析暂未开放',
      message: '考试尚未结束，为防止答案泄露，解析将在考试结束后开放。',
      confirmText: '我知道了',
      showCancel: false
    });
    return;
  }
  if (c.latest_status === 'pending_grading') {
    modalRef.value?.open?.({
      title: '批阅中',
      message: '该答卷含简答题，正在等待老师/AI 批阅，成绩发布后即可查看完整解析。',
      confirmText: '我知道了',
      showCancel: false
    });
    return;
  }
  router.push({ path: '/report', query: { record_id: c.latest_record_id } });
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
  margin-bottom: 4px;
}

.attempts {
  color: #0062ff;
  font-weight: 600;
}

.card-window {
  font-size: 11px;
  color: #9ca3af;
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
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

.btn.ghost {
  background: #f3f4f6;
  color: #374151;
}

.btn.disabled {
  background: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
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

.status-tag.fail {
  background: #fee2e2;
  color: #dc2626;
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
