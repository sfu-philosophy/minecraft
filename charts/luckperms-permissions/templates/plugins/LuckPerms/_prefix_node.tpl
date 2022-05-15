{{- define "prefix_node" }}
-
  {{- if or .comment }}
  # {{ .comment }}
  {{- end }}
  type: prefix
  key:  {{ printf "prefix.%v.%s" (.priority | required "prefix priority") (.text | required "prefix text") | quote }}
  value: true
  {{- with .context }}
  context:
    {{- range $context_key, $context_value := . }}
      {{ $context_key | quote }}: {{ $context_value | quote }}
    {{- end }}
  {{- end }}
{{end -}}
