<script setup lang="ts">
import type { StageCounts } from "../types";

defineProps<{ counts: StageCounts }>();

interface FlowStep {
  key: keyof StageCounts;
  kicker: string;
  label: string;
  sub: string;
}

const steps: FlowStep[] = [
  { key: "kyc", kicker: "Stage 1", label: "KYC verification", sub: "Identity · risk · sanctions" },
  { key: "account_creation", kicker: "Stage 2", label: "Account creation", sub: "Type · currency · deposit" },
  { key: "rm_assignment", kicker: "Stage 3", label: "Relationship manager", sub: "Auto-match or pick" },
  { key: "completed", kicker: "Done", label: "Fully onboarded", sub: "Client active" },
];
</script>

<template>
  <ol class="flow" aria-label="Client onboarding pipeline">
    <li
      v-for="(step, i) in steps"
      :key="step.key"
      class="chevron"
      :class="[`tone-${step.key}`, { first: i === 0, last: i === steps.length - 1 }]"
    >
      <div class="inner">
        <div class="count">{{ counts[step.key] }}</div>
        <div class="text">
          <div class="kicker">{{ step.kicker }}</div>
          <div class="title">{{ step.label }}</div>
          <div class="sub">{{ step.sub }}</div>
        </div>
      </div>
    </li>
  </ol>
</template>

<style scoped>
.flow {
  --h: 96px;
  --arrow: 28px;
  --gap: 4px;
  --radius: 12px;

  list-style: none;
  padding: 12px;
  margin: 0;
  display: flex;
  gap: var(--gap);
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.chevron {
  flex: 1;
  min-height: var(--h);
  display: flex;
}

.chevron .inner {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 28px 14px calc(var(--arrow) + 18px);
  color: #ffffff;
  clip-path: polygon(
    var(--arrow) 0,
    calc(100% - var(--arrow)) 0,
    100% 50%,
    calc(100% - var(--arrow)) 100%,
    var(--arrow) 100%,
    0 50%
  );
}
.chevron.first .inner {
  padding-left: 22px;
  clip-path: polygon(
    0 0,
    calc(100% - var(--arrow)) 0,
    100% 50%,
    calc(100% - var(--arrow)) 100%,
    0 100%
  );
  border-top-left-radius: var(--radius);
  border-bottom-left-radius: var(--radius);
}
.chevron.last .inner {
  padding-right: 22px;
  clip-path: polygon(
    var(--arrow) 0,
    100% 0,
    100% 100%,
    var(--arrow) 100%,
    0 50%
  );
  border-top-right-radius: var(--radius);
  border-bottom-right-radius: var(--radius);
}

/* Stage tones — distinct colors that hint "flow" left to right */
.chevron.tone-kyc .inner               { background: linear-gradient(135deg, #6366f1, #4338ca); }
.chevron.tone-account_creation .inner  { background: linear-gradient(135deg, #06b6d4, #0369a1); }
.chevron.tone-rm_assignment .inner     { background: linear-gradient(135deg, #f59e0b, #b45309); }
.chevron.tone-completed .inner         { background: linear-gradient(135deg, #10b981, #047857); }

/* The big count number inside each chevron */
.count {
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
  min-width: 48px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.text { line-height: 1.2; min-width: 0; }
.kicker {
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-weight: 700;
  opacity: 0.85;
}
.title {
  font-size: 15px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}
.sub {
  font-size: 12px;
  opacity: 0.85;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 900px) {
  .flow { flex-direction: column; }
  .chevron { min-height: auto; }
  .chevron .inner,
  .chevron.first .inner,
  .chevron.last .inner {
    clip-path: none;
    padding: 14px 18px;
    border-radius: 10px;
  }
}
</style>
