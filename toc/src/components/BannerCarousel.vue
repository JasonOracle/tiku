<!-- 首页Banner轮播：1张静显，超1张按秒数自播+圆点+手滑 -->
<template>
  <section v-if="items.length" class="banner-wrap">
    <div
      class="banner-track"
      :style="{ transform: `translateX(-${idx * 100}%)`, transition: anim ? 'transform .35s ease' : 'none' }"
      @touchstart="onTouchStart"
      @touchend="onTouchEnd"
      @click="onClick(items[idx])"
    >
      <div v-for="b in items" :key="b.id" class="banner-slide">
        <img :src="b.image_url" alt="banner" />
      </div>
    </div>
    <div v-if="items.length > 1" class="dots">
      <span v-for="(b, i) in items" :key="b.id" class="dot" :class="{ active: i === idx }" @click.stop="go(i)"></span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';

const props = withDefaults(defineProps<{ items?: any[]; interval?: number }>(), {
  items: () => [],
  interval: 4
});

const router = useRouter();
const idx = ref(0);
const anim = ref(true);
let timer: any = null;
let touchX = 0;

const stop = () => {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
};

const play = () => {
  stop();
  if (props.items.length > 1) {
    const sec = Math.min(Math.max(props.interval || 4, 2), 10);
    timer = setInterval(() => {
      idx.value = (idx.value + 1) % props.items.length;
    }, sec * 1000);
  }
};

const go = (i: number) => {
  idx.value = i;
};

const onTouchStart = (e: TouchEvent) => {
  touchX = e.touches[0].clientX;
  stop();
};

const onTouchEnd = (e: TouchEvent) => {
  const dx = e.changedTouches[0].clientX - touchX;
  if (Math.abs(dx) > 40 && props.items.length > 1) {
    idx.value = (idx.value + (dx < 0 ? 1 : props.items.length - 1)) % props.items.length;
  }
  play();
};

const onClick = (b: any) => {
  if (!b || b.link_type === 'none' || !b.link_value) return;
  if (b.link_type === 'external') {
    window.location.href = b.link_value;
    return;
  }
  // 内部路径仅允许 / 开头，防外跳
  if (b.link_type === 'internal' && b.link_value.startsWith('/')) {
    router.push(b.link_value);
  }
};

watch(() => [props.items.length, props.interval], play);
onMounted(play);
onUnmounted(stop);
</script>

<style scoped>
.banner-wrap {
  margin: 10px 20px 0;
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  box-shadow: 0 12px 30px rgba(2, 132, 199, 0.25);
}
.banner-track { display: flex; }
.banner-slide { flex: 0 0 100%; aspect-ratio: 16 / 9; }
.banner-slide img { width: 100%; height: 100%; object-fit: cover; display: block; }
.dots {
  position: absolute;
  bottom: 10px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 6px;
}
.dot { width: 6px; height: 6px; border-radius: 50%; background: rgba(255, 255, 255, 0.5); cursor: pointer; }
.dot.active { width: 18px; border-radius: 4px; background: white; }
</style>
