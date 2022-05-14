# minecraft
Configuration and documentation for the SFU Philosophy Minecraft server.


## How does this work?
Borrowing from my experiences of Kubernetes, I'm using [Helm](https://helm.sh/) to generate plugin configuration files from templates.

Servers are configured using the Helm charts (templates) inside the [charts](./charts) directory.
If a `[chart].yaml` file exists under `configs/servers/[server]`, it will use that as the template values for the corresponding chart under `charts/[chart]`.

### Rendering
Running `make render` or using [helmaroc](./helmaroc.py) will render the charts and save Bukkit plugin configuration under the `deploy` directory.

If a `.secrets` file exists, it will be used to provide secure secrets (like database passwords) to templates. Note that some templates may not be able to render properly unless run through the CI due to this.

### Deployments
Deploying is done through GitHub Actions.

By pushing to the `deploy` branch, the CI will render all the server templates and upload them to the appropriate servers over FTP.


## Architecture

The server is a pretty basic BungeeCord setup, using Waterfall for the proxy and Paper for the server instances.
