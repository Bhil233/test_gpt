<script setup>
defineProps({
  monitorForm: {
    type: Object,
    required: true,
  },
  monitorLoading: {
    type: Boolean,
    required: true,
  },
  monitorSubmitting: {
    type: Boolean,
    required: true,
  },
  monitorErrorText: {
    type: String,
    required: true,
  },
  monitorRows: {
    type: Array,
    required: true,
  },
  monitorSortBy: {
    type: String,
    required: true,
  },
  monitorSortOrder: {
    type: String,
    required: true,
  },
  formatDateTime: {
    type: Function,
    required: true,
  },
  getMonitorStatusText: {
    type: Function,
    required: true,
  },
  getMonitorStatusClass: {
    type: Function,
    required: true,
  },
  resolveMonitorImageUrl: {
    type: Function,
    required: true,
  },
});

const emit = defineEmits([
  "monitor-image-change",
  "monitor-remark-change",
  "save-monitor-record",
  "cancel-edit-monitor-record",
  "load-monitor-records",
  "monitor-sort-by-change",
  "monitor-sort-order-change",
  "start-edit-monitor-record",
  "delete-monitor-record",
]);
</script>

<template>
  <section class="monitor-page">
    <h2>数据监控</h2>

    <section class="monitor-form-card">
      <h3>{{ monitorForm.id === null ? "新增监控记录" : `编辑记录 #${monitorForm.id}` }}</h3>

      <div class="monitor-form-grid">
        <label class="form-item">
          <span>现场图片 (jpg)</span>
          <input
            type="file"
            accept=".jpg,.jpeg,image/jpeg,image/jpg"
            @change="emit('monitor-image-change', $event)"
          />
        </label>
        <p class="hint">状态将由系统自动识别（fire/normal）。</p>

        <label class="form-item full">
          <span>备注</span>
          <textarea
            :value="monitorForm.remark"
            rows="2"
            placeholder="可选，补充说明"
            @input="emit('monitor-remark-change', $event.target.value)"
          ></textarea>
        </label>
        <div v-if="monitorForm.scene_image_preview" class="form-item full">
          <span>图片预览</span>
          <img class="table-image" :src="monitorForm.scene_image_preview" alt="现场图片预览" />
        </div>
      </div>

      <div class="monitor-actions">
        <button :disabled="monitorSubmitting" @click="emit('save-monitor-record')">
          {{ monitorSubmitting ? "提交中..." : monitorForm.id === null ? "新增" : "更新" }}
        </button>
        <button
          v-if="monitorForm.id !== null"
          type="button"
          class="ghost-btn"
          :disabled="monitorSubmitting"
          @click="emit('cancel-edit-monitor-record')"
        >
          取消编辑
        </button>
        <button type="button" class="ghost-btn" :disabled="monitorLoading" @click="emit('load-monitor-records')">
          {{ monitorLoading ? "刷新中..." : "刷新列表" }}
        </button>
      </div>
    </section>

    <p v-if="monitorErrorText" class="error">{{ monitorErrorText }}</p>

    <section class="result-card">
      <h3>监控数据列表</h3>
      <div class="monitor-sort-bar">
        <label class="sort-item">
          <span>排序字段</span>
          <select :value="monitorSortBy" @change="emit('monitor-sort-by-change', $event.target.value)">
            <option value="id">ID</option>
            <option value="status">状态</option>
            <option value="remark">备注</option>
            <option value="created_at">创建时间</option>
            <option value="updated_at">更新时间</option>
          </select>
        </label>
        <label class="sort-item">
          <span>排序方式</span>
          <select :value="monitorSortOrder" @change="emit('monitor-sort-order-change', $event.target.value)">
            <option value="desc">降序</option>
            <option value="asc">升序</option>
          </select>
        </label>
      </div>

      <p v-if="monitorLoading" class="hint">加载中...</p>
      <p v-else-if="!monitorRows.length" class="hint">暂无数据。</p>

      <div v-else class="table-wrap">
        <table class="monitor-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>现场图片</th>
              <th>状态</th>
              <th>备注</th>
              <th>创建时间</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in monitorRows" :key="row.id">
              <td>{{ row.id }}</td>
              <td>
                <img class="table-image" :src="resolveMonitorImageUrl(row.scene_image_url)" alt="现场图片" />
                <p class="image-path">{{ row.scene_image_path }}</p>
              </td>
              <td>
                <span :class="getMonitorStatusClass(row.status)">
                  {{ getMonitorStatusText(row.status) }}
                </span>
              </td>
              <td>{{ row.remark || "-" }}</td>
              <td>{{ formatDateTime(row.created_at) }}</td>
              <td>{{ formatDateTime(row.updated_at) }}</td>
              <td class="table-actions">
                <button type="button" class="table-btn" @click="emit('start-edit-monitor-record', row)">编辑</button>
                <button type="button" class="table-btn danger-btn" @click="emit('delete-monitor-record', row.id)">
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>
