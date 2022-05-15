{{- define "permission_node" }}
-
  {{- with .plugin }}
  # <Plugin: {{ . }}>
  {{- end }}
  {{- with .comment }}
  # {{ . }}
  {{- end }}
  type: permission
  key:  {{ .name | required "Permission node key" | quote }}
  value: {{ .value | required "Permission node value" }}
  {{- with .context }}
  context:
    {{- range $context_key, $context_value := . }}
      {{ $context_key | quote }}: {{ $context_value | quote }}
    {{- end }}
  {{- end }}
{{end -}}
