<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "../api";
import type { Application, RiskLevel, Stats, Status } from "../types";
import StatusBadge from "../components/StatusBadge.vue";
import StatusBreakdownBar from "../components/charts/StatusBreakdownBar.vue";
import RiskDonut from "../components/charts/RiskDonut.vue";
import SubmissionsSparkline from "../components/charts/SubmissionsSparkline.vue";

const router = useRouter();
const applications = ref<Application[]>([]);
const stats = ref<Stats | null>(null);
const loading = ref(true);
const statusFilter = ref<Status | "">("");
const riskFilter = ref<RiskLevel | "">("");
const query = ref("");

async function refresh() {
  loading.value = true;
  try {
    const [apps, s] = await Promise.all([
      api.listApplications({
        status: statusFilter.value || undefined,
        risk: riskFilter.value || undefined,
        q: query.value || undefined,
      }),
      api.getStats(),
    ]);
    applications.value = apps;
    stats.value = s;
  } finally {
    loading.value = false;
  }
}

onMounted(refresh);
</script>

<template>
  <div class="stack">
    <div v-if="stats" class="grid cols-4">
      <div class="panel stat">
        <div class="muted">Total applications</div>
        <div class="big">{{ stats.total }}</div>
        <div class="muted">in the system</div>
      </div>
      <div class="panel stat">
        <div class="muted">Queue</div>
        <div class="big">{{ stats.status_counts.pending + stats.status_counts.in_review }}</div>
        <div class="muted">awaiting review</div>
      </div>
      <div class="panel stat">
        <div class="muted">High risk</div>
        <div class="big" style="color: var(--danger)">{{ stats.risk_counts.high }}</div>
        <div class="muted">flagged profiles</div>
      </div>
      <div class="panel stat">
        <div class="muted">Sanctions hits</div>
        <div class="big" style="color: var(--warn)">{{ stats.sanctions_hits }}</div>
        <div class="muted">require adjudication</div>
      </div>
    </div>

    <div v-if="stats" class="grid cols-3">
      <div class="panel">
        <h3>Status breakdown</h3>
        <StatusBreakdownBar :counts="stats.status_counts" />
      </div>
      <div class="panel">
        <h3>Risk distribution</h3>
        <RiskDonut :counts="stats.risk_counts" />
      </div>
      <div class="panel">
        <h3>Submissions · last 30 days</h3>
        <SubmissionsSparkline :series="stats.submissions_last_30_days" />
      </div>
    </div>

    <div class="panel">
      <div class="row between" style="margin-bottom: 16px">
        <h2 style="margin: 0">Applications</h2>
        <div class="row" style="gap: 8px">
          <input v-model="query" placeholder="Search name or email" style="width: 220px" @keyup.enter="refresh" />
          <select v-model="statusFilter" @change="refresh" style="width: auto">
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="in_review">In review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <select v-model="riskFilter" @change="refresh" style="width: auto">
            <option value="">All risks</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <button @click="refresh">Refresh</button>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Applicant</th>
            <th>Country</th>
            <th>Status</th>
            <th>Risk</th>
            <th>Sanctions</th>
            <th>Liveness</th>
            <th>Submitted</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="muted" style="text-align: center; padding: 24px">Loading…</td>
          </tr>
          <tr v-else-if="applications.length === 0">
            <td colspan="7" class="muted" style="text-align: center; padding: 24px">No applications match the filters.</td>
          </tr>
          <tr v-else v-for="a in applications" :key="a.id" @click="router.push(`/applications/${a.id}`)">
            <td>
              <div style="font-weight: 500">{{ a.applicant.first_name }} {{ a.applicant.last_name }}</div>
              <div class="muted">{{ a.applicant.email }}</div>
            </td>
            <td>{{ a.applicant.address.country }}</td>
            <td><StatusBadge :value="a.status" /></td>
            <td>
              <span v-if="a.risk" class="badge" :class="a.risk.level">{{ a.risk.level }} · {{ a.risk.score }}</span>
            </td>
            <td>
              <span v-if="a.sanctions?.clear" class="badge low">clear</span>
              <span v-else-if="a.sanctions" class="badge high">{{ a.sanctions.hits.length }} hit(s)</span>
            </td>
            <td>
              <span v-if="a.liveness?.passed" class="badge low">pass</span>
              <span v-else-if="a.liveness" class="badge high">fail</span>
              <span v-else class="muted">—</span>
            </td>
            <td class="muted">{{ new Date(a.created_at).toLocaleDateString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.stat .big { font-size: 32px; font-weight: 700; margin: 6px 0; }
h3 { margin: 0 0 12px; font-size: 15px; }
</style>
