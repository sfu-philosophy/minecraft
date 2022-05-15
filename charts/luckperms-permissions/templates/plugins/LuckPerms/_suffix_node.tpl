{{- define "suffix_node" }}
-
  {{- if or .comment }}
  # {{ .comment }}
  {{- end }}
  type: suffix
  key:  {{ printf "suffix.%v.%s" (.priority | required "suffix priority") (.text | required "suffix text") | quote }}
  value: true
  {{- with .context }}
  context:
    {{- range $context_key, $context_value := . }}
      {{ $context_key | quote }}: {{ $context_value | quote }}
    {{- end }}
  {{- end }}
{{end -}}
