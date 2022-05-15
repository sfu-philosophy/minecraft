{{- define "display_name_node" }}
-
  {{- with .comment }}
  # {{ . }}
  {{- end }}
  type: display_name
  key:  {{ printf "display_name.%s" (.text | required "display name") | quote }}
  value: true
  {{- with .context }}
  context:
    {{- range $context_key, $context_value := . }}
      {{ $context_key | quote }}: {{ $context_value | quote }}
    {{- end }}
  {{- end }}
{{end -}}
