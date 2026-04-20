<script setup lang="ts">
import { ref, watch } from "vue";
import { api } from "../api";
import type { AssignedRM, ManagerWithLoad, OnboardingStage } from "../types";

const props = defineProps<{
  assigned: AssignedRM | null;
  stage: OnboardingStage;
  busy?: boolean;
}>();
const emit = defineEmits<{
  (e: "assign", managerId: string | undefined): void;
}>();

const managers = ref<ManagerWithLoad[]>([]);
const picked = ref<string>("");

async function ensureLoaded() {
  if (managers.value.length === 0) {
    managers.value = await api.listRelationshipManagers();
  }
}

watch(
  () => props.stage,
  (s) => {
    if (s === "rm_assignment") void ensureLoaded();
  },
  { immediate: true },
);

function autoAssign() {
  emit("assign", undefined);
}

function manualAssign() {
  emit("assign", picked.value || undefined);
}
</script>

<template>
  <section class="panel">
    <div class="row between">
      <h3>Relationship manager</h3>
      <span v-if="assigned" class="badge low">Assigned</span>
      <span v-else-if="stage === 'rm_assignment'" class="badge in_review">Ready to assign</span>
      <span v-else-if="stage === 'kyc' || stage === 'account_creation'" class="badge pending">Locked</span>
      <span v-else class="badge low">Completed</span>
    </div>

    <div v-if="assigned" class="details">
      <div class="row">
        <div>
          <div class="muted">Manager</div>
          <div style="font-weight: 600">{{ assigned.manager.name }}</div>
          <div class="muted">{{ assigned.manager.email }}</div>
        </div>
        <div>
          <div class="muted">Specialization</div>
          <div style="text-transform: capitalize">{{ assigned.manager.specialization }}</div>
        </div>
        <div>
          <div class="muted">Languages</div>
          <div>{{ assigned.manager.languages.map((l) => l.toUpperCase()).join(", ") }}</div>
        </div>
      </div>
      <p class="muted" style="margin-top: 10px">
        Assigned {{ new Date(assigned.assigned_at).toLocaleString() }} · {{ assigned.reason }}
      </p>
    </div>

    <div v-else-if="stage === 'rm_assignment'" class="stack">
      <p class="muted" style="margin: 0">
        Auto-match uses the client's risk level, account type, and country-language preference.
      </p>
      <div class="row" style="gap: 8px">
        <button class="primary" :disabled="busy" @click="autoAssign">
          {{ busy ? "Assigning…" : "Auto-assign best match" }}
        </button>
      </div>
      <div style="margin-top: 12px">
        <label>Or pick manually</label>
        <div class="row" style="gap: 8px">
          <select v-model="picked" style="max-width: 420px">
            <option value="">— Select a manager —</option>
            <option v-for="m in managers" :key="m.manager.id" :value="m.manager.id">
              {{ m.manager.name }} · {{ m.manager.specialization }} · {{ m.manager.languages.map((l) => l.toUpperCase()).join("/") }} · {{ m.assigned_count }} clients
            </option>
          </select>
          <button :disabled="busy || !picked" @click="manualAssign">Assign</button>
        </div>
      </div>
    </div>

    <p v-else class="muted">
      This step unlocks once the bank account has been created.
    </p>
  </section>
</template>

<style scoped>
h3 { margin: 0; font-size: 16px; }
.details .row { gap: 28px; flex-wrap: wrap; }
.details .row > div { min-width: 160px; }
</style>
