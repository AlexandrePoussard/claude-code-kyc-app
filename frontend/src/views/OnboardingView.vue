<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "../api";
import type { ApplicantInput, Application, IdDocumentType } from "../types";

const router = useRouter();
const step = ref<1 | 2 | 3 | 4>(1);
const submitting = ref(false);
const error = ref("");
const createdApp = ref<Application | null>(null);

const form = reactive<ApplicantInput>({
  first_name: "",
  last_name: "",
  email: "",
  date_of_birth: "",
  nationality: "FR",
  address: { line1: "", line2: "", city: "", postal_code: "", country: "FR" },
  id_document_type: "passport" as IdDocumentType,
  id_document_number: "",
  politically_exposed: false,
});

const docFile = ref<File | null>(null);

function nextStep() {
  error.value = "";
  if (step.value === 1) {
    if (!form.first_name || !form.last_name || !form.email || !form.date_of_birth) {
      error.value = "Please fill all required fields.";
      return;
    }
  }
  if (step.value === 2) {
    if (!form.address.line1 || !form.address.city || !form.address.postal_code) {
      error.value = "Address is incomplete.";
      return;
    }
  }
  step.value = (step.value + 1) as 1 | 2 | 3 | 4;
}

function prevStep() {
  if (step.value > 1) step.value = (step.value - 1) as 1 | 2 | 3 | 4;
}

async function submit() {
  submitting.value = true;
  error.value = "";
  try {
    const app = await api.createApplication(form);
    createdApp.value = app;
    if (docFile.value) {
      await api.uploadDocument(app.id, docFile.value, form.id_document_type);
    }
    await api.runLiveness(app.id);
    createdApp.value = await api.getApplication(app.id);
    step.value = 4;
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    submitting.value = false;
  }
}

function onFile(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) docFile.value = target.files[0];
}
</script>

<template>
  <div class="onboarding">
    <div class="progress">
      <div v-for="n in 4" :key="n" class="step" :class="{ active: step >= n, current: step === n }">
        <span>{{ n }}</span>
        <label>{{ ["Identity", "Address", "Document", "Submitted"][n - 1] }}</label>
      </div>
    </div>

    <div class="panel">
      <section v-if="step === 1" class="stack">
        <h2>Who are you?</h2>
        <div class="grid cols-2">
          <div>
            <label>First name *</label>
            <input v-model="form.first_name" />
          </div>
          <div>
            <label>Last name *</label>
            <input v-model="form.last_name" />
          </div>
          <div>
            <label>Email *</label>
            <input v-model="form.email" type="email" />
          </div>
          <div>
            <label>Date of birth *</label>
            <input v-model="form.date_of_birth" type="date" />
          </div>
          <div>
            <label>Nationality (ISO-2) *</label>
            <input v-model="form.nationality" maxlength="2" style="text-transform: uppercase" />
          </div>
          <div style="display: flex; align-items: center; gap: 8px; padding-top: 26px">
            <input type="checkbox" v-model="form.politically_exposed" id="pep" style="width: auto" />
            <label for="pep" style="margin: 0">I am a politically exposed person</label>
          </div>
        </div>
      </section>

      <section v-if="step === 2" class="stack">
        <h2>Where do you live?</h2>
        <div class="grid cols-2">
          <div style="grid-column: span 2">
            <label>Address line 1 *</label>
            <input v-model="form.address.line1" />
          </div>
          <div style="grid-column: span 2">
            <label>Address line 2</label>
            <input v-model="form.address.line2" />
          </div>
          <div>
            <label>City *</label>
            <input v-model="form.address.city" />
          </div>
          <div>
            <label>Postal code *</label>
            <input v-model="form.address.postal_code" />
          </div>
          <div>
            <label>Country (ISO-2) *</label>
            <input v-model="form.address.country" maxlength="2" style="text-transform: uppercase" />
          </div>
        </div>
      </section>

      <section v-if="step === 3" class="stack">
        <h2>Identity document</h2>
        <div class="grid cols-2">
          <div>
            <label>Document type</label>
            <select v-model="form.id_document_type">
              <option value="passport">Passport</option>
              <option value="national_id">National ID card</option>
              <option value="driver_license">Driver license</option>
            </select>
          </div>
          <div>
            <label>Document number *</label>
            <input v-model="form.id_document_number" />
          </div>
          <div style="grid-column: span 2">
            <label>Upload a scan (optional in workshop mode)</label>
            <input type="file" accept="image/*,.pdf" @change="onFile" />
            <p v-if="docFile" class="muted">{{ docFile.name }} · {{ (docFile.size / 1024).toFixed(1) }} KB</p>
          </div>
        </div>
        <p class="muted">A fake liveness check will also run once you submit.</p>
      </section>

      <section v-if="step === 4 && createdApp" class="stack">
        <h2>Application submitted</h2>
        <p>Thanks {{ createdApp.applicant.first_name }} — your file is now <strong>{{ createdApp.status.replace("_", " ") }}</strong>.</p>
        <div class="grid cols-2">
          <div class="panel" style="background: #fafbfd">
            <div class="muted">Risk level</div>
            <div style="margin-top: 6px">
              <span v-if="createdApp.risk" class="badge" :class="createdApp.risk.level">
                {{ createdApp.risk.level }} · {{ createdApp.risk.score }}
              </span>
            </div>
          </div>
          <div class="panel" style="background: #fafbfd">
            <div class="muted">Sanctions</div>
            <div style="margin-top: 6px">
              <span v-if="createdApp.sanctions?.clear" class="badge low">clear</span>
              <span v-else-if="createdApp.sanctions" class="badge high">{{ createdApp.sanctions.hits.length }} hit(s)</span>
            </div>
          </div>
          <div class="panel" style="background: #fafbfd">
            <div class="muted">Liveness</div>
            <div style="margin-top: 6px">
              <span v-if="createdApp.liveness?.passed" class="badge low">passed</span>
              <span v-else-if="createdApp.liveness" class="badge high">failed</span>
            </div>
          </div>
          <div class="panel" style="background: #fafbfd">
            <div class="muted">Reference</div>
            <div class="mono" style="margin-top: 6px; font-size: 13px">{{ createdApp.id }}</div>
          </div>
        </div>
        <div class="row" style="gap: 8px; margin-top: 12px">
          <button class="primary" @click="router.push(`/applications/${createdApp.id}`)">Open review</button>
          <button @click="router.push('/dashboard')">Back to dashboard</button>
        </div>
      </section>

      <p v-if="error" class="error">{{ error }}</p>

      <div v-if="step < 4" class="row" style="margin-top: 20px; gap: 8px">
        <button v-if="step > 1" @click="prevStep">Back</button>
        <button v-if="step < 3" class="primary right" @click="nextStep">Continue</button>
        <button v-else class="primary right" :disabled="submitting" @click="submit">
          {{ submitting ? "Submitting…" : "Submit application" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.onboarding { max-width: 780px; margin: 0 auto; }
.progress {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 8px;
}
.step {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 6px;
  background: white;
  border: 1px solid var(--border);
  font-size: 13px;
  color: var(--muted);
}
.step span {
  display: inline-flex;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--border);
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 12px;
}
.step label { margin: 0; font-weight: 500; }
.step.active { color: var(--text); }
.step.active span { background: var(--primary); color: white; }
.step.current { border-color: var(--primary); }
h2 { margin: 0 0 8px; font-size: 20px; }
.error {
  margin: 16px 0 0;
  padding: 10px 14px;
  background: var(--danger-bg);
  color: var(--danger);
  border-radius: 6px;
  font-size: 14px;
}
.mono { font-family: ui-monospace, "SF Mono", Menlo, monospace; }
</style>
