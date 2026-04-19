<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "../api";
import type { Application, AuditEntry } from "../types";
import StatusBadge from "../components/StatusBadge.vue";
import RiskPanel from "../components/RiskPanel.vue";
import SanctionsPanel from "../components/SanctionsPanel.vue";
import LivenessPanel from "../components/LivenessPanel.vue";
import DocumentsPanel from "../components/DocumentsPanel.vue";

const props = defineProps<{ id: string }>();
const router = useRouter();

const application = ref<Application | null>(null);
const audit = ref<AuditEntry[]>([]);
const loading = ref(true);
const error = ref("");
const sanctionsBusy = ref(false);
const livenessBusy = ref(false);
const uploadBusy = ref(false);
const decisionBusy = ref(false);

const reviewer = ref("reviewer@kyc.io");
const note = ref("");

async function load() {
  loading.value = true;
  try {
    application.value = await api.getApplication(props.id);
    audit.value = await api.listAudit(props.id);
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    loading.value = false;
  }
}

async function rerunSanctions() {
  if (!application.value) return;
  sanctionsBusy.value = true;
  try {
    await api.rerunSanctions(application.value.id);
    await load();
  } finally {
    sanctionsBusy.value = false;
  }
}

async function runLiveness() {
  if (!application.value) return;
  livenessBusy.value = true;
  try {
    await api.runLiveness(application.value.id);
    await load();
  } finally {
    livenessBusy.value = false;
  }
}

async function uploadDocument(file: File) {
  if (!application.value) return;
  uploadBusy.value = true;
  try {
    await api.uploadDocument(application.value.id, file, application.value.applicant.id_document_type);
    await load();
  } finally {
    uploadBusy.value = false;
  }
}

async function decide(outcome: "approved" | "rejected") {
  if (!application.value) return;
  if (!note.value.trim()) {
    error.value = "Please add a reviewer note before deciding.";
    return;
  }
  decisionBusy.value = true;
  error.value = "";
  try {
    await api.decide(application.value.id, { outcome, reviewer: reviewer.value, note: note.value });
    note.value = "";
    await load();
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    decisionBusy.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div v-if="loading" class="muted">Loading…</div>
  <div v-else-if="error" class="panel" style="color: var(--danger)">{{ error }}</div>
  <div v-else-if="application" class="stack">
    <div class="row between">
      <div>
        <button @click="router.push('/dashboard')">&larr; Back to queue</button>
      </div>
      <div class="row" style="gap: 10px">
        <span class="muted">Ref {{ application.id.slice(0, 8) }}…</span>
        <StatusBadge :value="application.status" />
      </div>
    </div>

    <div class="panel">
      <div class="row between">
        <div>
          <h2 style="margin: 0">{{ application.applicant.first_name }} {{ application.applicant.last_name }}</h2>
          <div class="muted">{{ application.applicant.email }} · born {{ application.applicant.date_of_birth }}</div>
        </div>
        <div class="grid cols-3" style="gap: 24px; text-align: right">
          <div>
            <div class="muted">Nationality</div>
            <div>{{ application.applicant.nationality }}</div>
          </div>
          <div>
            <div class="muted">Country of residence</div>
            <div>{{ application.applicant.address.country }}</div>
          </div>
          <div>
            <div class="muted">ID document</div>
            <div>{{ application.applicant.id_document_type.replace("_", " ") }} · {{ application.applicant.id_document_number }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid cols-2">
      <RiskPanel :risk="application.risk" />
      <SanctionsPanel :sanctions="application.sanctions" :busy="sanctionsBusy" @rerun="rerunSanctions" />
      <LivenessPanel :liveness="application.liveness" :busy="livenessBusy" @run="runLiveness" />
      <DocumentsPanel
        :documents="application.documents"
        :expectedType="application.applicant.id_document_type"
        :busy="uploadBusy"
        @upload="uploadDocument"
      />
    </div>

    <section class="panel">
      <h3 style="margin: 0 0 12px">Decision</h3>
      <div v-if="application.decision" class="decided">
        <span class="badge" :class="application.status">{{ application.decision.outcome }}</span>
        <span class="muted">by {{ application.decision.reviewer }} on {{ new Date(application.decision.decided_at).toLocaleString() }}</span>
        <p style="margin: 8px 0 0">{{ application.decision.note }}</p>
      </div>
      <div v-else class="stack">
        <div class="grid cols-2">
          <div>
            <label>Reviewer</label>
            <input v-model="reviewer" />
          </div>
          <div>
            <label>Decision note</label>
            <input v-model="note" placeholder="Rationale visible in audit log" />
          </div>
        </div>
        <div class="row" style="gap: 8px">
          <button class="success" :disabled="decisionBusy" @click="decide('approved')">Approve</button>
          <button class="danger" :disabled="decisionBusy" @click="decide('rejected')">Reject</button>
        </div>
      </div>
    </section>

    <section class="panel">
      <h3 style="margin: 0 0 12px">Audit trail</h3>
      <table>
        <thead>
          <tr>
            <th>When</th>
            <th>Actor</th>
            <th>Action</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in audit" :key="e.id" style="cursor: default">
            <td class="muted">{{ new Date(e.at).toLocaleString() }}</td>
            <td>{{ e.actor }}</td>
            <td><code>{{ e.action }}</code></td>
            <td class="muted">{{ Object.keys(e.details).length ? JSON.stringify(e.details) : "—" }}</td>
          </tr>
          <tr v-if="audit.length === 0"><td colspan="4" class="muted">No audit entries.</td></tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
h2 { font-size: 22px; }
.decided p { font-size: 14px; }
code { background: #fafbfd; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
</style>
