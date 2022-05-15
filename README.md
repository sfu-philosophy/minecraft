# minecraft
[![Deploy](https://github.com/sfu-philosophy/minecraft/actions/workflows/deploy.yaml/badge.svg?branch=deploy&event=push)](https://github.com/sfu-philosophy/minecraft/actions/workflows/deploy.yaml)

Configuration and documentation for the SFU Philosophy Minecraft server.

## Contributing

We use a declarative model for defining and configuring our Minecraft server, utilizing templates to create consistent but flexible configuration files for both the server and its plugins.

To understand how this works, we encourage you to read through the [helmaroc documentation](./helmaroc.md).


### Requirements

In order to render templates locally, you will need the following software:

- GNU Make
- Helm 3
- Python 3
  - `pyyaml`
  - `yamllint`

<details><summary><b>MacOS</b></summary>

```bash
brew install make helm python yamllint
pip3 install pyyaml
```

</details>

<details><summary><b>Arch Linux</b></summary>

```bash
sudo pacman -Sy make helm python3 python-pip yamllint
pip3 install pyyaml
```

</details>

<details><summary><b>Ubuntu Linux</b></summary>

```bash
sudo apt-get install make python3 python3-pip yamllint
pip3 install pyyaml
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

</details>

<details><summary><b>Windows</b></summary>

[Please read this guide, and then follow the Ubuntu instructions from above.](https://docs.microsoft.com/en-us/windows/wsl/install)

</details>

### Building
Running `make render` will render the charts and save configurations files under the `deploy/[server]` directories.

If a `.secrets` file exists, it will be used to provide secure secrets (like database passwords) to templates. Note that some templates may not be able to render properly unless run through the CI due to this.

### Deployments
Deployments are done through GitHub Actions.

By pushing to the `deploy` branch, the CI will render all the server templates and upload them to the appropriate servers over FTP. You can see the results of a deployment [here](https://github.com/sfu-philosophy/minecraft/actions/workflows/deploy.yaml).

After deploying successfully, the servers will need to be restarted manually.


#### Permissions
Permissions must be imported manually through `/lpb import permissions.json.gz --replace`.


## Architecture

The server is a pretty basic BungeeCord setup, using Waterfall for the proxy and Paper for the server instances.
