<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "../api";
import type { Application } from "../types";
import { daysSince, suggestAccountType } from "../utils";

const router = useRouter();
const applications = ref<Application[]>([]);
const loading = ref(true);

async function refresh() {
  loading.value = true;
  try {
    applications.value = await api.listApplications({ stage: "account_creation" });
  } finally {
    loading.value = false;
  }
}

const summary = computed(() => {
  const total = applications.value.length;
  const waits = applications.value.map((a) =>
    a.decision ? daysSince(a.decision.decided_at) : daysSince(a.created_at),
  );
  const avg =
    waits.length > 0 ? Math.round(waits.reduce((s, n) => s + n, 0) / waits.length) : 0;
  const oldest = waits.length > 0 ? Math.max(...waits) : 0;
  return { total, avg, oldest };
});

function suggestion(app: Application) {
  return suggestAccountType(app);
}

function waitingDays(app: Application) {
  return app.decision ? daysSince(app.decision.decided_at) : daysSince(app.created_at);
}

onMounted(refresh);
</script>

<template>
  <div class="stack">
    <div class="row between">
      <div>
        <div class="section-kicker">Stage 2 · Workspace</div>
        <h2 style="margin: 4px 0 0">Account creation queue</h2>
        <p class="muted" style="margin: 4px 0 0">
          Approved clients waiting for their first bank account. Each row shows a product suggestion —
          open the file to confirm currency, initial deposit, and product.
        </p>
      </div>
      <button @click="refresh">Refresh</button>
    </div>

    <div class="grid cols-3">
      <div class="panel stat">
        <div class="muted">Waiting</div>
        <div class="big" style="color: var(--info)">{{ summary.total }}</div>
        <div class="muted">approved clients</div>
      </div>
      <div class="panel stat">
        <div class="muted">Avg wait</div>
        <div class="big">{{ summary.avg }}</div>
        <div class="muted">days since approval</div>
      </div>
      <div class="panel stat">
        <div class="muted">Oldest</div>
        <div class="big" style="color: var(--warn)">{{ summary.oldest }}</div>
        <div class="muted">days · escalate if &gt; 5</div>
      </div>
    </div>

    <div class="panel">
      <h3 style="margin: 0 0 12px">Ready to open</h3>
      <table>
        <thead>
          <tr>
            <th>Client</th>
            <th>Country</th>
            <th>Risk</th>
            <th>Approved</th>
            <th>Waiting</th>
            <th>Suggested product</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="7" class="muted" style="text-align: center; padding: 24px">Loading…</td></tr>
          <tr v-else-if="applications.length === 0">
            <td colspan="7" class="muted" style="text-align: center; padding: 24px">
              No approved clients waiting — clean slate.
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
            <td class="muted">{{ a.decision ? new Date(a.decision.decided_at).toLocaleDateString() : "—" }}</td>
            <td>
              <span :class="['wait-tag', waitingDays(a) > 5 ? 'overdue' : '']">
                {{ waitingDays(a) }}d
              </span>
            </td>
            <td>
              <div class="row" style="gap: 6px; align-items: flex-start">
                <span class="badge stage-account_creation" style="text-transform: capitalize">
                  {{ suggestion(a).type }}
                </span>
                <span class="muted" style="font-size: 12px">{{ suggestion(a).reason }}</span>
              </div>
            </td>
            <td style="text-align: right">
              <button @click.stop="router.push(`/applications/${a.id}`)">Open account →</button>
            </td>
          </tr>
        </tbody>
      </table>
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
</style>
