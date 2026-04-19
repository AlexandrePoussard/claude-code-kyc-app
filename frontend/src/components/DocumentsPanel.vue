<script setup lang="ts">
import type { Document as KycDocument, IdDocumentType } from "../types";

defineProps<{ documents: KycDocument[]; expectedType: IdDocumentType; busy?: boolean }>();
const emit = defineEmits<{ (e: "upload", file: File): void }>();

function onFile(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) emit("upload", target.files[0]);
  target.value = "";
}
</script>

<template>
  <section class="panel">
    <div class="row between">
      <h3>Identity documents</h3>
      <label class="upload-btn">
        <input type="file" accept="image/*,.pdf" @change="onFile" :disabled="busy" />
        {{ busy ? "Uploading…" : "Upload document" }}
      </label>
    </div>
    <p class="muted">Expected: {{ expectedType.replace("_", " ") }}</p>
    <ul v-if="documents.length > 0" class="docs">
      <li v-for="doc in documents" :key="doc.id">
        <div class="row between">
          <div>
            <div class="doc-name">{{ doc.filename }}</div>
            <div class="muted">
              {{ (doc.size_bytes / 1024).toFixed(1) }} KB · uploaded {{ new Date(doc.uploaded_at).toLocaleString() }}
            </div>
          </div>
          <span class="badge pending">{{ doc.type.replace("_", " ") }}</span>
        </div>
        <div v-if="Object.keys(doc.ocr_extracted).length > 0" class="ocr">
          <strong>Extracted (OCR):</strong>
          <ul>
            <li v-for="(v, k) in doc.ocr_extracted" :key="k">
              <span class="muted">{{ k }}:</span> {{ v }}
            </li>
          </ul>
        </div>
      </li>
    </ul>
    <div v-else class="muted">No documents uploaded.</div>
  </section>
</template>

<style scoped>
h3 { margin: 0; font-size: 16px; }
.upload-btn {
  display: inline-block;
  background: var(--primary);
  color: white;
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 0;
}
.upload-btn input { display: none; }
.docs { list-style: none; padding: 0; margin: 12px 0 0; }
.docs > li {
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  margin-bottom: 10px;
}
.doc-name { font-weight: 500; }
.ocr { margin-top: 10px; font-size: 13px; background: #fafbfd; padding: 10px; border-radius: 4px; }
.ocr ul { margin: 6px 0 0; padding-left: 18px; }
</style>
