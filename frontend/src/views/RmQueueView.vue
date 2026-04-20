<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "../api";
import type { Application, ManagerWithLoad } from "../types";
import { daysSince } from "../utils";

const router = useRouter();
const applications = ref<Application[]>([]);
const managers = ref<ManagerWithLoad[]>([]);
const loading = ref(true);
const busyRowId = ref<string | null>(null);
const error = ref("");

async function refresh() {
  loading.value = true;
  try {
    const [apps, mgrs] = await Promise.all([
      api.listApplications({ stage: "rm_assignment" }),
      api.listRelationshipManagers(),
    ]);
    applications.value = apps;
    managers.value = mgrs;
  } finally {
    loading.value = false;
  }
}

async function autoAssign(app: Application) {
  busyRowId.value = app.id;
  error.value = "";
  try {
    await api.assignRelationshipManager(app.id);
    await refresh();
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    busyRowId.value = null;
  }
}

const summary = computed(() => {
  const waiting = applications.value.length;
  const waits = applications.value.map((a) =>
    a.account ? daysSince(a.account.opened_at) : daysSince(a.created_at),
  );
  const avg =
    waits.length > 0 ? Math.round(waits.reduce((s, n) => s + n, 0) / waits.length) : 0;
  const rmCount = managers.value.length;
  const totalLoad = managers.value.reduce((s, m) => s + m.assigned_count, 0);
  return { waiting, avg, rmCount, totalLoad };
});

function waitingDays(app: Application) {
  return app.account ? daysSince(app.account.opened_at) : daysSince(app.created_at);
}

onMounted(refresh);
</script>

<template>
  <div class="stack">
    <div class="row between">
      <div>
        <div class="section-kicker">Stage 3 · Workspace</div>
        <h2 style="margin: 4px 0 0">Relationship manager assignment</h2>
        <p class="muted" style="margin: 4px 0 0">
          Clients with an open account waiting for a dedicated relationship manager. Auto-match in one click
          or open the file to pick manually.
        </p>
      </div>
      <button @click="refresh">Refresh</button>
    </div>

    <div class="grid cols-4">
      <div class="panel stat">
        <div class="muted">Awaiting RM</div>
        <div class="big" style="color: var(--warn)">{{ summary.waiting }}</div>
        <div class="muted">accounts open</div>
      </div>
      <div class="panel stat">
        <div class="muted">Avg wait</div>
        <div class="big">{{ summary.avg }}</div>
        <div class="muted">days since account opened</div>
      </div>
      <div class="panel stat">
        <div class="muted">RM pool</div>
        <div class="big">{{ summary.rmCount }}</div>
        <div class="muted">active managers</div>
      </div>
      <div class="panel stat">
        <div class="muted">Managed clients</div>
        <div class="big" style="color: var(--success)">{{ summary.totalLoad }}</div>
        <div class="muted">across the pool</div>
      </div>
    </div>

    <div class="grid cols-3" style="align-items: stretch">
      <div class="panel" style="grid-column: span 2">
        <h3 style="margin: 0 0 12px">Clients to assign</h3>
        <p v-if="error" class="error-banner">{{ error }}</p>
        <table>
          <thead>
            <tr>
              <th>Client</th>
              <th>Country</th>
              <th>Risk</th>
              <th>Account</th>
              <th>Waiting</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td colspan="6" class="muted" style="text-align: center; padding: 24px">Loading…</td></tr>
            <tr v-else-if="applications.length === 0">
              <td colspan="6" class="muted" style="text-align: center; padding: 24px">
                All accounts have a relationship manager.
              </td>
            </tr>
            <tr v-else v-for="a in applications" :key="a.id" @click="router.push(`/applications/${a.id}`)">
              <td>
                <div style="font-weight: 500">{{ a.applicant.first_name }} {{ a.applicant.last_name }}</div>
                <div class="muted">{{ a.applicant.email }}</div>
              </td>
              <td>{{ a.applicant.address.country }}</td>
              <td>
                <span v-if="a.risk" class="badge" :class="a.risk.level">{{ a.risk.level }}</span>
              </td>
              <td>
                <span v-if="a.account" class="badge stage-account_creation" style="text-transform: capitalize">
                  {{ a.account.type }} · {{ a.account.currency }}
                </span>
              </td>
              <td>
                <span :class="['wait-tag', waitingDays(a) > 3 ? 'overdue' : '']">{{ waitingDays(a) }}d</span>
              </td>
              <td style="text-align: right">
                <button
                  class="primary"
                  :disabled="busyRowId === a.id"
                  @click.stop="autoAssign(a)"
                >
                  {{ busyRowId === a.id ? "Assigning…" : "Auto-assign" }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <aside class="panel">
        <h3 style="margin: 0 0 12px">RM pool workload</h3>
        <ul class="rm-list">
          <li v-for="m in managers" :key="m.manager.id">
            <div class="row between">
              <div>
                <div style="font-weight: 600">{{ m.manager.name }}</div>
                <div class="muted" style="font-size: 12px; text-transform: capitalize">
                  {{ m.manager.specialization }} · {{ m.manager.languages.map((l) => l.toUpperCase()).join("/") }}
                </div>
              </div>
              <div class="caseload">
                <div class="big">{{ m.assigned_count }}</div>
                <div class="muted" style="font-size: 11px">clients</div>
              </div>
            </div>
          </li>
        </ul>
        <p class="muted" style="font-size: 12px; margin: 12px 0 0">
          Auto-match picks the best specialist; the pool view helps balance workload manually.
        </p>
      </aside>
    </div>
  </div>
</template>

<style scoped>
h2 { font-size: 22px; }
h3 { font-size: 15px; }
.stat .big { font-size: 32px; font-weight: 700; margin: 6px 0; }
.section-kicker {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}
.rm-list { list-style: none; padding: 0; margin: 0; }
.rm-list > li {
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}
.rm-list > li:last-child { border-bottom: none; }
.caseload { text-align: right; }
.caseload .big { font-size: 22px; font-weight: 700; }
.wait-tag {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
}
.wait-tag.overdue {
  background: var(--warn-bg);
  color: var(--warn);
}
.error-banner {
  padding: 10px 14px;
  background: var(--danger-bg);
  color: var(--danger);
  border-radius: 6px;
  font-size: 14px;
  margin: 0 0 12px;
}
</style>
