"""Module for running python-semantic-release (PSR) commands."""

import dataclasses
import dagger
from dagger import dag, function, object_type


@object_type
class Psr:
    ctr: dagger.Container = dataclasses.field(init=False)

    def __post_init__(self, version: str | None = None):
        psr_version_args = ""
        if version:
            psr_version_args = f"--version {version}"

        self.ctr = (
            dag.container()
            .from_("python:3.11-bookworm")
            .with_exec(
                [
                    "pip",
                    "install",
                    f"python-semantic-release{psr_version_args}",
                ]
            )
        )

    @function
    def container(self) -> dagger.Container:
        return self.ctr

    @function
    async def version(
        self,
        source: dagger.Directory,
        commit: bool = True,
        tag: bool = True,
        push: bool = True,
        vcs_release: bool = False,
        changelog: bool = True,
        build_metadata: str | None = None,
        noop: bool = False,
        strict: bool = False,
        config: str | None = None,
    ) -> dagger.Container:
        global_args = []
        cmd_args = []

        if noop:
            global_args.append("--noop")

        if strict:
            global_args.append("--strict")

        if config:
            global_args.extend(["--config", f"{config}"])

        if commit:
            cmd_args.append("--commit")
        else:
            cmd_args.append("--no-commit")

        if tag:
            cmd_args.append("--tag")
        else:
            cmd_args.append("--no-tag")

        if push:
            cmd_args.append("--push")
        else:
            cmd_args.append("--no-push")

        if changelog:
            cmd_args.append("--changelog")
        else:
            cmd_args.append("--no-changelog")

        if vcs_release:
            cmd_args.append("--vcs-release")
        else:
            cmd_args.append("--no-vcs-release")

        if build_metadata:
            cmd_args.extend(["--build-metadata", f"{build_metadata}"])

        return (
            await self.ctr.with_directory("/src", source, exclude=[".venv"])
            .with_workdir("/src")
            .with_exec(["semantic-release", *global_args, "version", *cmd_args])
        )
