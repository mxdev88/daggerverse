"""Module for running python-semantic-release (PSR) commands."""

import dagger
from dagger import dag, function, object_type


@object_type
class Psr:
    @function
    def base(
        self,
        version: str | None = None,
    ) -> dagger.Container:
        """Build base environment"""
        pinned_version = ""
        if version:
            pinned_version = f"=={version}"
        ctr = (
            dag.container()
            .from_("python:3.11-bookworm")
            .with_exec(
                [
                    "pip",
                    "install",
                    f"python-semantic-release{pinned_version}",
                ]
            )
        )
        return ctr

    @function
    async def version(
        self,
        source: dagger.Directory,
        commit: bool = True,
        tag: bool = True,
        version: str | None = None,
    ) -> dagger.Container:
        args = []

        if commit:
            args.append("--commit")
        else:
            args.append("--no-commit")

        if tag:
            args.append("--tag")
        else:
            args.append("--no-tag")

        return (
            await self.base(version=version)
            .with_directory("/src", source, exclude=[".venv"])
            .with_workdir("/src")
            .with_exec(["semantic-release", "version", *args])
        )
