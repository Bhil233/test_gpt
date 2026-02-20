<script setup>
defineProps({
  activeMenu: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["update:activeMenu"]);

function switchMenu(menu) {
  emit("update:activeMenu", menu);
}
</script>

<template>
  <nav class="menu">
    <button
      type="button"
      class="menu-btn"
      :class="{ active: activeMenu === 'fire_detection' }"
      @click="switchMenu('fire_detection')"
    >
      火灾检测
    </button>
    <button
      type="button"
      class="menu-btn"
      :class="{ active: activeMenu === 'data_monitor' }"
      @click="switchMenu('data_monitor')"
    >
      数据监控
    </button>
  </nav>
</template>
