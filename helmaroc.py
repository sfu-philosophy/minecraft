#!/usr/bin/env python3
# ======================================================================================================================
# helmaroc: A Python script for managing Minecraft server configurations using Helm 3.
# Copyright (C) 2022 eth-p | MIT License
#
# Software:
#  - `helm` version 3
#
# Requirements:
#  - pip3 install `pyyaml`
# ======================================================================================================================
from os import path
import os
import sys
import subprocess
import yaml


class Chart:
    """
    An abstract representation of a Helm chart.
    """

    def __init__(self: 'Chart', chart: 'str', destination: 'str'):
        self.chart = chart
        self.chart_name = path.basename(chart)
        self.destination = destination

        self.values = []

        if not path.exists(path.join(chart, "Chart.yaml")):
            raise RuntimeError(f"Chart not found: {chart}")

        pass

    def append_values(self: 'Chart', values: 'ChartValues') -> 'Chart':
        """
        Appends additional ChartValues to this Chart.
        This can be used to change parameters for the rendered template.

        :param values: The values to add.
        :return: The Chart, for chaining.
        """
        self.values.append(values)
        return self

    def render(self):
        stdin = ''
        args = [
            'helm',
            'template', self.chart,
            '--atomic',  # Do not keep broken partial renders.
            '--output-dir', self.destination,
        ]

        # TODO(eth-p): Allow multiple STDIN inputs somehow.
        #              On *nix systems, STDIN can be opened multiple times by the subprocess.

        # Append the `--values` to the Helm arguments.
        for values_info in self.values:
            if values_info.file is not None:
                args.append('--values')
                args.append(values_info.file)

            if values_info.data is not None:
                if stdin == '':
                    args.append('--values')
                    args.append('-')
                    stdin = values_info.data
                else:
                    stdin += "\n---\n"
                    stdin += values_info.data

        # Run helm to render the template.
        result = subprocess.run(args, input=stdin, encoding='utf-8')
        if result.returncode != 0:
            raise RuntimeError('Failed to run Helm')

        # Un-Helmify the output path. This involves moving:
        #   - `[chartname]/templates/*` to `*`.
        #   - `[chartname]/charts/[subchart]/*` to `*`.
        subcharts_dir = path.join(self.destination, self.chart_name, 'charts')
        rename = [self.chart_name]
        if path.isdir(subcharts_dir):
            for subchart in os.listdir(subcharts_dir):
                subcharts.append(path.join(self.destination, self.chart_name, 'charts', subchart))

        for target in rename:
            move_dir(
                path.join(self.destination, target, 'templates'),
                self.destination,
            )

            os.rmdir(path.join(self.destination, target))


class ChartValues:
    """
    A values file (or literal block of text) being used to render a Helm template.
    """

    def __init__(self: 'ChartValues', data: 'str|None' = None, file: 'str|None' = None):
        if (data is None and file is None) or (data is not None and file is not None):
            raise RuntimeError("ChartValues requires either 'data' or 'file'")

        self.data = data
        self.file = file

    def __repr__(self):
        if self.data is not None:
            return "<ChartValues data:...>"
        if self.file is not None:
            return f"<ChartValues file:'{self.file}'>"
        return "<ChartValues broken>"

    def __str__(self):
        if self.data is not None:
            return "<data>"
        if self.file is not None:
            return self.file
        return "<broken>"


class Environment:
    """
    The environment for running helmaroc.
    """

    def __init__(self: 'Environment', dir: str):
        self.root = dir
        self.charts_dir = path.join(dir, "charts")
        self.configs_dir = path.join(dir, "configs", "servers")
        self.deploy_dir = path.join(dir, "deploy")
        self.secrets_file = path.join(".secrets.yml")
        self.logger = default_logger
        pass

    def __parse_values_references(self: 'Environment', file: 'str') -> 'Array[ChartValues]':
        values = []

        # Parse the frontmatter from the Chart values file.
        #   If it exists, all items under `~include` will be added as in-order values files.
        #   Any remaining data will be added at the end via STDIN.
        frontmatter, data = split_frontmatter(file)
        if frontmatter is not None:
            frontmatter_yaml = yaml.safe_load(frontmatter)
            if '~include' in frontmatter_yaml:
                for values_file in frontmatter_yaml['~include']:
                    if values_file[0:1] == '/':
                        values_file = self.root + values_file

                    values.append(ChartValues(file=values_file))

        if data.strip() != "":
            values.append(ChartValues(data=data))

        return values

    def run_target(self, target: 'str'):
        """
        Runs a specific target.

        A target is considered to be a `foo.yml` file, where `foo` corresponds to the chart name under the `charts`
        directory. The `foo.yml` file defines the values that will be provided to Helm during chart rendering.

        :param target: The target path, excluding the `.yml` extension.
        """
        self.logger("render", target)

        chart_template = path.join(self.charts_dir, path.basename(target))
        chart_values = target + ".yml"
        chart_dest = path.join(self.deploy_dir, path.basename(path.dirname(target)))

        # Create the Chart object.
        chart = Chart(chart_template, chart_dest)

        # If the `.secrets.yml` file exists, add it as a value.
        if path.exists(self.secrets_file):
            self.logger("values", self.secrets_file)
            chart.append_values(ChartValues(file=self.secrets_file))

        # Parse the values YAML, looking for include references in the front-matter.
        values = self.__parse_values_references(chart_values)
        for values_info in values:
            self.logger("values", str(values_info))
            chart.append_values(values_info)

        # Render the chart.
        chart.render()

    def run_all(self, dir: str):
        """
        Runs all the targets within a directory.
        Note: This will NOT recurse subdirectories.

        :param dir: The directory.
        """
        for config in os.listdir(dir):
            config_name, config_ext = os.path.splitext(config)
            if config_ext != '.yml':
                continue

            self.run_target(path.join(dir, config_name))


def split_frontmatter(file: 'str') -> ('str|None', 'str'):
    """
    Reads and splits a file into YAML frontmatter and actual contents.

    :param file: The file.
    :return: A tuple containing the frontmatter and the contents.
    """
    frontmatter = ''
    contents = ''

    in_frontmatter = False
    with open(file, 'r') as handle:
        while True:
            line = handle.readline()
            if line is None:
                break

            # If in frontmatter, collect each line until reading the last `---`.
            if in_frontmatter is True:
                if line.rstrip() == "---":
                    break

                frontmatter += line
                continue

            # If not in frontmatter, enter frontmatter if a `---` is found, or exit otherwise.
            if line.rstrip() == "---":
                in_frontmatter = True
            else:
                handle.seek(0)
                break

        # Collect the remaining data as the contents.
        contents = handle.read()

    if frontmatter == '':
        frontmatter = None

    return frontmatter, contents


def move_dir(source: 'str', dest: 'str'):
    """
    Recursively moves the contents of one directory to another.
    This will replace any existing files in the destination.

    :param source: The source dir.
    :param dest: The destination dir.
    """
    for entry in os.listdir(source):
        source_path = path.join(source, entry)
        dest_path = path.join(dest, entry)

        # Recursively merge directories.
        if path.isdir(source_path):
            if not path.isdir(dest_path):
                os.mkdir(dest_path)

            move_dir(path.join(source, entry), path.join(dest, entry))
            continue

        # Remove existing files.
        if path.exists(dest_path):
            os.remove(dest_path)

        # Move files.
        os.rename(source_path, dest_path)

    # Remove the directory.
    os.rmdir(source)


# ======================================================================================================================
# Logging:
# ======================================================================================================================

def default_logger(kind: str, message: str):
    """
    A simple logging function that prints info to STDOUT.

    :param kind: The message kind.
    :param message: The message.
    """
    if kind == 'render':
        print(f"\x1B[34mRender: \x1B[0m{message}")
    elif kind == 'values':
        print(f"  Values: {message}")
    else:
        print(f"{kind} {message}")


# ======================================================================================================================
# Main:
# ======================================================================================================================

if __name__ == "__main__":
    try:
        instance = Environment(".")

        # If no specific server(s) will be rendered, render all servers.
        if len(sys.argv) == 1:
            for server in os.listdir(instance.configs_dir):
                instance.run_all(path.join(instance.configs_dir, server))
            exit(0)

        # Render the requested charts.
        for arg in sys.argv[1:]:
            instance.run_target(arg)

    except SystemExit:
        raise

    except:
        raise
