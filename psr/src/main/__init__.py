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
        push: bool = True,
        vcs_release: bool = False,
        changelog: bool = True,
        build_metadata: str | None = None,
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

        if push:
            args.append("--push")
        else:
            args.append("--no-push")

        if changelog:
            args.append("--changelog")
        else:
            args.append("--no-changelog")

        if vcs_release:
            args.append("--vcs-release")
        else:
            args.append("--no-vcs-release")

        if build_metadata:
            args.extend(["--build-metadata", f"{build_metadata}"])

        return (
            await self.base(version=version)
            .with_directory("/src", source, exclude=[".venv"])
            .with_workdir("/src")
            .with_exec(["semantic-release", "version", *args])
        )
