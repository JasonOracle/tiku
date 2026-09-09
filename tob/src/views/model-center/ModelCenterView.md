# ModelCenterView 动态模型中心

## 💡 核心思想

模型中心：
1. **浅色高定微弥散渐变美学 (Light Luxury Design)**：摒弃传统生硬暗沉的暗色卡片，采用高明度、低饱和度的双色微弥散轻奢渐变（冰川蓝、晨曦紫、薄荷绿、暖阳杏、浅胭粉），卡片文本与表单采用高对比度深色高精字色（`#0f172a`），通透清爽。
2. **闭环配置流程（弹窗内选择模型 + 强校验）**：新增或编辑通道弹窗中，支持配置 API 协议（`openai-completions` / `openai-responses` / `anthropic-messages`），内嵌模型下拉框及「获取模型」按钮。用户可一键探活拉取或手动输入模型，**必须选定生效模型才允许保存**，彻底杜绝无模型通道。
3. **卡片展示与在线更新**：卡片上只展示已配置生效的模型；右侧提供「更新模型」按钮用于重新同步远端模型清单；切换主力通道时全屏 Loading 进行真实连通性探活，异常时精准阻断提示。
4. **剔除冗余**：默认仅保留 Dots 云端主力通道，彻底移除离线的本地 3070 默认卡片。

## 💻 使用示例

```vue
<!-- router/index.ts -->
{
  path: 'model-center',
  name: 'ModelCenter',
  component: () => import('../views/model-center/ModelCenterView.vue'),
  meta: { title: '模型中心' }
}
```

```ts
import { useModelCenterStore } from '../../store/modelCenter';

const mcStore = useModelCenterStore();
// 获取当前主力生效模型及协议
console.log(mcStore.activeModel); // 如 'dots3-note-prev'
console.log(mcStore.activeChannel?.protocol); // 如 'openai-completions'
```
