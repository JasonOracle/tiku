<!--
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗重写：租户级网关覆盖（脱敏回显+连通测试+总开关），旧本机localStorage stub已删除]
-->
<template>
  <div class="page-card">
    <div class="page-title">AI 模型配置</div>
    <div class="page-sub">
      本企业专属网关覆盖；留空则继承服务端环境配置。密钥仅脱敏回显，置空提交表示沿用旧值。
      <el-tag size="small" :type="source === 'tenant' ? 'success' : 'info'" effect="plain" style="margin-left: 8px">
        当前生效：{{ source === 'tenant' ? '企业专属' : '服务端环境' }} · {{ envModel }}
      </el-tag>
    </div>

    <el-form label-width="140px" style="max-width: 680px; margin-top: 20px" v-loading="loading">
      <el-form-item label="企业 AI 总开关">
        <el-switch v-model="form.enabled" />
        <span class="hint">关闭后本企业 AI 出题/对话/核验全部走人工兜底</span>
      </el-form-item>
      <el-form-item label="对话网关地址">
        <el-input v-model="form.chat_api_url" placeholder="https://…/v1/chat/completions" />
      </el-form-item>
      <el-form-item label="对话 API Key">
        <el-input v-model="form.chat_api_key" type="password" show-password placeholder="置空=沿用旧值" />
      </el-form-item>
      <el-form-item label="对话模型">
        <el-input v-model="form.chat_model" placeholder="如 dots3-note-prev" />
      </el-form-item>
      <el-form-item label="向量模型">
        <el-input v-model="form.embed_model" placeholder="选填，默认跟随对话网关" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="saving" @click="save">保存到服务端</el-button>
        <el-button :loading="testing" @click="testConn">连通测试</el-button>
        <el-button type="danger" plain @click="clearKey">清除专属 Key 回退环境</el-button>
      </el-form-item>
      <el-form-item v-if="testResult" label="测试结果">
        <el-tag :type="testResult.ok ? 'success' : 'danger'" size="small">
          {{ testResult.ok ? `连通正常 · ${testResult.latency_ms}ms · ${testResult.source}` : '失败' }}
        </el-tag>
        <div v-if="testResult.reply" class="reply">{{ testResult.reply }}</div>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '../../utils/request';

const loading = ref(false);
const saving = ref(false);
const testing = ref(false);
const source = ref('env');
const envModel = ref('');
const testResult = ref<any>(null);

const form = reactive({
  enabled: true,
  chat_api_url: '',
  chat_api_key: '',
  chat_model: '',
  embed_model: ''
});

const load = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/ai/config');
    form.enabled = res.enabled ?? true;
    form.chat_api_url = res.chat_api_url || '';
    form.chat_api_key = res.chat_api_key_masked || '';
    form.chat_model = res.chat_model || '';
    form.embed_model = res.embed_model || '';
    source.value = res.source || 'env';
    envModel.value = res.env_model || '';
  } finally {
    loading.value = false;
  }
};

const save = async () => {
  saving.value = true;
  try {
    await request.put('/api/v1/admin/ai/config', { ...form });
    ElMessage.success('企业 AI 配置已保存');
    testResult.value = null;
    load();
  } finally {
    saving.value = false;
  }
};

const testConn = async () => {
  testing.value = true;
  try {
    const res: any = await request.post('/api/v1/admin/ai/config/test', { ...form }, { timeout: 120000 });
    testResult.value = res;
    if (res.ok) ElMessage.success(`连通正常（${res.latency_ms}ms）`);
  } finally {
    testing.value = false;
  }
};

const clearKey = async () => {
  try {
    await ElMessageBox.confirm('清除企业专属 Key 并回退服务端环境配置？', '提示', { type: 'warning' });
  } catch (e) {
    return;
  }
  saving.value = true;
  try {
    await request.put('/api/v1/admin/ai/config', { clear_key: true });
    ElMessage.success('已回退环境配置');
    form.chat_api_key = '';
    load();
  } finally {
    saving.value = false;
  }
};

onMounted(load);
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
  line-height: 2;
}

.hint {
  font-size: 12px;
  color: #94a3b8;
  margin-left: 10px;
}

.reply {
  font-size: 13px;
  color: #334155;
  background: #f8fafc;
  border-radius: 8px;
  padding: 8px 12px;
  margin-top: 8px;
  width: 100%;
  box-sizing: border-box;
}
</style>
