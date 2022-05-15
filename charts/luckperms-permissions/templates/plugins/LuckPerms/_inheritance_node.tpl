{{- define "inheritance_node" }}
-
  {{- with .comment }}
  # {{ . }}
  {{- end }}
  type: inheritance
  key:  {{ printf "group.%s" (.group | required "parent group") | quote }}
  value: true
  {{- with .context }}
  context:
    {{- range $context_key, $context_value := . }}
      {{ $context_key | quote }}: {{ $context_value | quote }}
    {{- end }}
  {{- end }}
{{end -}}
