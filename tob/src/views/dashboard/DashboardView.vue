<!--
  * [变更日志]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[v1.7 新建: SaaS 首页 Dashboard，1:1 还原设计图（Banner + 4 KPI + 趋势图 + 环形图 + 四小卡），ECharts 静态假数据]
  -->
<template>
  <div class="dashboard">
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
      <div v-for="k in kpis" :key="k.label" class="kpi-card">
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
              @click="range = r"
            >{{ r }}</span>
          </div>
        </div>
        <div ref="trendRef" class="trend-chart"></div>
      </div>

      <div class="card donut-card">
        <div class="card-head">
          <div>
            <div class="card-title"><el-icon class="title-icon"><PieChart /></el-icon>试卷类型占比</div>
            <div class="card-sub">各类题型试卷在总数中的占比</div>
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
            <div class="quota-num">36,892 <span class="quota-total">/ 54,000</span></div>
            <el-progress :percentage="68" :show-text="false" stroke-width="8" />
            <div class="quota-left">剩余额度</div>
            <div class="quota-left-num">17,108 <el-tag size="small" type="info" effect="plain">预计可用 2.5 天</el-tag></div>
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { ArrowRight, TrendCharts, PieChart, Document, User, Cpu, Clock } from '@element-plus/icons-vue';
import * as echarts from 'echarts';

const bannerUrl = `${import.meta.env.BASE_URL}images/dashboard-banner.png`;

// ---- 静态假数据（v1.7：先展示，后续再接真实统计接口）----
const ranges = ['近7天', '近30天', '近90天'];
const range = ref('近7天');
const donutFilter = ref('all');

const kpis = [
  { key: 'exams', label: '试卷总数', value: '2,846', delta: '12.5%', down: false, bg: 'linear-gradient(135deg,#3b82f6,#60a5fa)', icon: Document, spark: [12, 18, 15, 22, 19, 28, 24, 33] },
  { key: 'users', label: '考试人次', value: '48,721', delta: '18.3%', down: false, bg: 'linear-gradient(135deg,#22c55e,#4ade80)', icon: User, spark: [20, 16, 24, 21, 30, 27, 36, 34] },
  { key: 'ai', label: 'AI 额度消耗', value: '36,892', delta: '7.6%', down: false, bg: 'linear-gradient(135deg,#8b5cf6,#a78bfa)', icon: Cpu, spark: [10, 14, 12, 18, 16, 22, 20, 26] },
  { key: 'pending', label: '待阅试卷', value: '428', delta: '23.4%', down: true, bg: 'linear-gradient(135deg,#f43f5e,#fb7185)', icon: Clock, spark: [30, 26, 28, 22, 24, 18, 20, 14] }
];

const donutData = [
  { name: '客观题', value: 1284, pct: '45.1%', color: '#3b82f6' },
  { name: '主观题', value: 712, pct: '25.0%', color: '#8b5cf6' },
  { name: '组合题', value: 468, pct: '16.4%', color: '#14b8a6' },
  { name: '实操题', value: 246, pct: '8.6%', color: '#f59e0b' },
  { name: '其他', value: 136, pct: '4.8%', color: '#cbd5e1' }
];

const recentExams = [
  { time: '2025年09月07日 14:32', name: '计算机基础测试', status: '进行中' },
  { time: '2025年09月07日 11:20', name: '英语能力评估', status: '已完成' },
  { time: '2025年09月07日 09:15', name: '职业技能考试', status: '已完成' },
  { time: '2025年09月06日 16:48', name: '数学模拟测试', status: '已完成' },
  { time: '2025年09月06日 14:22', name: '语文综合测试', status: '已完成' }
];

const hotList = [
  { name: '计算机基础测试', count: '1,248' },
  { name: '英语能力评估', count: '982' },
  { name: '职业技能考试', count: '764' },
  { name: '数学模拟测试', count: '621' },
  { name: '综合素质测评', count: '508' }
];

const notices = [
  { text: '系统将于本周六进行例行维护', date: '09-05' },
  { text: 'AI 题库新增模板更新', date: '09-03' },
  { text: '新增试卷模板上线', date: '08-28' },
  { text: '关于数据安全的说明', date: '08-25' }
];

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
  // KPI 迷你折线
  for (const k of kpis) {
    const el = sparkRefs[k.key];
    if (!el) continue;
    const c = echarts.init(el);
    c.setOption({
      grid: { left: 0, right: 0, top: 4, bottom: 0 },
      xAxis: { type: 'category', show: false, data: k.spark.map((_, i) => i) },
      yAxis: { type: 'value', show: false },
      series: [{ ...lineStyle(k.key === 'pending' ? '#f43f5e' : k.key === 'ai' ? '#8b5cf6' : k.key === 'users' ? '#22c55e' : '#3b82f6'), data: k.spark }]
    });
    charts.push(c);
  }
  // 趋势图
  if (trendRef.value) {
    const c = echarts.init(trendRef.value);
    c.setOption({
      grid: { left: 36, right: 16, top: 32, bottom: 28 },
      tooltip: { trigger: 'axis' },
      legend: { top: 0, right: 0, textStyle: { fontSize: 11, color: '#64748b' }, data: ['平均分', '考试人次'] },
      xAxis: { type: 'category', data: ['09/01', '09/02', '09/03', '09/04', '09/05', '09/06', '09/07'], axisLine: { lineStyle: { color: '#e2e8f0' } }, axisTick: { show: false }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
      yAxis: { type: 'value', max: 100, splitLine: { lineStyle: { color: '#f1f5f9' } }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
      series: [
        { name: '平均分', data: [40, 38, 48, 47, 58, 79, 62], ...lineStyle('#3b82f6') },
        { name: '考试人次', data: [24, 22, 32, 31, 42, 59, 43], ...lineStyle('#14b8a6') }
      ]
    });
    charts.push(c);
  }
  // 环形图
  if (donutRef.value) {
    const c = echarts.init(donutRef.value);
    c.setOption({
      tooltip: { trigger: 'item' },
      graphic: [
        { type: 'text', left: 'center', top: '42%', style: { text: '总计', fontSize: 12, fill: '#94a3b8', textAlign: 'center' } },
        { type: 'text', left: 'center', top: '50%', style: { text: '2,846', fontSize: 22, fontWeight: 800, fill: '#0f172a', textAlign: 'center' } },
        { type: 'text', left: 'center', top: '60%', style: { text: '试卷总数', fontSize: 12, fill: '#94a3b8', textAlign: 'center' } }
      ],
      series: [{
        type: 'pie',
        radius: ['62%', '82%'],
        center: ['50%', '52%'],
        avoidLabelOverlap: true,
        label: { show: false },
        itemStyle: { borderColor: '#fff', borderWidth: 2, borderRadius: 4 },
        data: donutData.map((d) => ({ name: d.name, value: d.value, itemStyle: { color: d.color } }))
      }]
    });
    charts.push(c);
  }
  // 额度环
  if (ringRef.value) {
    const c = echarts.init(ringRef.value);
    c.setOption({
      graphic: [{ type: 'text', left: 'center', top: '44%', style: { text: '68%\n已使用', fontSize: 16, fontWeight: 800, fill: '#0f172a', textAlign: 'center' } }],
      series: [{
        type: 'pie',
        radius: ['72%', '88%'],
        center: ['50%', '50%'],
        label: { show: false },
        data: [
          { value: 68, itemStyle: { color: '#3b82f6', borderRadius: 8 } },
          { value: 32, itemStyle: { color: '#e0f2fe' } }
        ]
      }]
    });
    charts.push(c);
  }
};

const handleResize = () => charts.forEach((c) => c.resize());

onMounted(() => {
  initCharts();
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
