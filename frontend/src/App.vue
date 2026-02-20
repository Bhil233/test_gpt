<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

const apiBase = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

const manualSelectedFile = ref(null);
const manualPreviewUrl = ref("");
const manualLoading = ref(false);
const manualResultText = ref("");
const manualFireDetected = ref(false);
const manualErrorText = ref("");
const manualCanUpload = computed(
  () => !!manualSelectedFile.value && !manualLoading.value
);

const scriptPreviewUrl = ref("");
const scriptResultText = ref("");
const scriptFireDetected = ref(false);
const scriptErrorText = ref("");
const scriptSocketConnected = ref(false);
let scriptSocket = null;
let scriptReconnectTimer = null;

function getWsBaseUrl(httpBase) {
  if (httpBase.startsWith("https://")) {
    return `wss://${httpBase.slice("https://".length)}`;
  }
  if (httpBase.startsWith("http://")) {
    return `ws://${httpBase.slice("http://".length)}`;
  }
  return httpBase;
}

function scheduleScriptReconnect() {
  if (scriptReconnectTimer !== null) {
    return;
  }
  scriptReconnectTimer = window.setTimeout(() => {
    scriptReconnectTimer = null;
    connectScriptSocket();
  }, 2000);
}

function connectScriptSocket() {
  if (
    scriptSocket &&
    (scriptSocket.readyState === WebSocket.OPEN ||
      scriptSocket.readyState === WebSocket.CONNECTING)
  ) {
    return;
  }

  const wsBase = getWsBaseUrl(apiBase);
  const wsUrl = `${wsBase}/ws/script/latest-upload-image`;
  const socket = new WebSocket(wsUrl);
  scriptSocket = socket;

  socket.onopen = () => {
    scriptSocketConnected.value = true;
    scriptErrorText.value = "";
  };

  socket.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      if (payload.type !== "script_upload_result") {
        return;
      }
      if (payload.image_data_url) {
        scriptPreviewUrl.value = payload.image_data_url;
      }
      scriptFireDetected.value = !!payload.fire_detected;
      scriptResultText.value = payload.result_text || "";
      scriptErrorText.value = "";
    } catch {
      scriptErrorText.value = "脚本模块消息解析失败";
    }
  };

  socket.onclose = () => {
    if (scriptSocket === socket) {
      scriptSocket = null;
      scriptSocketConnected.value = false;
      scheduleScriptReconnect();
    }
  };

  socket.onerror = () => {
    socket.close();
  };
}

function onManualFileChange(event) {
  const file = event.target.files?.[0] || null;
  manualSelectedFile.value = file;
  manualResultText.value = "";
  manualErrorText.value = "";
  manualFireDetected.value = false;

  if (manualPreviewUrl.value) {
    URL.revokeObjectURL(manualPreviewUrl.value);
    manualPreviewUrl.value = "";
  }

  if (file) {
    manualPreviewUrl.value = URL.createObjectURL(file);
  }
}

async function detectManualFire() {
  if (!manualSelectedFile.value) {
    return;
  }

  manualLoading.value = true;
  manualResultText.value = "";
  manualErrorText.value = "";
  manualFireDetected.value = false;

  try {
    const formData = new FormData();
    formData.append("file", manualSelectedFile.value);

    const response = await fetch(`${apiBase}/api/manual/detect-fire`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "检测失败，请稍后重试。");
    }

    manualResultText.value = data.result_text || "";
    manualFireDetected.value = !!data.fire_detected;

    if (manualFireDetected.value) {
      window.alert("警告：检测到火灾！请立即处理并报警！");
    }
  } catch (error) {
    manualErrorText.value = error.message || "请求失败";
  } finally {
    manualLoading.value = false;
  }
}

onMounted(() => {
  connectScriptSocket();
});

onBeforeUnmount(() => {
  if (manualPreviewUrl.value) {
    URL.revokeObjectURL(manualPreviewUrl.value);
  }
  if (scriptSocket) {
    scriptSocket.close();
    scriptSocket = null;
  }
  if (scriptReconnectTimer !== null) {
    clearTimeout(scriptReconnectTimer);
    scriptReconnectTimer = null;
  }
});
</script>

<template>
  <main class="page">
    <h1 class="title">AI智能火灾监测系统</h1>
    <div class="modules">
      <section class="panel">
        <h2>模块一：手动上传</h2>
        <p class="hint">在网页手动选择图片并检测。</p>

        <input type="file" accept="image/*" @change="onManualFileChange" />

        <div v-if="manualPreviewUrl" class="preview-wrap">
          <img :src="manualPreviewUrl" alt="手动上传预览图" />
        </div>

        <button :disabled="!manualCanUpload" @click="detectManualFire">
          {{ manualLoading ? "检测中..." : "开始检测" }}
        </button>

        <p v-if="manualErrorText" class="error">{{ manualErrorText }}</p>
        <p v-else-if="manualResultText" :class="manualFireDetected ? 'danger' : 'safe'">
          {{ manualResultText }}
        </p>
      </section>

      <section class="panel">
        <h2>模块二：脚本上传</h2>
        <p class="hint">运行上传脚本后，此处会实时显示图片与检测结果。</p>
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
    </div>
  </main>
</template>

<style scoped>
:global(*) {
  box-sizing: border-box;
}

:global(body) {
  margin: 0;
  min-height: 100vh;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  background: linear-gradient(135deg, #fff8f5 0%, #ffe4d9 100%);
  color: #1f2937;
}

.page {
  min-height: 100vh;
  padding: 24px;
  display: grid;
  gap: 16px;
  align-content: start;
  width: min(1080px, 100%);
  margin: 0 auto;
}

.title {
  margin: 0;
  color: #7c2d12;
  font-size: 30px;
}

.modules {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.panel {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 18px 40px rgba(187, 52, 0, 0.15);
  display: grid;
  gap: 12px;
}

h2 {
  margin: 0;
  color: #7c2d12;
}

.hint {
  margin: 0;
  color: #4b5563;
}

input[type="file"] {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px;
}

.preview-wrap {
  width: 100%;
}

.preview-wrap img {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 12px;
  border: 1px solid #f3f4f6;
  background: #fff;
}

button {
  appearance: none;
  border: 0;
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #ef4444, #ea580c);
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.connected {
  margin: 0;
  color: #047857;
  font-weight: 700;
}

.disconnected {
  margin: 0;
  color: #b45309;
  font-weight: 700;
}

.error {
  margin: 0;
  color: #b91c1c;
}

.danger {
  margin: 0;
  color: #b91c1c;
  font-weight: 700;
}

.safe {
  margin: 0;
  color: #047857;
  font-weight: 700;
}
</style>
