<script setup lang="ts">
defineProps<{ value: string }>();
</script>

<template>
  <span class="badge" :class="value">{{ value.replace("_", " ") }}</span>
</template>
