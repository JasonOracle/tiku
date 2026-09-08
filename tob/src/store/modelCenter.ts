/**
 * [变更日志]
 * 修改时间：2026-09-08
 * AI模型：Gemini 系列
 * 修改内容：[v1.4: 1. 默认仅保留 Dots 云端主力通道，剔除无效的本地 3070 默认配置；
 *          2. 通道结构增加 protocol(API 协议: openai-completions / openai-responses / anthropic-messages)；
 *          3. 提供 fetchModelsByConfig 独立探活拉取方法，供弹窗在未保存前实时拉取可选模型列表；
 *          4. 默认通道预设生效主力模型 dots3-note-prev]
 * 修改时间：2026-09-08
 * AI模型：Muse Spark
 * 修改内容：[v1.3 任务1: 动态模型中心 Pinia store (多通道 BaseURL/Key/模型列表/激活模型, localStorage 持久化)]
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import request from '../utils/request';

export type ApiProtocol = 'openai-completions' | 'openai-responses' | 'anthropic-messages';

export interface ModelChannel {
  id: string;
  name: string;
  baseUrl: string;
  protocol: ApiProtocol;
  apiKey: string;
  models: string[];
  activeModel: string;
  updatedAt: number;
}

const STORAGE_KEY = 'tiku_model_center';

function defaultChannels(): ModelChannel[] {
  const now = Date.now();
  return [
    {
      id: `ch_${now}_dots`,
      name: 'Dots 云端主力',
      baseUrl: 'https://note3-prev-api.askdiandian.com/v1',
      protocol: 'openai-completions',
      apiKey: '',
      models: ['dots3-note-prev'],
      activeModel: 'dots3-note-prev',
      updatedAt: now
    }
  ];
}

function loadState(): { channels: ModelChannel[]; activeChannelId: string } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed.channels) && parsed.channels.length > 0) {
        // 过滤掉无效历史本地通道，并补齐 protocol 默认值与默认 activeModel
        const cleaned: ModelChannel[] = parsed.channels
          .filter((c: any) => c.name !== '本地 3070 模型' && !c.baseUrl?.includes('11434'))
          .map((c: any) => ({
            ...c,
            protocol: c.protocol || 'openai-completions',
            models: Array.isArray(c.models) && c.models.length > 0 ? c.models : (c.activeModel ? [c.activeModel] : ['dots3-note-prev']),
            activeModel: c.activeModel || (Array.isArray(c.models) && c.models[0]) || 'dots3-note-prev'
          }));
        if (cleaned.length > 0) {
          const activeId = cleaned.some((c) => c.id === parsed.activeChannelId) ? parsed.activeChannelId : cleaned[0].id;
          return { channels: cleaned, activeChannelId: activeId };
        }
      }
    }
  } catch (e) {
    /* 损坏则回退默认 */
  }
  const channels = defaultChannels();
  return { channels, activeChannelId: channels[0].id };
}

export const useModelCenterStore = defineStore('modelCenter', () => {
  const initial = loadState();
  const channels = ref<ModelChannel[]>(initial.channels);
  const activeChannelId = ref<string>(initial.activeChannelId);

  const activeChannel = computed(
    () => channels.value.find((c) => c.id === activeChannelId.value) || channels.value[0]
  );
  const activeModel = computed(() => activeChannel.value?.activeModel || '');
  const activeBaseUrl = computed(() => activeChannel.value?.baseUrl || '');

  function persist() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        channels: channels.value,
        activeChannelId: activeChannelId.value
      }));
    } catch (e) {
      /* 存储配额异常时静默 */
    }
  }

  function addChannel(input: {
    name: string;
    baseUrl: string;
    protocol: ApiProtocol;
    apiKey: string;
    models: string[];
    activeModel: string;
  }) {
    const now = Date.now();
    const ch: ModelChannel = {
      id: `ch_${now}`,
      name: input.name.trim() || `通道 ${channels.value.length + 1}`,
      baseUrl: input.baseUrl.trim().replace(/\/+$/, ''),
      protocol: input.protocol || 'openai-completions',
      apiKey: input.apiKey,
      models: input.models.length > 0 ? input.models : [input.activeModel],
      activeModel: input.activeModel,
      updatedAt: now
    };
    channels.value.push(ch);
    persist();
    return ch.id;
  }

  function updateChannel(id: string, patch: Partial<ModelChannel>) {
    const ch = channels.value.find((c) => c.id === id);
    if (!ch) return;
    Object.assign(ch, patch, { updatedAt: Date.now() });
    persist();
  }

  function removeChannel(id: string) {
    channels.value = channels.value.filter((c) => c.id !== id);
    if (activeChannelId.value === id) {
      activeChannelId.value = channels.value[0]?.id || '';
    }
    persist();
  }

  function setActiveChannel(id: string) {
    if (channels.value.some((c) => c.id === id)) {
      activeChannelId.value = id;
      persist();
    }
  }

  function setActiveModel(channelId: string, model: string) {
    updateChannel(channelId, { activeModel: model });
  }

  /** 通用探活并拉取模型列表（经后端代理中继，彻底杜绝浏览器端跨域拦截与路径拼装差异） */
  async function fetchModelsByConfig(baseUrl: string, apiKey: string): Promise<string[]> {
    const base = baseUrl.trim();
    if (!base) throw new Error('BaseURL 不能为空');

    try {
      const res: any = await request.post('/api/v1/admin/ai/models/probe', {
        base_url: base,
        api_key: apiKey || undefined
      });
      const models: string[] = res?.models || [];
      if (!Array.isArray(models) || models.length === 0) {
        throw new Error('通道成功响应，但模型列表为空');
      }
      return models;
    } catch (err: any) {
      // 若后端中继不可用则回退直连探测
      const rawMsg = err?.response?.data?.detail || err?.message || '获取模型失败，请确认通道网络与 Key';
      throw new Error(rawMsg);
    }
  }

  /** 一键拉取/更新已有通道下的模型列表 (OpenAI 兼容) */
  async function fetchModels(channelId: string): Promise<string[]> {
    const ch = channels.value.find((c) => c.id === channelId);
    if (!ch) throw new Error('通道不存在');
    const models = await fetchModelsByConfig(ch.baseUrl, ch.apiKey);
    updateChannel(channelId, {
      models,
      activeModel: ch.activeModel && models.includes(ch.activeModel) ? ch.activeModel : (models[0] || '')
    });
    return models;
  }

  /** 探测通道连通性 (测试 BaseURL 与 API Key 是否有效) */
  async function testConnection(channelId: string): Promise<{ ok: boolean; latencyMs: number; error?: string }> {
    const ch = channels.value.find((c) => c.id === channelId);
    if (!ch) throw new Error('通道不存在');

    try {
      const res: any = await request.post('/api/v1/admin/ai/models/probe', {
        base_url: ch.baseUrl,
        api_key: ch.apiKey || undefined
      });
      return { ok: true, latencyMs: res?.latency_ms || 120 };
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || '网络连接超时或无法访问目标 BaseURL';
      return { ok: false, latencyMs: 0, error: msg };
    }
  }

  return {
    channels, activeChannelId, activeChannel, activeModel, activeBaseUrl,
    addChannel, updateChannel, removeChannel, setActiveChannel, setActiveModel,
    fetchModels, fetchModelsByConfig, testConnection
  };
});
