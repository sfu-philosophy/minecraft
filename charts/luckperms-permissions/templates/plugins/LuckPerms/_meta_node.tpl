{{- define "meta_node" }}
-
  {{- with .comment }}
  # {{ . }}
  {{- end }}
  type: permission
  key:  {{ printf "meta.%v.%s" (.name | required "meta priority") (.text | required "meta text") | quote }}
  value: true
  {{- with .context }}
  context:
    {{- range $context_key, $context_value := . }}
      {{ $context_key | quote }}: {{ $context_value | quote }}
    {{- end }}
  {{- end }}
{{end -}}
