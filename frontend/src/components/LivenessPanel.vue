<script setup lang="ts">
import type { LivenessResult } from "../types";
defineProps<{ liveness: LivenessResult | null; busy?: boolean }>();
defineEmits<{ (e: "run"): void }>();
</script>

<template>
  <section class="panel">
    <div class="row between">
      <h3>Liveness check</h3>
      <button :disabled="busy" @click="$emit('run')">
        {{ busy ? "Running…" : "Run liveness check" }}
      </button>
    </div>
    <div v-if="!liveness" class="muted">No liveness check performed.</div>
    <div v-else class="liveness-body">
      <div class="row" style="gap: 8px">
        <span v-if="liveness.passed" class="badge low">Passed</span>
        <span v-else class="badge high">Failed</span>
        <span class="muted">Confidence {{ (liveness.confidence * 100).toFixed(0) }}%</span>
      </div>
      <p class="challenge">Challenge issued: <em>"{{ liveness.challenge }}"</em></p>
      <p class="muted">Checked {{ new Date(liveness.checked_at).toLocaleString() }}</p>
    </div>
  </section>
</template>

<style scoped>
h3 { margin: 0; font-size: 16px; }
.liveness-body { margin-top: 12px; }
.challenge { margin: 12px 0 4px; font-size: 14px; }
</style>
