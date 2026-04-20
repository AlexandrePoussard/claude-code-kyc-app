<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../api";
import type { Stats } from "../types";
import StageFlow from "../components/StageFlow.vue";
import StatusBreakdownBar from "../components/charts/StatusBreakdownBar.vue";
import RiskDonut from "../components/charts/RiskDonut.vue";
import SubmissionsSparkline from "../components/charts/SubmissionsSparkline.vue";
import FunnelBar from "../components/charts/FunnelBar.vue";
import TopFactorsBar from "../components/charts/TopFactorsBar.vue";
import TopCountriesBar from "../components/charts/TopCountriesBar.vue";
import LivenessHistogram from "../components/charts/LivenessHistogram.vue";
import ReviewerLeaderboard from "../components/charts/ReviewerLeaderboard.vue";

const stats = ref<Stats | null>(null);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    stats.value = await api.getStats();
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div v-if="loading" class="muted">Loading overview…</div>
  <div v-else-if="stats" class="stack">
    <section class="stack" style="gap: 6px">
      <div class="section-kicker">Client onboarding pipeline</div>
      <StageFlow :counts="stats.stage_counts" />
    </section>

    <div class="grid cols-3">
      <div class="panel">
        <h3>KYC status breakdown</h3>
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

    <section class="panel">
      <h3>Review funnel</h3>
      <p class="muted">How applications progress from submission to approval.</p>
      <FunnelBar :funnel="stats.funnel" />
    </section>

    <div class="grid cols-2">
      <section class="panel">
        <h3>Top risk factors</h3>
        <p class="muted">Rules that fire most often across all applications.</p>
        <TopFactorsBar :factors="stats.top_risk_factors" />
      </section>

      <section class="panel">
        <h3>Top countries of residence</h3>
        <p class="muted">Where applicants are based (ISO-2 country codes).</p>
        <TopCountriesBar :countries="stats.top_countries" />
      </section>

      <section class="panel">
        <h3>Liveness confidence distribution</h3>
        <p class="muted">How confident the fake liveness check was, bucketed.</p>
        <LivenessHistogram :buckets="stats.liveness_confidence_buckets" />
      </section>

      <section class="panel">
        <h3>Reviewer leaderboard</h3>
        <p class="muted">Decisions per reviewer, split by outcome.</p>
        <ReviewerLeaderboard :reviewers="stats.reviewer_stats" />
      </section>
    </div>
  </div>
</template>

<style scoped>
h3 { margin: 0 0 6px; font-size: 16px; }
.section-kicker {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}
</style>
