<script setup lang="ts">
import type { SanctionsResult } from "../types";
defineProps<{ sanctions: SanctionsResult | null; busy?: boolean }>();
defineEmits<{ (e: "rerun"): void }>();
</script>

<template>
  <section class="panel">
    <div class="row between">
      <h3>Sanctions screening</h3>
      <button :disabled="busy" @click="$emit('rerun')">
        {{ busy ? "Screening…" : "Re-run screening" }}
      </button>
    </div>
    <div v-if="!sanctions" class="muted">Not screened yet.</div>
    <template v-else>
      <div class="row" style="gap: 8px; margin-bottom: 12px">
        <span v-if="sanctions.clear" class="badge low">Clear</span>
        <span v-else class="badge high">{{ sanctions.hits.length }} potential hits</span>
        <span class="muted">Checked {{ new Date(sanctions.checked_at).toLocaleString() }}</span>
      </div>
      <table v-if="sanctions.hits.length > 0">
        <thead>
          <tr>
            <th>List</th>
            <th>Matched name</th>
            <th>Score</th>
            <th>Reason</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(h, i) in sanctions.hits" :key="i">
            <td>{{ h.list_name }}</td>
            <td>{{ h.matched_name }}</td>
            <td>{{ (h.score * 100).toFixed(0) }}%</td>
            <td>{{ h.reason }}</td>
          </tr>
        </tbody>
      </table>
    </template>
  </section>
</template>

<style scoped>
h3 { margin: 0; font-size: 16px; }
</style>
