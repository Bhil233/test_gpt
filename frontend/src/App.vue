<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import NavigationMenu from "./components/NavigationMenu.vue";
import FireDetectionView from "./components/FireDetectionView.vue";
import DataMonitorView from "./components/DataMonitorView.vue";
import { apiBase } from "./config/api";
import { useScriptSocket } from "./composables/useScriptSocket";
import {
  createMonitorRecord,
  deleteMonitorRecordRequest,
  detectManualFireRequest,
  fetchMonitorRecords,
  updateMonitorRecord,
} from "./services/fireApi";
import {
  formatDateTime,
  getMonitorStatusClass,
  getMonitorStatusText,
  resolveMonitorImageUrl,
} from "./utils/format";

const activeMenu = ref("fire_detection");

const manualSelectedFile = ref(null);
const manualPreviewUrl = ref("");
const manualLoading = ref(false);
const manualResultText = ref("");
const manualFireDetected = ref(false);
const manualErrorText = ref("");
const manualCanUpload = computed(
  () => !!manualSelectedFile.value && !manualLoading.value
);

const {
  scriptPreviewUrl,
  scriptResultText,
  scriptFireDetected,
  scriptErrorText,
  scriptSocketConnected,
  connectScriptSocket,
  cleanupScriptSocket,
} = useScriptSocket();

const monitorRows = ref([]);
const monitorLoading = ref(false);
const monitorSubmitting = ref(false);
const monitorErrorText = ref("");
const monitorSortBy = ref("created_at");
const monitorSortOrder = ref("desc");
const monitorForm = ref({
  id: null,
  scene_image_file: null,
  scene_image_preview: "",
  remark: "",
});

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
    const data = await detectManualFireRequest(apiBase, manualSelectedFile.value);
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

function resetMonitorForm() {
  if (monitorForm.value.scene_image_preview?.startsWith("blob:")) {
    URL.revokeObjectURL(monitorForm.value.scene_image_preview);
  }
  monitorForm.value = {
    id: null,
    scene_image_file: null,
    scene_image_preview: "",
    remark: "",
  };
}

async function loadMonitorRecords() {
  monitorLoading.value = true;
  monitorErrorText.value = "";

  try {
    monitorRows.value = await fetchMonitorRecords(
      apiBase,
      monitorSortBy.value,
      monitorSortOrder.value
    );
  } catch (error) {
    monitorErrorText.value = error.message || "请求失败";
    monitorRows.value = [];
  } finally {
    monitorLoading.value = false;
  }
}

function onMonitorImageChange(event) {
  const file = event.target.files?.[0] || null;
  if (monitorForm.value.scene_image_preview?.startsWith("blob:")) {
    URL.revokeObjectURL(monitorForm.value.scene_image_preview);
  }
  monitorForm.value.scene_image_file = file;
  if (file) {
    monitorForm.value.scene_image_preview = URL.createObjectURL(file);
  } else {
    monitorForm.value.scene_image_preview = "";
  }
}

function onMonitorRemarkChange(value) {
  monitorForm.value.remark = value;
}

function onMonitorSortByChange(value) {
  monitorSortBy.value = value;
  void loadMonitorRecords();
}

function onMonitorSortOrderChange(value) {
  monitorSortOrder.value = value;
  void loadMonitorRecords();
}

async function saveMonitorRecord() {
  monitorSubmitting.value = true;
  monitorErrorText.value = "";

  try {
    const remark = monitorForm.value.remark.trim();
    const editingId = monitorForm.value.id;
    const isEdit = editingId !== null;
    if (!isEdit && !monitorForm.value.scene_image_file) {
      throw new Error("新增记录必须上传 jpg 图片");
    }

    if (isEdit) {
      await updateMonitorRecord(
        apiBase,
        editingId,
        remark,
        monitorForm.value.scene_image_file
      );
    } else {
      await createMonitorRecord(apiBase, remark, monitorForm.value.scene_image_file);
    }

    resetMonitorForm();
    await loadMonitorRecords();
  } catch (error) {
    monitorErrorText.value = error.message || "请求失败";
  } finally {
    monitorSubmitting.value = false;
  }
}

function startEditMonitorRecord(record) {
  if (monitorForm.value.scene_image_preview?.startsWith("blob:")) {
    URL.revokeObjectURL(monitorForm.value.scene_image_preview);
  }
  monitorForm.value = {
    id: record.id,
    scene_image_file: null,
    scene_image_preview: resolveMonitorImageUrl(record.scene_image_url, apiBase),
    remark: record.remark ?? "",
  };
}

function cancelEditMonitorRecord() {
  resetMonitorForm();
}

async function deleteMonitorRecord(recordId) {
  if (!window.confirm("确认删除这条监控记录吗？")) {
    return;
  }

  monitorErrorText.value = "";
  try {
    await deleteMonitorRecordRequest(apiBase, recordId);
    await loadMonitorRecords();
    if (monitorForm.value.id === recordId) {
      resetMonitorForm();
    }
  } catch (error) {
    monitorErrorText.value = error.message || "请求失败";
  }
}

function resolveMonitorImageUrlWithBase(url) {
  return resolveMonitorImageUrl(url, apiBase);
}

watch(
  activeMenu,
  (menu) => {
    if (menu === "data_monitor") {
      void loadMonitorRecords();
    }
  },
  { immediate: true }
);

onMounted(() => {
  connectScriptSocket();
});

onBeforeUnmount(() => {
  if (manualPreviewUrl.value) {
    URL.revokeObjectURL(manualPreviewUrl.value);
  }
  cleanupScriptSocket();
  if (monitorForm.value.scene_image_preview?.startsWith("blob:")) {
    URL.revokeObjectURL(monitorForm.value.scene_image_preview);
  }
});
</script>

<template>
  <main class="page">
    <h1 class="title">AI智能火灾监测系统</h1>

    <NavigationMenu v-model:active-menu="activeMenu" />

    <FireDetectionView
      v-if="activeMenu === 'fire_detection'"
      :manual-can-upload="manualCanUpload"
      :manual-loading="manualLoading"
      :manual-preview-url="manualPreviewUrl"
      :manual-error-text="manualErrorText"
      :manual-result-text="manualResultText"
      :manual-fire-detected="manualFireDetected"
      :script-preview-url="scriptPreviewUrl"
      :script-result-text="scriptResultText"
      :script-fire-detected="scriptFireDetected"
      :script-error-text="scriptErrorText"
      :script-socket-connected="scriptSocketConnected"
      @manual-file-change="onManualFileChange"
      @detect-manual-fire="detectManualFire"
    />

    <DataMonitorView
      v-else
      :monitor-form="monitorForm"
      :monitor-loading="monitorLoading"
      :monitor-submitting="monitorSubmitting"
      :monitor-error-text="monitorErrorText"
      :monitor-rows="monitorRows"
      :monitor-sort-by="monitorSortBy"
      :monitor-sort-order="monitorSortOrder"
      :format-date-time="formatDateTime"
      :get-monitor-status-text="getMonitorStatusText"
      :get-monitor-status-class="getMonitorStatusClass"
      :resolve-monitor-image-url="resolveMonitorImageUrlWithBase"
      @monitor-image-change="onMonitorImageChange"
      @monitor-remark-change="onMonitorRemarkChange"
      @save-monitor-record="saveMonitorRecord"
      @cancel-edit-monitor-record="cancelEditMonitorRecord"
      @load-monitor-records="loadMonitorRecords"
      @monitor-sort-by-change="onMonitorSortByChange"
      @monitor-sort-order-change="onMonitorSortOrderChange"
      @start-edit-monitor-record="startEditMonitorRecord"
      @delete-monitor-record="deleteMonitorRecord"
    />
  </main>
</template>
