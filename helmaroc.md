# Helmaroc
Helmaroc (named after the bird in TLoZ:WW) is a tool that utilizes [Helm](https://helm.sh/) 3 to generate Minecraft server configuration files from templates. This idea was borrowed from the Kubernetes ecosystem.


## Helm?
Helm is a tool used in the Kubernetes ecosystem for configuring and deploying applications. It also happens to provide a really good framework for generating YAML files from templates, which works great for Bukkit's YAML-based ecosystem.

A package of related templates is contained within a "Chart". Charts are logically cohesive units that describe and provide configuration options for some service or application (in this case, plugins).

When rendering the templates in a Chart, "Values" are provided to fill in the blanks/user-configurable parts of the templates.

Helmaroc acts as a middle layer between the user (you) and Helm, providing a straightforward and declarative way to specify which templates are applicable to which servers, and what their unique values should be.

## Usage

Helmaroc looks at two directories:

- `charts`, which contains a list of available charts; and
- `configs/servers/[server]`, which contains the list of applicable charts for `[server]` and their Values.

For example, suppose I have the server `creative`:

If I wanted to render a `worldguard` chart for the `creative` server, I would create a file called `configs/servers/creative/worldguard.yml`. This instructs Helmaroc to render the `worldguard` chart located at `charts/worldguard`, using the values defined in `configs/servers/creative/worldguard.yml`. 



## Features

### Multiple-Values Support
Using YAML front-matter, multiple values files can be specified:

```yaml
---
~include:
  - /configs/shared/something.yml
---

other: content
```

The above snippet would include the values file `{repo_root}/configs/shared/something.yml`.

Values-file ordering is done as follows:

- `.secrets.yml` (generated by the CI)
- `~include` values files, in order.
- The remaining content in the `[chart].yml` file.

### "Wrapper" Templates

Sometimes you have non-YAML files for configuration. Helm doesn't support this out of the box, but Helmaroc does. By using the `.notyml` file extension instead of the real one, you can tell Helmaroc to extract the file contents as part of its rendering:

```yaml
~rename: something.md
~contents: |-
  ## Hello!
  I am not {{ .Values.name.yaml }}, but I'm still a template!
```

The above snippet would move the `~contents` text into a file called `something.md`.

#### Postprocessing

Wrapper templates support additional postprocessing, too. By adding the `~modify` directive, you can change the final result of the saved file:

```yaml
~rename: data.json.gz
~modify: [yaml2json, gzip]
~contents: |-
  this:
    will:
      be: |-
        json
```

Available postprocessing operations are:

- `yaml2json`: Parses the contents string as YAML, then encodes it into a JSON string.
- `gzip`: Gzips the contents string.

