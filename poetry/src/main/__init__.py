"""Module for running Poetry commands."""

from typing_extensions import Self
import dataclasses
import dagger
from dagger import dag, function, object_type


@object_type
class Poetry:
    ctr: dagger.Container = dataclasses.field(init=False)
    version: dataclasses.InitVar[str | None] = None

    def __post_init__(self, version: str | None = None):
        poetry_version = ""
        if version:
            poetry_version = f"--version {version}"

        # curl -sSL https://install.python-poetry.org | python3 - --version 1.2.0
        self.ctr = (
            dag.container()
            .from_("python:3.11-bookworm")
            .with_exec(
                [
                    "sh",
                    "-c",
                    f"curl -sSL https://install.python-poetry.org | python3 - {poetry_version}",
                ]
            )
            .with_env_variable("PATH", "/root/.local/bin:$PATH", expand=True)
        )

    @function
    def container(self) -> dagger.Container:
        return self.ctr

    @function
    async def with_config(self, key: str, value: str) -> Self:
        self.ctr = await self.ctr.with_exec(
            [
                "sh",
                "-c",
                f"poetry config {key} {value}",
            ]
        )
        return self

    @function
    async def with_build(self, source: dagger.Directory) -> Self:
        self.ctr = await (
            self.ctr.with_directory("/src", source, exclude=[".venv"])
            .with_workdir("/src")
            .with_exec(
                [
                    "poetry",
                    "build",
                ]
            )
        )
        return self

    @function
    async def with_publish(self, repository: str| None = None) -> Self:
        args = []
        if repository:
            args.extend(["--repository", f"{repository}"])
        self.ctr = await (
            self.ctr.with_exec(
                [
                    "poetry",
                    "publish",
                    *args
                ]
            )
        )
        return self
