<script setup lang="ts">
import { computed } from "vue";
import type { OnboardingStage, Status } from "../types";

const props = defineProps<{ stage: OnboardingStage; status: Status }>();

type StepKey = OnboardingStage;
type StepState = "done" | "current" | "locked" | "failed";

interface Step {
  key: StepKey;
  kicker: string;
  label: string;
  sub: string;
}

const steps: Step[] = [
  { key: "kyc", kicker: "Stage 1", label: "KYC verification", sub: "Identity · risk · sanctions" },
  { key: "account_creation", kicker: "Stage 2", label: "Account creation", sub: "Type · currency · deposit" },
  { key: "rm_assignment", kicker: "Stage 3", label: "Relationship manager", sub: "Auto-match or pick" },
  { key: "completed", kicker: "Done", label: "Client onboarded", sub: "Journey complete" },
];

const order: StepKey[] = steps.map((s) => s.key);

const currentIndex = computed(() => order.indexOf(props.stage));
const rejected = computed(() => props.status === "rejected");

function stateFor(key: StepKey): StepState {
  if (rejected.value && key === "kyc") return "failed";
  const idx = order.indexOf(key);
  if (idx < currentIndex.value) return "done";
  if (idx === currentIndex.value) return "current";
  return "locked";
}
</script>

<template>
  <ol class="workflow" :aria-label="`Onboarding journey — current stage: ${stage.replace('_', ' ')}`">
    <li
      v-for="(step, i) in steps"
      :key="step.key"
      class="chevron"
      :class="[
        stateFor(step.key),
        { first: i === 0, last: i === steps.length - 1 },
      ]"
    >
      <div class="inner">
        <div class="marker" aria-hidden="true">
          <template v-if="stateFor(step.key) === 'done' || (step.key === 'completed' && stateFor(step.key) === 'current')">
            ✓
          </template>
          <template v-else-if="stateFor(step.key) === 'failed'">×</template>
          <template v-else>{{ i + 1 }}</template>
        </div>
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
.workflow {
  --step-h: 76px;
  --arrow-w: 18px;
  --gap: 4px;
  --radius: 10px;

  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  gap: var(--gap);
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px;
}

.chevron {
  position: relative;
  flex: 1;
  min-height: var(--step-h);
  padding: 0;
  display: flex;
  transition: filter 0.2s;
}

/* Chevron shape via clip-path.
   - middle: notch on the left, arrow on the right
   - first: flat left, arrow right
   - last:  notch left, flat right                    */
.chevron .inner {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 22px 10px calc(var(--arrow-w) + 14px);
  clip-path: polygon(
    var(--arrow-w) 0,
    calc(100% - var(--arrow-w)) 0,
    100% 50%,
    calc(100% - var(--arrow-w)) 100%,
    var(--arrow-w) 100%,
    0 50%
  );
}
.chevron.first .inner {
  padding-left: 18px;
  clip-path: polygon(
    0 0,
    calc(100% - var(--arrow-w)) 0,
    100% 50%,
    calc(100% - var(--arrow-w)) 100%,
    0 100%
  );
  border-top-left-radius: var(--radius);
  border-bottom-left-radius: var(--radius);
}
.chevron.last .inner {
  padding-right: 18px;
  clip-path: polygon(
    var(--arrow-w) 0,
    100% 0,
    100% 100%,
    var(--arrow-w) 100%,
    0 50%
  );
  border-top-right-radius: var(--radius);
  border-bottom-right-radius: var(--radius);
}

/* States ---------------------------------------------------- */

.chevron.locked .inner {
  background: #f1f5f9;
  color: #94a3b8;
}
.chevron.done .inner {
  background: #10b981;
  color: #ffffff;
}
.chevron.current .inner {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #ffffff;
  box-shadow: 0 6px 18px -6px rgba(79, 70, 229, 0.55);
}
.chevron.failed .inner {
  background: #ef4444;
  color: #ffffff;
}

/* Marker ---------------------------------------------------- */

.marker {
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.22);
  color: inherit;
  border: 2px solid rgba(255, 255, 255, 0.5);
}
.chevron.locked .marker {
  background: #ffffff;
  color: #94a3b8;
  border-color: #e2e8f0;
}

/* Labels ---------------------------------------------------- */

.text { line-height: 1.2; min-width: 0; }
.kicker {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 600;
  opacity: 0.85;
  margin-bottom: 2px;
}
.title {
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sub {
  font-size: 12px;
  opacity: 0.8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Pulse on the current step so the active stage is obvious */
@keyframes pulse {
  0%, 100% { box-shadow: 0 6px 18px -6px rgba(79, 70, 229, 0.55); }
  50%      { box-shadow: 0 6px 26px -4px rgba(79, 70, 229, 0.75); }
}
.chevron.current .inner { animation: pulse 2.2s ease-in-out infinite; }

/* Responsive fallback: stack on small screens */
@media (max-width: 900px) {
  .workflow { flex-direction: column; }
  .chevron { min-height: auto; }
  .chevron .inner,
  .chevron.first .inner,
  .chevron.last .inner {
    clip-path: none;
    padding: 12px 16px;
    border-radius: 8px;
  }
}
</style>
