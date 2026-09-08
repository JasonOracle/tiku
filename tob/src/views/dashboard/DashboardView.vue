<!--
  * [变更日志]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[v1.7 新建: SaaS 首页 Dashboard，1:1 还原设计图（Banner + 4 KPI + 趋势图 + 环形图 + 四小卡），ECharts 静态假数据]
  * 修改时间：2026-09-08
  * AI模型：Muse Spark
  * 修改内容：[v1.3 任务4: 对接 GET /admin/dashboard/stats 真实聚合数据（KPI/趋势/环形/排行/动态/公告/额度），出题人自动作用域隔离]
  -->
<template>
  <div v-loading="loading" class="dashboard">
    <!-- 顶部 Banner -->
    <div class="banner">
      <div class="banner-text">
        <h1>智能考试 · 数据驱动 · 助力成长</h1>
        <p>用科技让教育更高效 · 让每一次考试更有价值</p>
      </div>
      <img class="banner-img" :src="bannerUrl" alt="数据看板插画" />
    </div>

    <!-- 4 张 KPI 卡 -->
    <div class="kpi-row">
      <div v-for="k in kpis" :key="k.key" class="kpi-card">
        <div class="kpi-top">
          <div class="kpi-icon" :style="{ background: k.bg }">
            <el-icon><component :is="k.icon" /></el-icon>
          </div>
          <div class="kpi-meta">
            <span class="kpi-label">{{ k.label }}</span>
            <span class="kpi-value">{{ k.value }}</span>
          </div>
          <el-icon class="kpi-more"><ArrowRight /></el-icon>
        </div>
        <div class="kpi-bottom">
          <span class="kpi-delta" :class="k.down ? 'down' : 'up'">
            {{ k.down ? '↓' : '↑' }} {{ k.delta }} 较上周
          </span>
          <div :ref="(el) => setSparkRef(el, k.key)" class="spark"></div>
        </div>
      </div>
    </div>

    <!-- 趋势 + 环形 -->
    <div class="chart-row">
      <div class="card trend-card">
        <div class="card-head">
          <div>
            <div class="card-title"><el-icon class="title-icon"><TrendCharts /></el-icon>学生成绩趋势分析</div>
            <div class="card-sub">近 7 天考试人次与平均分变化趋势</div>
          </div>
          <div class="range-tabs">
            <span
              v-for="r in ranges"
              :key="r"
              class="range-tab"
              :class="{ active: range === r }"
              @click="switchRange(r)"
            >{{ r }}</span>
          </div>
        </div>
        <div ref="trendRef" class="trend-chart"></div>
      </div>

      <div class="card donut-card">
        <div class="card-head">
          <div>
            <div class="card-title"><el-icon class="title-icon"><PieChart /></el-icon>试卷分类占比</div>
            <div class="card-sub">各分类试卷在总数中的占比</div>
          </div>
          <el-select v-model="donutFilter" size="small" style="width: 110px">
            <el-option label="全部类型" value="all" />
          </el-select>
        </div>
        <div class="donut-body">
          <div ref="donutRef" class="donut-chart"></div>
          <div class="donut-legend">
            <div v-for="d in donutData" :key="d.name" class="legend-row">
              <span class="dot" :style="{ background: d.color }"></span>
              <span class="legend-name">{{ d.name }}</span>
              <span class="legend-val">{{ d.value.toLocaleString() }}</span>
              <span class="legend-pct">{{ d.pct }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 四小卡 -->
    <div class="bottom-row">
      <div class="card">
        <div class="card-head">
          <div class="card-title"><span class="title-dot"></span>最近考试动态</div>
          <span class="more">更多 ></span>
        </div>
        <div v-for="e in recentExams" :key="e.time + e.name" class="dyn-row">
          <span class="dot-blue"></span>
          <span class="dyn-time">{{ e.time }}</span>
          <span class="dyn-name">{{ e.name }}</span>
          <el-tag size="small" :type="e.status === '进行中' ? 'primary' : 'success'" effect="plain">
            {{ e.status }}
          </el-tag>
        </div>
        <el-empty v-if="!recentExams.length" description="暂无考试动态" :image-size="60" />
      </div>

      <div class="card">
        <div class="card-head">
          <div class="card-title">◇ AI 额度使用情况</div>
          <span class="more">↗ ></span>
        </div>
        <div class="quota-body">
          <div ref="ringRef" class="ring-chart"></div>
          <div class="quota-info">
            <div class="quota-label">今日已用</div>
            <div class="quota-num">{{ quota.used }} <span class="quota-total">/ {{ quota.total }}</span></div>
            <el-progress :percentage="quota.pct" :show-text="false" stroke-width="8" />
            <div class="quota-left">剩余额度</div>
            <div class="quota-left-num">{{ quota.left }} <el-tag v-if="quota.days" size="small" type="info" effect="plain">预计可用 {{ quota.days }}</el-tag></div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-head">
          <div class="card-title"><span class="title-doc">▤</span> 热门试卷排行</div>
          <span class="more">更多 ></span>
        </div>
        <div v-for="(h, i) in hotList" :key="h.name" class="hot-row">
          <span class="rank" :class="`rank-${i + 1}`">{{ i + 1 }}</span>
          <span class="hot-name">{{ h.name }}</span>
          <span class="hot-count">{{ h.count }} 次</span>
        </div>
        <el-empty v-if="!hotList.length" description="暂无排行数据" :image-size="60" />
      </div>

      <div class="card">
        <div class="card-head">
          <div class="card-title">🛰 系统公告</div>
          <span class="more">更多 ></span>
        </div>
        <div v-for="n in notices" :key="n.date + n.text" class="notice-row">
          <span class="dot-blue"></span>
          <span class="notice-text">{{ n.text }}</span>
          <span class="notice-date">{{ n.date }}</span>
        </div>
        <el-empty v-if="!notices.length" description="暂无公告" :image-size="60" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { ArrowRight, TrendCharts, PieChart, Document, User, Cpu, Clock } from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import request from '../../utils/request';

const bannerUrl = `${import.meta.env.BASE_URL}images/dashboard-banner.png`;

const ranges = ['近7天', '近30天', '近90天'];
const range = ref('近7天');
const donutFilter = ref('all');
const loading = ref(true);

interface Stats {
  kpi: { exams: number; records: number; ai_usage: number; pending: number };
  deltas: { exams: string; records: string; ai_usage: string };
  sparks: { exams: number[]; records: number[]; ai: number[] };
  trend: Array<{ day: string; count: number; avg: number }>;
  donut: Array<{ name: string; value: number }>;
  hot: Array<{ exam_id: number; title: string; count: number }>;
  recent: Array<{ time: string; name: string; username: string; score: number; status: string }>;
  notices: Array<{ text: string; date: string }>;
  quota: { used_today: number; remaining: number; limit: number };
}

const stats = ref<Stats | null>(null);

const fmt = (n: number) => (n || 0).toLocaleString();
const isDown = (d?: string) => !!d && d !== '—' && d.startsWith('-');

const kpis = computed(() => {
  const k = stats.value?.kpi || { exams: 0, records: 0, ai_usage: 0, pending: 0 };
  const dl = stats.value?.deltas || { exams: '—', records: '—', ai_usage: '—' };
  const sp = stats.value?.sparks || { exams: [], records: [], ai: [] };
  return [
    { key: 'exams', label: '试卷总数', value: fmt(k.exams), delta: dl.exams, down: isDown(dl.exams), bg: 'linear-gradient(135deg,#3b82f6,#60a5fa)', icon: Document, spark: sp.exams, color: '#3b82f6' },
    { key: 'users', label: '考试人次', value: fmt(k.records), delta: dl.records, down: isDown(dl.records), bg: 'linear-gradient(135deg,#22c55e,#4ade80)', icon: User, spark: sp.records, color: '#22c55e' },
    { key: 'ai', label: 'AI 额度消耗', value: fmt(k.ai_usage), delta: dl.ai_usage, down: isDown(dl.ai_usage), bg: 'linear-gradient(135deg,#8b5cf6,#a78bfa)', icon: Cpu, spark: sp.ai, color: '#8b5cf6' },
    { key: 'pending', label: '待阅试卷', value: fmt(k.pending), delta: '—', down: false, bg: 'linear-gradient(135deg,#f43f5e,#fb7185)', icon: Clock, spark: sp.records.map(() => 0), color: '#f43f5e' }
  ];
});

const donutPalette = ['#3b82f6', '#8b5cf6', '#14b8a6', '#f59e0b', '#64748b', '#cbd5e1'];

const donutData = computed(() => {
  const total = (stats.value?.donut || []).reduce((s, d) => s + d.value, 0);
  return (stats.value?.donut || []).map((d, i) => ({
    name: d.name,
    value: d.value,
    pct: total > 0 ? `${((d.value * 100) / total).toFixed(1)}%` : '0%',
    color: donutPalette[i % donutPalette.length]
  }));
});

const donutTotal = computed(() => (stats.value?.donut || []).reduce((s, d) => s + d.value, 0));

const recentExams = computed(() => (stats.value?.recent || []).map((r) => ({
  time: r.time, name: r.name, status: '已完成'
})));

const hotList = computed(() => (stats.value?.hot || []).map((h) => ({
  name: h.title, count: String(h.count)
})));

const notices = computed(() => stats.value?.notices || []);

const quota = computed(() => {
  const q = stats.value?.quota || { used_today: 0, remaining: 0, limit: 0 };
  const total = q.used_today + q.remaining;
  const pct = total > 0 ? Math.round((q.used_today * 100) / total) : 0;
  const avg7 = ((stats.value?.sparks.ai || []).reduce((s, v) => s + v, 0) / 7) || 0;
  return {
    used: fmt(q.used_today),
    total: fmt(total),
    pct,
    left: q.remaining >= 99999999 ? '无限制' : fmt(q.remaining),
    days: q.remaining >= 99999999 || avg7 <= 0 ? '' : `${(q.remaining / avg7).toFixed(1)} 天`
  };
});

const switchRange = (r: string) => {
  range.value = r;
  if (r !== '近7天') {
    ElMessage.info('近30/90天视图即将上线，当前展示近7天数据');
    range.value = '近7天';
  }
};

// ---- ECharts ----
const trendRef = ref<HTMLElement | null>(null);
const donutRef = ref<HTMLElement | null>(null);
const ringRef = ref<HTMLElement | null>(null);
const sparkRefs: Record<string, HTMLElement | null> = {};
const charts: echarts.ECharts[] = [];

const setSparkRef = (el: unknown, key: string) => {
  sparkRefs[key] = el as HTMLElement | null;
};

const lineStyle = (color: string) => ({
  type: 'line' as const,
  smooth: true,
  symbol: 'none',
  lineStyle: { width: 2, color },
  areaStyle: {
    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
      { offset: 0, color: `${color}55` },
      { offset: 1, color: `${color}05` }
    ])
  }
});

const initCharts = () => {
  for (const k of kpis.value) {
    const el = sparkRefs[k.key];
    if (!el) continue;
    const c = echarts.init(el);
    c.setOption({
      grid: { left: 0, right: 0, top: 4, bottom: 0 },
      xAxis: { type: 'category', show: false, data: k.spark.map((_, i) => i) },
      yAxis: { type: 'value', show: false },
      series: [{ ...lineStyle(k.color), data: k.spark }]
    });
    charts.push(c);
  }
  const trend = stats.value?.trend || [];
  if (trendRef.value) {
    const c = echarts.init(trendRef.value);
    c.setOption({
      grid: { left: 36, right: 16, top: 32, bottom: 28 },
      tooltip: { trigger: 'axis' },
      legend: { top: 0, right: 0, textStyle: { fontSize: 11, color: '#64748b' }, data: ['平均分', '考试人次'] },
      xAxis: { type: 'category', data: trend.map((t) => t.day), axisLine: { lineStyle: { color: '#e2e8f0' } }, axisTick: { show: false }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
      yAxis: { type: 'value', max: 100, splitLine: { lineStyle: { color: '#f1f5f9' } }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
      series: [
        { name: '平均分', data: trend.map((t) => t.avg), ...lineStyle('#3b82f6') },
        { name: '考试人次', data: trend.map((t) => t.count), ...lineStyle('#14b8a6') }
      ]
    });
    charts.push(c);
  }
  if (donutRef.value) {
    const c = echarts.init(donutRef.value);
    const total = donutTotal.value;
    c.setOption({
      tooltip: { trigger: 'item' },
      graphic: [
        { type: 'text', left: 'center', top: '42%', style: { text: '总计', fontSize: 12, fill: '#94a3b8', textAlign: 'center' } },
        { type: 'text', left: 'center', top: '50%', style: { text: String(total), fontSize: 22, fontWeight: 800, fill: '#0f172a', textAlign: 'center' } },
        { type: 'text', left: 'center', top: '60%', style: { text: '试卷总数', fontSize: 12, fill: '#94a3b8', textAlign: 'center' } }
      ],
      series: [{
        type: 'pie',
        radius: ['62%', '82%'],
        center: ['50%', '52%'],
        avoidLabelOverlap: true,
        label: { show: false },
        itemStyle: { borderColor: '#fff', borderWidth: 2, borderRadius: 4 },
        data: donutData.value.map((d) => ({ name: d.name, value: d.value, itemStyle: { color: d.color } }))
      }]
    });
    charts.push(c);
  }
  if (ringRef.value) {
    const c = echarts.init(ringRef.value);
    const q = stats.value?.quota || { used_today: 0, remaining: 0 };
    const total = q.used_today + q.remaining;
    const pct = total > 0 ? Math.round((q.used_today * 100) / total) : 0;
    c.setOption({
      graphic: [{ type: 'text', left: 'center', top: '44%', style: { text: `${pct}%\n已使用`, fontSize: 16, fontWeight: 800, fill: '#0f172a', textAlign: 'center' } }],
      series: [{
        type: 'pie',
        radius: ['72%', '88%'],
        center: ['50%', '50%'],
        label: { show: false },
        data: [
          { value: pct, itemStyle: { color: '#3b82f6', borderRadius: 8 } },
          { value: 100 - pct, itemStyle: { color: '#e0f2fe' } }
        ]
      }]
    });
    charts.push(c);
  }
};

const handleResize = () => charts.forEach((c) => c.resize());

const loadStats = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/dashboard/stats');
    stats.value = res;
  } catch (e) {
    /* 拦截器已提示；图表保持空态 */
  } finally {
    loading.value = false;
    initCharts();
  }
};

onMounted(() => {
  loadStats();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  charts.forEach((c) => c.dispose());
  charts.length = 0;
});
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #f4f7fe;
  padding: 4px;
}

.banner {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  background: linear-gradient(120deg, #e8f1ff 0%, #dbeafe 55%, #bfdbfe 100%);
  min-height: 150px;
  display: flex;
  align-items: center;
  padding: 28px 36px;
}

.banner-text h1 {
  font-size: 26px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 8px;
  letter-spacing: 1px;
}

.banner-text p {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.banner-img {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 46%;
  object-fit: cover;
  mask-image: linear-gradient(to right, transparent, #000 30%);
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.kpi-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px 18px;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
}

.kpi-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.kpi-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
  flex-shrink: 0;
}

.kpi-meta {
  display: flex;
  flex-direction: column;
}

.kpi-label {
  font-size: 13px;
  color: #475569;
}

.kpi-value {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
}

.kpi-more {
  margin-left: auto;
  color: #94a3b8;
}

.kpi-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.kpi-delta {
  font-size: 12px;
  font-weight: 600;
}

.kpi-delta.up { color: #16a34a; }
.kpi-delta.down { color: #ef4444; }

.spark {
  width: 110px;
  height: 36px;
}

.chart-row {
  display: grid;
  grid-template-columns: 7fr 5fr;
  gap: 16px;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 8px;
}

.card-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 6px;
}

.title-icon { color: #3b82f6; }
.title-dot { width: 8px; height: 8px; border-radius: 50%; background: #3b82f6; display: inline-block; }
.title-doc { color: #3b82f6; font-weight: 800; }

.card-sub {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.more {
  font-size: 12px;
  color: #94a3b8;
  cursor: pointer;
  white-space: nowrap;
}

.range-tabs {
  display: flex;
  gap: 4px;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 3px;
}

.range-tab {
  font-size: 12px;
  color: #64748b;
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
}

.range-tab.active {
  background: #3b82f6;
  color: #fff;
  font-weight: 600;
}

.trend-chart { height: 300px; }

.donut-body {
  display: flex;
  align-items: center;
  gap: 8px;
}

.donut-chart {
  width: 220px;
  height: 260px;
  flex-shrink: 0;
}

.donut-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.dot { width: 10px; height: 10px; border-radius: 50%; }
.legend-name { color: #475569; }
.legend-val { margin-left: auto; font-weight: 700; color: #0f172a; }
.legend-pct { color: #94a3b8; width: 44px; text-align: right; }

.bottom-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.dyn-row, .notice-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  padding: 7px 0;
  border-bottom: 1px dashed #f1f5f9;
}

.dyn-row:last-child, .notice-row:last-child { border-bottom: none; }
.dot-blue { width: 6px; height: 6px; border-radius: 50%; background: #3b82f6; flex-shrink: 0; }
.dyn-time { color: #94a3b8; white-space: nowrap; }
.dyn-name { color: #334155; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.notice-text { color: #334155; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.notice-date { color: #94a3b8; }

.quota-body {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ring-chart { width: 130px; height: 130px; flex-shrink: 0; }
.quota-info { flex: 1; }
.quota-label { font-size: 12px; color: #64748b; }
.quota-num { font-size: 18px; font-weight: 800; color: #0f172a; margin: 2px 0 6px; }
.quota-total { font-size: 12px; color: #94a3b8; font-weight: 400; }
.quota-left { font-size: 12px; color: #64748b; margin-top: 8px; }
.quota-left-num { font-size: 16px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px; }

.hot-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  font-size: 13px;
}

.rank {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rank-1 { background: #3b82f6; color: #fff; }
.rank-2 { background: #8b5cf6; color: #fff; }
.rank-3 { background: #f59e0b; color: #fff; }
.hot-name { flex: 1; color: #334155; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hot-count { color: #94a3b8; font-size: 12px; }
</style>
