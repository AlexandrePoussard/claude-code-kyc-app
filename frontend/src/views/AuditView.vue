<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "../api";
import type { AuditEntry } from "../types";

const router = useRouter();
const entries = ref<AuditEntry[]>([]);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    entries.value = await api.listAudit();
  } finally {
    loading.value = false;
  }
}

function open(entry: AuditEntry) {
  if (entry.application_id) router.push(`/applications/${entry.application_id}`);
}

onMounted(load);
</script>

<template>
  <div class="panel">
    <div class="row between" style="margin-bottom: 16px">
      <h2 style="margin: 0">Audit log</h2>
      <button @click="load">Refresh</button>
    </div>
    <table>
      <thead>
        <tr>
          <th>When</th>
          <th>Actor</th>
          <th>Action</th>
          <th>Application</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading"><td colspan="5" class="muted">Loading…</td></tr>
        <tr v-else-if="entries.length === 0"><td colspan="5" class="muted">No entries yet.</td></tr>
        <tr v-else v-for="e in entries" :key="e.id" @click="open(e)">
          <td class="muted">{{ new Date(e.at).toLocaleString() }}</td>
          <td>{{ e.actor }}</td>
          <td><code>{{ e.action }}</code></td>
          <td>
            <span v-if="e.application_id" class="mono">{{ e.application_id.slice(0, 8) }}…</span>
            <span v-else class="muted">—</span>
          </td>
          <td class="muted">{{ Object.keys(e.details).length ? JSON.stringify(e.details) : "—" }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
h2 { font-size: 22px; }
code { background: #fafbfd; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
.mono { font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 13px; }
</style>
