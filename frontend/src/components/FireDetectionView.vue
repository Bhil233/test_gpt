<script setup>
defineProps({
  manualCanUpload: {
    type: Boolean,
    required: true,
  },
  manualLoading: {
    type: Boolean,
    required: true,
  },
  manualPreviewUrl: {
    type: String,
    required: true,
  },
  manualErrorText: {
    type: String,
    required: true,
  },
  manualResultText: {
    type: String,
    required: true,
  },
  manualFireDetected: {
    type: Boolean,
    required: true,
  },
  scriptPreviewUrl: {
    type: String,
    required: true,
  },
  scriptResultText: {
    type: String,
    required: true,
  },
  scriptFireDetected: {
    type: Boolean,
    required: true,
  },
  scriptErrorText: {
    type: String,
    required: true,
  },
  scriptSocketConnected: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(["manual-file-change", "detect-manual-fire"]);
</script>

<template>
  <div class="layout">
    <aside class="sidebar">
      <section class="panel">
        <h2>手动上传</h2>
        <p class="hint">在网页手动选择图片并检测。</p>

        <input type="file" accept="image/*" @change="emit('manual-file-change', $event)" />

        <button :disabled="!manualCanUpload" @click="emit('detect-manual-fire')">
          {{ manualLoading ? "检测中..." : "开始检测" }}
        </button>
      </section>

      <section class="panel">
        <h2>自动上传</h2>
        <p class="hint">由系统自动上传</p>
      </section>
    </aside>

    <section class="workspace">
      <h2>工作区</h2>
      <section class="result-card">
        <h3>手动上传结果</h3>
        <div v-if="manualPreviewUrl" class="preview-wrap">
          <img :src="manualPreviewUrl" alt="手动上传预览图" />
        </div>
        <p v-else class="hint">请先在左侧选择图片。</p>
        <p v-if="manualErrorText" class="error">{{ manualErrorText }}</p>
        <p v-else-if="manualResultText" :class="manualFireDetected ? 'danger' : 'safe'">
          {{ manualResultText }}
        </p>
      </section>

      <section class="result-card">
        <h3>自动上传结果</h3>
        <p :class="scriptSocketConnected ? 'connected' : 'disconnected'">
          {{ scriptSocketConnected ? "实时连接正常" : "连接断开，正在重连..." }}
        </p>
        <div v-if="scriptPreviewUrl" class="preview-wrap">
          <img :src="scriptPreviewUrl" alt="脚本上传预览图" />
        </div>
        <p v-else class="hint">等待脚本上传图片...</p>
        <p v-if="scriptErrorText" class="error">{{ scriptErrorText }}</p>
        <p v-else-if="scriptResultText" :class="scriptFireDetected ? 'danger' : 'safe'">
          {{ scriptResultText }}
        </p>
      </section>
    </section>
  </div>
</template>
