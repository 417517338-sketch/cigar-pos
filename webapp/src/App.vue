<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { tts } from './services/tts'

// 预加载语音列表
onMounted(() => {
  speechSynthesis.getVoices()
  // 读取设置
})
</script>
