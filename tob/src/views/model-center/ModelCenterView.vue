<!--
  * [变更日志]
  * 修改时间：2026-09-08
  * AI模型：Gemini 系列
  * 修改内容：[1. 全面升级轻奢质感浅色流光渐变卡片 (极高辨识度与极佳可读性，告别暗沉);
  *          2. 弹窗内增加 API 协议选择 (openai-completions / openai-responses / anthropic-messages);
  *          3. 弹窗内嵌入选择模型下拉框 + 独立获取模型按钮，保存时强校验必须选定模型;
  *          4. 卡片中拉取模型文案统一改为「更新模型」，确保每张卡片展示有效选中的模型;
  *          5. 默认通道仅保留云端主力通道，彻底移除无效的本地 3070 默认卡片]
  * 修改时间：2026-09-08
  * AI模型：Gemini 系列
  * 修改内容：[v1.3: 切换模型通道增加连通性检测与 Loading 遮罩，探测失败阻止切换并精准提示错误]
  -->
<template>
  <div class="page-card" v-loading="switching" element-loading-text="正在探测通道连通性并激活主力通道...">
    <div class="mc-header">
      <div>
        <div class="mc-title">模型中心</div>
        <div class="mc-sub">多通道模型网关托管：支持自定义协议、BaseURL 与模型热切换（切换时自动进行健康探活）</div>
      </div>
      <el-button type="primary" class="add-btn" @click="openDialog()">+ 新增通道</el-button>
    </div>

    <!-- 浅色高定卡片网格 -->
    <div class="mc-grid">
      <div
        v-for="(ch, idx) in store.channels"
        :key="ch.id"
        class="mc-card"
        :class="[
          `theme-${idx % lightThemes.length}`,
          { active: ch.id === store.activeChannelId }
        ]"
      >
        <div class="mc-card-top">
          <div class="title-group">
            <span class="mc-name">{{ ch.name }}</span>
            <span class="protocol-badge">{{ ch.protocol || 'openai-completions' }}</span>
          </div>
          <div class="top-tags">
            <span v-if="testResults[ch.id]" class="latency-chip" :class="testResults[ch.id].ok ? 'online' : 'offline'">
              <span class="dot"></span>
              {{ testResults[ch.id].ok ? `${testResults[ch.id].latencyMs}ms` : '连接异常' }}
            </span>
            <span v-if="ch.id === store.activeChannelId" class="active-badge">当前主力</span>
          </div>
        </div>

        <div class="mc-base" :title="ch.baseUrl">{{ ch.baseUrl || '未填写 BaseURL' }}</div>

        <!-- 当前生效模型选择 + 更新模型 -->
        <div class="mc-models-row">
          <el-select
            :model-value="ch.activeModel"
            placeholder="请选择生效模型"
            size="default"
            style="flex: 1"
            class="mc-select"
            @change="(m: string) => store.setActiveModel(ch.id, m)"
          >
            <el-option v-for="m in ch.models" :key="m" :label="m" :value="m" />
          </el-select>
          <el-button
            size="default"
            class="btn-update-models"
            :loading="pullingId === ch.id"
            @click="updateModels(ch.id)"
          >
            更新模型
          </el-button>
        </div>

        <div class="mc-status-desc">
          <span class="status-label">生效模型：</span>
          <strong class="status-val">{{ ch.activeModel || '暂无生效模型' }}</strong>
          <span class="status-count">（共 {{ ch.models.length }} 个备选）</span>
        </div>

        <div class="mc-actions">
          <button
            class="action-link primary"
            :class="{ disabled: ch.id === store.activeChannelId }"
            :disabled="ch.id === store.activeChannelId"
            @click="switchChannel(ch.id)"
          >
            {{ ch.id === store.activeChannelId ? '主力生效中' : '设为主力通道' }}
          </button>
          <span class="action-divider">|</span>
          <button
            class="action-link"
            :disabled="testingId === ch.id"
            @click="testProbe(ch.id)"
          >
            {{ testingId === ch.id ? '探活中...' : '测试连通性' }}
          </button>
          <span class="action-divider">|</span>
          <button class="action-link" @click="openDialog(ch)">编辑</button>
          <span class="action-divider">|</span>
          <button class="action-link danger" @click="removeChannel(ch.id)">删除</button>
        </div>
      </div>
    </div>

    <!-- 通道新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑通道' : '新增通道'"
      width="540px"
      destroy-on-close
      class="channel-dialog"
    >
      <el-form :model="form" label-width="96px" size="default">
        <el-form-item label="通道名称" required>
          <el-input v-model="form.name" placeholder="如：本地 3070 / Dots 云端主力" maxlength="40" />
        </el-form-item>

        <el-form-item label="BaseURL" required>
          <el-input
            v-model="form.baseUrl"
            placeholder="如：https://note3-prev-api.askdiandian.com/v1"
            clearable
          />
        </el-form-item>

        <el-form-item label="API 协议" required>
          <el-select v-model="form.protocol" placeholder="选择 API 协议" style="width: 100%">
            <el-option label="openai-completions" value="openai-completions" />
            <el-option label="openai-responses" value="openai-responses" />
            <el-option label="anthropic-messages" value="anthropic-messages" />
          </el-select>
        </el-form-item>

        <el-form-item label="API Key">
          <el-input
            v-model="form.apiKey"
            type="password"
            show-password
            placeholder="可留空（本地 Ollama / vLLM 模型一般留空）"
          />
        </el-form-item>

        <!-- 弹窗内选择模型 + 获取模型 -->
        <el-form-item label="选择模型" required>
          <div class="dialog-model-row">
            <el-select
              v-model="form.activeModel"
              placeholder="请选择或输入模型名称"
              filterable
              allow-create
              default-first-option
              style="flex: 1"
            >
              <el-option v-for="m in form.models" :key="m" :label="m" :value="m" />
            </el-select>
            <el-button
              type="primary"
              plain
              :loading="dialogPulling"
              @click="fetchDialogModels"
            >
              获取模型
            </el-button>
          </div>
          <div class="form-hint">
            先填写 BaseURL（与可选 Key），点击「获取模型」即可自动拉取，或直接在此输入自定义模型名。
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveChannel">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useModelCenterStore, ApiProtocol } from '../../store/modelCenter';

const store = useModelCenterStore();

// 轻奢质感浅色流光渐变调色板（双色微弥散，高对比度暗黑文字，舒适高级）
const lightThemes = [
  { key: 'blue' },
  { key: 'purple' },
  { key: 'emerald' },
  { key: 'amber' },
  { key: 'rose' }
];

const dialogVisible = ref(false);
const editingId = ref('');
const pullingId = ref('');
const testingId = ref('');
const dialogPulling = ref(false);
const switching = ref(false);
const saving = ref(false);

const testResults = reactive<Record<string, { ok: boolean; latencyMs: number }>>({});

const form = reactive({
  name: '',
  baseUrl: '',
  protocol: 'openai-completions' as ApiProtocol,
  apiKey: '',
  models: [] as string[],
  activeModel: ''
});

const openDialog = (ch?: any) => {
  if (ch) {
    editingId.value = ch.id;
    form.name = ch.name;
    form.baseUrl = ch.baseUrl;
    form.protocol = ch.protocol || 'openai-completions';
    form.apiKey = ch.apiKey;
    form.models = Array.isArray(ch.models) && ch.models.length > 0 ? [...ch.models] : (ch.activeModel ? [ch.activeModel] : []);
    form.activeModel = ch.activeModel || form.models[0] || '';
  } else {
    editingId.value = '';
    form.name = '';
    form.baseUrl = '';
    form.protocol = 'openai-completions';
    form.apiKey = '';
    form.models = [];
    form.activeModel = '';
  }
  dialogVisible.value = true;
};

// 弹窗中点击「获取模型」
const fetchDialogModels = async () => {
  if (!form.baseUrl.trim()) {
    ElMessage.warning('请先填写 BaseURL 才能获取模型');
    return;
  }
  dialogPulling.value = true;
  try {
    const list = await store.fetchModelsByConfig(form.baseUrl, form.apiKey);
    form.models = list;
    if (list.length > 0 && (!form.activeModel || !list.includes(form.activeModel))) {
      form.activeModel = list[0];
    }
    ElMessage.success(`成功获取到 ${list.length} 个可用模型`);
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.error?.message || e?.message || '获取模型失败，请检查 BaseURL/Key 或允许跨域');
  } finally {
    dialogPulling.value = false;
  }
};

// 保存通道（强校验：必须选定生效模型）
const saveChannel = () => {
  if (!form.name.trim()) {
    ElMessage.error('请填写通道名称');
    return;
  }
  if (!form.baseUrl.trim()) {
    ElMessage.error('请填写 BaseURL');
    return;
  }
  if (!form.activeModel.trim()) {
    ElMessage.error('请先获取或选择一个生效模型');
    return;
  }

  saving.value = true;
  try {
    const models = form.models.length > 0 ? form.models : [form.activeModel];
    if (editingId.value) {
      store.updateChannel(editingId.value, {
        name: form.name,
        baseUrl: form.baseUrl,
        protocol: form.protocol,
        apiKey: form.apiKey,
        models,
        activeModel: form.activeModel
      });
      ElMessage.success('通道已更新');
    } else {
      store.addChannel({
        name: form.name,
        baseUrl: form.baseUrl,
        protocol: form.protocol,
        apiKey: form.apiKey,
        models,
        activeModel: form.activeModel
      });
      ElMessage.success('通道已成功新增');
    }
    dialogVisible.value = false;
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败');
  } finally {
    saving.value = false;
  }
};

const removeChannel = async (id: string) => {
  try {
    await ElMessageBox.confirm('确定删除该通道吗？删除后不可恢复。', '删除提示', {
      type: 'warning',
      confirmButtonText: '确定删除',
      cancelButtonText: '取消'
    });
  } catch (e) {
    return;
  }
  store.removeChannel(id);
  ElMessage.success('通道已删除');
};

// 卡片中点击「更新模型」
const updateModels = async (id: string) => {
  pullingId.value = id;
  try {
    const models = await store.fetchModels(id);
    ElMessage.success(`模型已同步更新，共 ${models.length} 个模型`);
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.error?.message || e?.message || '更新模型失败，请检查通道网络状态');
  } finally {
    pullingId.value = '';
  }
};

// 切换主力通道（带探活与异常阻断）
const switchChannel = async (channelId: string) => {
  switching.value = true;
  try {
    const res = await store.testConnection(channelId);
    testResults[channelId] = { ok: res.ok, latencyMs: res.latencyMs };
    if (!res.ok) {
      ElMessageBox.alert(
        `切换失败：无法连接该模型通道。\n原因：${res.error || '连接超时或服务未就绪'}。\n\n请确认该通道的 BaseURL 是否正确可用。`,
        '通道连通异常',
        { type: 'error', confirmButtonText: '确定' }
      );
      return;
    }
    store.setActiveChannel(channelId);
    ElMessage.success(`已成功切换为主力通道（响应延迟 ${res.latencyMs}ms）`);
  } catch (e: any) {
    ElMessage.error(e?.message || '切换失败');
  } finally {
    switching.value = false;
  }
};

// 单独测试连通性
const testProbe = async (channelId: string) => {
  testingId.value = channelId;
  try {
    const res = await store.testConnection(channelId);
    testResults[channelId] = { ok: res.ok, latencyMs: res.latencyMs };
    if (res.ok) {
      ElMessage.success(`连通性良好！响应延迟: ${res.latencyMs}ms`);
    } else {
      ElMessage.error(`连通性异常: ${res.error}`);
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '探测失败');
  } finally {
    testingId.value = '';
  }
};
</script>

<style scoped>
.page-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px 28px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.mc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.mc-title {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
}

.mc-sub {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.add-btn {
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 8px;
}

/* 网格布局 */
.mc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

/* 卡片基础骨架 */
.mc-card {
  border-radius: 16px;
  padding: 20px 22px;
  border: 1px solid #e2e8f0;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
  position: relative;
  overflow: hidden;
}

.mc-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.07);
}

/* 浅色流光渐变主题包 (高明度/低饱和度，温润优雅) */
.mc-card.theme-0 {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-color: #bae6fd;
}
.mc-card.theme-1 {
  background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
  border-color: #e9d5ff;
}
.mc-card.theme-2 {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #bbf7d0;
}
.mc-card.theme-3 {
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border-color: #fed7aa;
}
.mc-card.theme-4 {
  background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 100%);
  border-color: #fbcfe8;
}

/* 激活主力状态外发光与边框 */
.mc-card.active {
  border-color: #0284c7;
  box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.25), 0 12px 28px rgba(2, 132, 199, 0.12);
}

/* 头部 */
.mc-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mc-name {
  font-size: 16px;
  font-weight: 800;
  color: #0f172a;
}

.protocol-badge {
  font-size: 11px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.35);
  color: #475569;
  padding: 1px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.top-tags {
  display: flex;
  align-items: center;
  gap: 6px;
}

.active-badge {
  font-size: 12px;
  font-weight: 700;
  background: #0284c7;
  color: #ffffff;
  padding: 2px 8px;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(2, 132, 199, 0.3);
}

.latency-chip {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.latency-chip.online {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
}

.latency-chip.offline {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

/* BaseURL */
.mc-base {
  font-size: 12px;
  color: #64748b;
  margin: 8px 0 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: Consolas, Monaco, monospace;
  background: rgba(255, 255, 255, 0.6);
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

/* 模型选择与更新按钮行 */
.mc-models-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-update-models {
  background: #ffffff;
  border-color: #cbd5e1;
  color: #334155;
  font-weight: 600;
  flex-shrink: 0;
}

.btn-update-models:hover {
  color: #0284c7;
  border-color: #0284c7;
}

/* 状态描述 */
.mc-status-desc {
  font-size: 12px;
  margin-top: 10px;
  color: #475569;
  display: flex;
  align-items: center;
}

.status-label {
  color: #64748b;
}

.status-val {
  color: #0f172a;
  margin-left: 2px;
  font-family: monospace;
}

.status-count {
  color: #94a3b8;
  margin-left: 4px;
}

/* 底部操作条 */
.mc-actions {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(203, 213, 225, 0.5);
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-link {
  background: none;
  border: none;
  padding: 0;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: color 0.15s;
}

.action-link:hover {
  color: #0284c7;
}

.action-link.primary {
  color: #0284c7;
  font-weight: 700;
}

.action-link.primary.disabled {
  color: #94a3b8;
  cursor: default;
}

.action-link.danger {
  color: #ef4444;
  margin-left: auto;
}

.action-link.danger:hover {
  color: #dc2626;
}

.action-divider {
  color: #cbd5e1;
  font-size: 12px;
}

/* 弹窗专用样式 */
.dialog-model-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

.form-hint {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 6px;
  line-height: 1.4;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
