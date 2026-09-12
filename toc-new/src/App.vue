<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 新增全局极客蓝 CSS 自定义属性与 page 基础样式; 2. 补齐通用盒模型与图片默认行为; 3. 保留既有应用生命周期钩子]
 */
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";

onLaunch(() => {
  console.log("智题库考生端启动");
});
onShow(() => {
  console.log("智题库考生端进入前台");
});
onHide(() => {
  console.log("智题库考生端进入后台");
});
</script>

<style>
/*
 * 全局 CSS 自定义属性。
 * uni.scss 会被注入每一个组件的样式编译单元，只适合放编译期 SCSS 变量；
 * 运行期的自定义属性与 page 级基础样式必须落在 App.vue，才不会被重复输出。
 */
page {
  --geek-blue: #1d63ff;
  --geek-blue-deep: #0045d8;
  --geek-blue-light: #e8f0ff;
  --bg-light: #f6f8fc;
  --bg-card: #ffffff;
  --text-main: #1c2331;
  --text-secondary: #748094;
  --text-placeholder: #a8b2c4;
  --color-success: #00b578;
  --color-warning: #f0883a;
  --color-danger: #fa4350;

  background-color: #f6f8fc;
  color: #1c2331;
  font-family: "PingFang SC", "Helvetica Neue", Helvetica, "Microsoft YaHei", sans-serif;
  font-size: 28rpx;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

view,
text,
image,
input,
scroll-view {
  box-sizing: border-box;
}

image {
  display: block;
}
</style>
