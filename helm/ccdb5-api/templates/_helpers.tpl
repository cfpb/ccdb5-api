{{/*
Expand the name of the chart.
*/}}
{{- define "ccdb5-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ccdb5-api.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ccdb5-api.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ccdb5-api.labels" -}}
helm.sh/chart: {{ include "ccdb5-api.chart" . }}
{{ include "ccdb5-api.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ccdb5-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ccdb5-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "ccdb5-api.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ccdb5-api.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}


{{/*
Postgres Environment Vars
*/}}
{{- define "ccdb5-api.postgresEnv" -}}
{{- if .Values.postgresql.enabled -}}
- name: PGUSER
  value: "{{ include "postgresql.username" .Subcharts.postgresql | default "postgres"  }}"
- name: PGPASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "postgresql.secretName" .Subcharts.postgresql }}
      key: {{ include "postgresql.userPasswordKey" .Subcharts.postgresql }}
- name: PGHOST
  value: "{{ include "postgresql.primary.fullname" .Subcharts.postgresql | trunc 63 | trimSuffix "-" }}"
- name: PGDATABASE
  value: "{{ include "postgresql.database" .Subcharts.postgresql | default "postgres" }}"
- name: PGPORT
  value: "{{ include "postgresql.service.port" .Subcharts.postgresql }}"
{{- else }}
{{- if .Values.postgresql.auth.createSecret -}}
- name: PGUSER
  valueFrom:
    secretKeyRef:
      name: {{ include "ccdb5-api.fullname" . }}-postgres
      key: username
- name: PGPASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "ccdb5-api.fullname" . }}-postgres
      key: password
- name: PGDATABASE
  valueFrom:
    secretKeyRef:
      name: {{ include "ccdb5-api.fullname" . }}-postgres
      key: database
{{- else }}
- name: PGUSER
  value: "{{ .Values.postgresql.auth.username | default "postgres" }}"
- name: PGPASSWORD
  value: {{ .Values.postgresql.auth.password | quote }}
- name: PGDATABASE
  value: "{{ .Values.postgresql.auth.database | default "postgres" }}"
{{- end }}
- name: PGHOST
  value: {{ .Values.postgresql.external.host | quote }}
- name: PGPORT
  value: "{{ .Values.postgresql.external.port | default "5432" }}"
{{- end }}
{{- end }}

{{/*
Opensearch Environment Vars
*/}}
{{- define "ccdb5-api.opensearchEnv" -}}
- name: ES_SCHEME
  value: "{{ default "https" .Values.opensearch.protocol }}"
- name: ES_HOST
{{- if .Values.opensearch.enabled }}
  value: "{{ include "opensearch.serviceName" .Subcharts.opensearch }}"
{{- else }}
  value: {{ .Values.opensearch.hostname | quote }}
{{- end }}
- name: ES_PORT
  value: {{ .Values.opensearch.httpPort | quote }}
{{- end }}


{{/*
Main container Environment Vars
*/}}
{{- define "ccdb5-api.env" -}}
{{ include "ccdb5-api.postgresEnv" . }}
{{ include "ccdb5-api.opensearchEnv" . }}
{{- end }}
