<script setup lang="ts">
import type { RiskAssessment } from "../types";
defineProps<{ risk: RiskAssessment | null }>();
</script>

<template>
  <section class="panel">
    <div class="row between">
      <h3>Risk assessment</h3>
      <span v-if="risk" class="badge" :class="risk.level">{{ risk.level }} · {{ risk.score }}</span>
    </div>
    <div v-if="!risk" class="muted">No assessment yet.</div>
    <ul v-else class="factors">
      <li v-for="f in risk.factors" :key="f.code">
        <span>{{ f.label }}</span>
        <span class="weight">+{{ f.weight }}</span>
      </li>
      <li v-if="risk.factors.length === 0" class="muted">No risk factors triggered — clean profile.</li>
    </ul>
  </section>
</template>

<style scoped>
h3 { margin: 0 0 12px; font-size: 16px; }
.factors { list-style: none; padding: 0; margin: 0; }
.factors li {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
}
.factors li:last-child { border-bottom: none; }
.weight { font-weight: 600; color: var(--warn); }
</style>
