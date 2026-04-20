<script setup lang="ts">
import { reactive, ref } from "vue";
import type { AccountType, BankAccount, OnboardingStage } from "../types";

const props = defineProps<{
  account: BankAccount | null;
  stage: OnboardingStage;
  busy?: boolean;
}>();
const emit = defineEmits<{
  (e: "create", payload: { type: AccountType; currency: string; initial_deposit: number }): void;
}>();

const form = reactive({
  type: "checking" as AccountType,
  currency: "EUR",
  initial_deposit: 1000,
});
const error = ref("");

function submit() {
  error.value = "";
  if (!form.currency || form.currency.length < 3) {
    error.value = "Currency is required (3-letter ISO code).";
    return;
  }
  if (form.initial_deposit < 0) {
    error.value = "Initial deposit cannot be negative.";
    return;
  }
  emit("create", {
    type: form.type,
    currency: form.currency.trim().toUpperCase(),
    initial_deposit: Number(form.initial_deposit),
  });
}
</script>

<template>
  <section class="panel">
    <div class="row between">
      <h3>Bank account</h3>
      <span v-if="account" class="badge low">Opened</span>
      <span v-else-if="stage === 'account_creation'" class="badge in_review">Ready to open</span>
      <span v-else-if="stage === 'kyc'" class="badge pending">Locked — KYC pending</span>
      <span v-else class="badge low">Opened</span>
    </div>

    <div v-if="account" class="details">
      <div class="row">
        <div>
          <div class="muted">Account number</div>
          <div class="mono">{{ account.account_number }}</div>
        </div>
        <div>
          <div class="muted">Type</div>
          <div style="text-transform: capitalize">{{ account.type }}</div>
        </div>
        <div>
          <div class="muted">Currency</div>
          <div>{{ account.currency }}</div>
        </div>
        <div>
          <div class="muted">Initial deposit</div>
          <div>{{ account.initial_deposit.toLocaleString() }} {{ account.currency }}</div>
        </div>
      </div>
      <p class="muted" style="margin-top: 10px">
        Opened {{ new Date(account.opened_at).toLocaleString() }}
      </p>
    </div>

    <div v-else-if="stage === 'account_creation'" class="stack">
      <div class="grid cols-3">
        <div>
          <label>Account type</label>
          <select v-model="form.type">
            <option value="checking">Checking</option>
            <option value="savings">Savings</option>
            <option value="investment">Investment</option>
          </select>
        </div>
        <div>
          <label>Currency</label>
          <input v-model="form.currency" maxlength="3" style="text-transform: uppercase" />
        </div>
        <div>
          <label>Initial deposit</label>
          <input type="number" v-model.number="form.initial_deposit" min="0" step="50" />
        </div>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <div class="row">
        <button class="primary right" :disabled="busy" @click="submit">
          {{ busy ? "Opening…" : "Open account" }}
        </button>
      </div>
    </div>

    <p v-else class="muted">
      This step unlocks once KYC has been approved.
    </p>
  </section>
</template>

<style scoped>
h3 { margin: 0; font-size: 16px; }
.details .row { gap: 28px; flex-wrap: wrap; }
.details .row > div { min-width: 140px; }
.mono { font-family: ui-monospace, "SF Mono", Menlo, monospace; }
.error {
  margin: 4px 0 0;
  padding: 8px 12px;
  background: var(--danger-bg);
  color: var(--danger);
  border-radius: 6px;
  font-size: 13px;
}
</style>
