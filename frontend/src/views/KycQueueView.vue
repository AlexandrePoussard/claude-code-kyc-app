<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "../api";
import type { Application, RiskLevel, Status } from "../types";
import StatusBadge from "../components/StatusBadge.vue";
import RiskDonut from "../components/charts/RiskDonut.vue";

const router = useRouter();
const applications = ref<Application[]>([]);
const loading = ref(true);
const statusFilter = ref<Status | "">("");
const riskFilter = ref<RiskLevel | "">("");
const query = ref("");

async function refresh() {
  loading.value = true;
  try {
    applications.value = await api.listApplications({
      stage: "kyc",
      status: statusFilter.value || undefined,
      risk: riskFilter.value || undefined,
      q: query.value || undefined,
    });
  } finally {
    loading.value = false;
  }
}

const summary = computed(() => {
  const pending = applications.value.filter((a) => a.status === "pending").length;
  const inReview = applications.value.filter((a) => a.status === "in_review").length;
  const rejected = applications.value.filter((a) => a.status === "rejected").length;
  const highRisk = applications.value.filter((a) => a.risk?.level === "high").length;
  const sanctionHits = applications.value.filter((a) => a.sanctions && !a.sanctions.clear).length;
  return { pending, inReview, rejected, highRisk, sanctionHits };
});

const riskCounts = computed(() => ({
  low: applications.value.filter((a) => a.risk?.level === "low").length,
  medium: applications.value.filter((a) => a.risk?.level === "medium").length,
  high: applications.value.filter((a) => a.risk?.level === "high").length,
}));

onMounted(refresh);
</script>

<template>
  <div class="stack">
    <div class="row between">
      <div>
        <div class="section-kicker">Stage 1 · Workspace</div>
        <h2 style="margin: 4px 0 0">KYC verification queue</h2>
        <p class="muted" style="margin: 4px 0 0">
          Review identity, risk, sanctions and liveness. Approve to unlock account creation; reject to close the file.
        </p>
      </div>
      <button @click="refresh">Refresh</button>
    </div>

    <div class="grid cols-4">
      <div class="panel stat">
        <div class="muted">Pending</div>
        <div class="big" style="color: var(--info)">{{ summary.pending }}</div>
        <div class="muted">new files</div>
      </div>
      <div class="panel stat">
        <div class="muted">In review</div>
        <div class="big" style="color: var(--warn)">{{ summary.inReview }}</div>
        <div class="muted">reviewer action needed</div>
      </div>
      <div class="panel stat">
        <div class="muted">High risk</div>
        <div class="big" style="color: var(--danger)">{{ summary.highRisk }}</div>
        <div class="muted">requires EDD</div>
      </div>
      <div class="panel stat">
        <div class="muted">Sanctions hits</div>
        <div class="big" style="color: var(--warn)">{{ summary.sanctionHits }}</div>
        <div class="muted">need adjudication</div>
      </div>
    </div>

    <div class="grid cols-3" style="align-items: stretch">
      <div class="panel" style="grid-column: span 2">
        <div class="row between" style="margin-bottom: 12px">
          <h3 style="margin: 0">Queue</h3>
          <div class="row" style="gap: 8px">
            <input v-model="query" placeholder="Search name or email" style="width: 200px" @keyup.enter="refresh" />
            <select v-model="statusFilter" @change="refresh" style="width: auto">
              <option value="">All statuses</option>
              <option value="pending">Pending</option>
              <option value="in_review">In review</option>
              <option value="rejected">Rejected</option>
            </select>
            <select v-model="riskFilter" @change="refresh" style="width: auto">
              <option value="">All risks</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
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
            <tr v-if="loading"><td colspan="7" class="muted" style="text-align: center; padding: 24px">Loading…</td></tr>
            <tr v-else-if="applications.length === 0">
              <td colspan="7" class="muted" style="text-align: center; padding: 24px">No KYC files match the filters.</td>
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

      <div class="panel">
        <h3>Risk mix in queue</h3>
        <RiskDonut :counts="riskCounts" />
        <p class="muted" style="margin-top: 12px">
          Based on the applications currently visible in the table.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
h2 { font-size: 22px; }
h3 { margin: 0 0 12px; font-size: 15px; }
.stat .big { font-size: 32px; font-weight: 700; margin: 6px 0; }
.section-kicker {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}
</style>
