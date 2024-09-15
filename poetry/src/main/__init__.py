"""Module for running Poetry commands."""

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
    def base(self) -> dagger.Container:
        return self.ctr
