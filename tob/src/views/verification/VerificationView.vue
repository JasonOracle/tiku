<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 3.6 Flash
 * 修改内容：[全面重构待核验队列与阅卷流程：1. 列表清晰展现试卷标题、考生姓名账号、提交时间与AI智能分析建议；2. 增加抽屉式可视人工批改，高亮展示试题原文、标准答案与学生答卷；3. 支持一键采纳AI建议或手动微调分数]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="title-box">
        <span class="title">待核验试卷提交列表</span>
        <el-tag type="warning" size="small" style="margin-left: 8px">待人工审阅 {{ records.length }} 份</el-tag>
      </div>
      <el-button text type="primary" @click="loadRecords">
        <el-icon><Refresh /></el-icon> 刷新数据
      </el-button>
    </div>

    <el-table :data="records" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
      <el-table-column prop="record_id" label="记录ID" width="85" align="center" />
      <el-table-column prop="task_title" label="考核试卷名称" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span style="font-weight: 600; color: #1e293b">{{ row.task_title }}</span>
        </template>
      </el-table-column>
      <el-table-column label="考生姓名 / 账号" min-width="170">
        <template #default="{ row }">
          <div style="display: flex; flex-direction: column">
            <span style="font-weight: 700; color: #0f172a">{{ row.nickname || row.username }}</span>
            <span style="font-size: 12px; color: #64748b" v-if="row.nickname">{{ row.username }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="submit_time" label="提交时间" width="160" align="center" />
      <el-table-column label="AI 智能阅卷预判" min-width="220">
        <template #default="{ row }">
          <div v-if="row.ai_result" class="ai-suggestion-box">
            <el-tag type="success" size="small" style="margin-right: 6px">建议 {{ row.ai_result.suggested_score }} 分</el-tag>
            <span class="ai-comment-text" :title="row.ai_result.comments">{{ row.ai_result.comments }}</span>
          </div>
          <el-tag v-else type="info" size="small">未触发 AI 评阅</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right" align="center">
        <template #default="{ row }">
          <el-button type="warning" text size="small" :loading="aiLoading === row.record_id" @click="triggerAi(row)">
            ✨ AI 助考分析
          </el-button>
          <el-button type="primary" size="small" @click="openDrawer(row)">
            进入批改
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 可视化人工批改抽屉 Drawer -->
    <el-drawer v-model="drawerVisible" size="700px" destroy-on-close title="人工阅卷批改与核验">
      <div v-loading="drawerLoading" class="drawer-content" v-if="detailData">
        <!-- 考生与试卷基础信息 -->
        <div class="exam-header-card">
          <div class="header-line">
            <span class="exam-title">{{ detailData.task_title }}</span>
            <el-tag type="warning">待核验定分</el-tag>
          </div>
          <div class="header-meta">
            <span>考生: <strong>{{ detailData.nickname || detailData.username }}</strong></span>
            <span>账号: {{ detailData.username }}</span>
            <span>提交时间: {{ detailData.submit_time }}</span>
          </div>
        </div>

        <!-- AI 建议评分高亮卡片 -->
        <div v-if="detailData.ai_result" class="ai-eval-card">
          <div class="ai-eval-head">
            <span>✨ AI 批改意见与建议得分</span>
            <el-tag type="success" effect="dark" size="small">建议得分: {{ detailData.ai_result.suggested_score }} 分</el-tag>
          </div>
          <div class="ai-eval-body">
            {{ detailData.ai_result.comments }}
          </div>
          <div style="margin-top: 8px">
            <el-button type="success" size="small" plain @click="applyAiScore">
              一键采纳 AI 建议分数 ({{ detailData.ai_result.suggested_score }}分)
            </el-button>
          </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px;">
          <el-divider content-position="left" style="margin: 0"><strong>待人工批改的简答题（共 {{ shortQuestions.length }} 题）</strong></el-divider>
          <el-checkbox v-model="showAllTypes" size="small">显示全卷客观题（客客观题已自动判分）</el-checkbox>
        </div>

        <!-- 题目与作答逐题高亮展示（仅高亮展示简答题 / 选填全卷） -->
        <div class="question-list">
          <div v-for="(item, idx) in displayQuestions" :key="idx" class="q-item-card">
            <div class="q-head">
              <span class="q-num">第 {{ item.originalIndex + 1 }} 题</span>
              <el-tag size="small" :type="getQuestionTypeTag(item.type)">{{ getQuestionTypeLabel(item.type) }}</el-tag>
              <span class="q-score">满分 {{ item.score || 10 }} 分</span>
            </div>
            <div class="q-content">{{ item.content }}</div>

            <!-- 参考正确答案 -->
            <div class="correct-box">
              <span class="label">标准参考答案: </span>
              <span class="val">{{ formatAnswer(item.correct_answer) }}</span>
            </div>

            <!-- 考生真实作答内容 -->
            <div class="user-answer-box">
              <span class="label">考生答卷内容: </span>
              <div class="user-val">{{ formatAnswer(item.answer) }}</div>
            </div>
          </div>
        </div>

        <!-- 定分表单区域 -->
        <div class="confirm-footer-box">
          <el-divider content-position="left"><strong>核验定分录入</strong></el-divider>
          <el-form label-width="100px">
            <el-form-item label="核验最终得分" required>
              <el-input-number v-model="confirmForm.final_score" :min="0" :max="500" style="width: 180px" />
              <span style="margin-left: 10px; color: #64748b; font-size: 13px">分</span>
            </el-form-item>
            <el-form-item label="主考官评语">
              <el-input v-model="confirmForm.comments" type="textarea" :rows="3" placeholder="请输入主考官核验意见或批改评语..." />
            </el-form-item>
          </el-form>
        </div>
      </div>

      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 12px">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="doConfirm">确认定分并完成阅卷</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { Refresh } from '@element-plus/icons-vue';
import request from '../../utils/request';

const loading = ref(false);
const saving = ref(false);
const aiLoading = ref<number | null>(null);
const records = ref<any[]>([]);

// 抽屉状态
const drawerVisible = ref(false);
const drawerLoading = ref(false);
const detailData = ref<any>(null);
const showAllTypes = ref(false);
const confirmForm = reactive({ final_score: 0, comments: '' });

const allQuestions = computed(() => {
  if (!detailData.value?.items) return [];
  return detailData.value.items.map((it: any, idx: number) => ({
    ...it,
    originalIndex: idx
  }));
});

const shortQuestions = computed(() => {
  return allQuestions.value.filter((it: any) => it.type === 'short' || it.type === 'short_answer');
});

const displayQuestions = computed(() => {
  if (showAllTypes.value || shortQuestions.value.length === 0) {
    return allQuestions.value;
  }
  return shortQuestions.value;
});

const loadRecords = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/verifications/pending');
    records.value = res.items || [];
  } finally {
    loading.value = false;
  }
};

const triggerAi = async (row: any) => {
  aiLoading.value = row.record_id;
  try {
    const res: any = await request.post(`/api/v1/admin/ai/verify/${row.record_id}`);
    ElMessage.success(res.message || 'AI 助考分析完成');
    loadRecords();
  } finally {
    aiLoading.value = null;
  }
};

const openDrawer = async (row: any) => {
  drawerVisible.value = true;
  drawerLoading.value = true;
  detailData.value = null;
  try {
    const res: any = await request.get(`/api/v1/admin/verifications/${row.record_id}`);
    detailData.value = res;
    confirmForm.final_score = res.ai_result?.suggested_score ?? (res.score || 0);
    confirmForm.comments = res.comments || res.ai_result?.comments || '';
  } catch (e) {
    ElMessage.error('加载试卷作答详情失败');
  } finally {
    drawerLoading.value = false;
  }
};

const applyAiScore = () => {
  if (detailData.value?.ai_result) {
    confirmForm.final_score = detailData.value.ai_result.suggested_score;
    if (detailData.value.ai_result.comments) {
      confirmForm.comments = `【采纳AI意见】${detailData.value.ai_result.comments}`;
    }
    ElMessage.success('已应用 AI 建议得分与评语');
  }
};

const doConfirm = async () => {
  if (!detailData.value) return;
  saving.value = true;
  try {
    await request.post(`/api/v1/admin/verifications/${detailData.value.record_id}/confirm`, {
      accept_ai_suggestion: true,
      final_score: confirmForm.final_score,
      comments: confirmForm.comments
    });
    ElMessage.success('核验定分保存成功！');
    drawerVisible.value = false;
    loadRecords();
  } finally {
    saving.value = false;
  }
};

const getQuestionTypeTag = (type: string) => {
  const map: Record<string, string> = {
    single_choice: '',
    multiple_choice: 'warning',
    judge: 'info',
    fill_in: 'success',
    short_answer: 'danger'
  };
  return map[type] || 'info';
};

const getQuestionTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    single_choice: '单选题',
    multiple_choice: '多选题',
    judge: '判断题',
    fill_in: '填空题',
    short_answer: '简答题'
  };
  return map[type] || type || '题目';
};

const formatAnswer = (ans: any) => {
  if (ans === null || ans === undefined || ans === '') return '未解答/留空';
  if (Array.isArray(ans)) return ans.join(', ');
  if (typeof ans === 'object') return JSON.stringify(ans);
  return String(ans);
};

onMounted(loadRecords);
</script>

<style scoped>
.page-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-box {
  display: flex;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: 800;
  color: #0f172a;
}

.ai-suggestion-box {
  display: flex;
  align-items: center;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.ai-comment-text {
  font-size: 12px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drawer-content {
  padding-bottom: 20px;
}

.exam-header-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #e2e8f0;
}

.header-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.exam-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.header-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #64748b;
}

.ai-eval-card {
  margin-top: 16px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 12px;
  padding: 14px;
}

.ai-eval-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 700;
  color: #166534;
  font-size: 14px;
}

.ai-eval-body {
  margin-top: 8px;
  font-size: 13px;
  color: #15803d;
  line-height: 1.5;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 12px;
}

.q-item-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;

}

.q-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.q-num {
  font-weight: 800;
  color: #0284c7;
}

.q-score {
  margin-left: auto;
  font-size: 12px;
  color: #94a3b8;
}

.q-content {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
  line-height: 1.5;
}

.correct-box {
  background: #f8fafc;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 8px;
}

.correct-box .label {
  color: #64748b;
  font-weight: 600;
}

.correct-box .val {
  color: #16a34a;
  font-weight: 700;
}

.user-answer-box {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
}

.user-answer-box .label {
  color: #1d4ed8;
  font-weight: 700;
  margin-bottom: 4px;
}

.user-answer-box .user-val {
  color: #1e40af;
  font-weight: 600;
  line-height: 1.5;
}

.confirm-footer-box {
  margin-top: 20px;
}
</style>
