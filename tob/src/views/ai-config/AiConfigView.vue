<!--
  * [变更日志]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[新建: AI 模型配置预留静态页 (主力/备用 Key 本地保存, 演示环境不落库)]
  -->
<template>
  <div class="page-card">
    <div class="page-title">AI 模型配置</div>
    <div class="page-sub">预留页面：演示环境下配置保存在本机浏览器，不会写入服务端。</div>

    <el-form label-width="140px" style="max-width: 640px; margin-top: 20px">
      <el-form-item label="主力模型网关">
        <el-input v-model="form.primaryUrl" placeholder="https://…" />
      </el-form-item>
      <el-form-item label="主力 API Key">
        <el-input v-model="form.primaryKey" type="password" show-password placeholder="留空则使用服务端配置" />
      </el-form-item>
      <el-form-item label="备用 API Key">
        <el-input v-model="form.backupKey" type="password" show-password placeholder="故障转移备用 Key" />
      </el-form-item>
      <el-form-item label="阅卷模型">
        <el-input v-model="form.gradingModel" placeholder="如 dots3-note-prev" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="saveLocal">保存到本机</el-button>
        <el-button @click="clearLocal">清空本机配置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

const KEY = 'tiku_ai_config_preview';

const form = reactive({
  primaryUrl: '',
  primaryKey: '',
  backupKey: '',
  gradingModel: ''
});

onMounted(() => {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) Object.assign(form, JSON.parse(raw));
  } catch (e) {
    /* 忽略损坏的本地配置 */
  }
});

const saveLocal = () => {
  localStorage.setItem(KEY, JSON.stringify(form));
  ElMessage.success('已保存到本机浏览器（演示环境，不影响服务端）');
};

const clearLocal = () => {
  localStorage.removeItem(KEY);
  form.primaryUrl = '';
  form.primaryKey = '';
  form.backupKey = '';
  form.gradingModel = '';
  ElMessage.success('本机配置已清空');
};
</script>

<style scoped>
.page-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.page-title {
  font-size: 17px;
  font-weight: 800;
  color: #0f172a;
}

.page-sub {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}
</style>
