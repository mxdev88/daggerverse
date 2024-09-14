"""Module for running Poetry commands."""

import dagger
from dagger import dag, function, object_type


@object_type
class Poetry:
    @function
    def base(
        self,
        version: str | None = None,
    ) -> dagger.Container:
        """Build base environment"""
        pinned_version = ""
        if version:
            pinned_version = f"--version {version}"

        # curl -sSL https://install.python-poetry.org | python3 - --version 1.2.0
        ctr = (
            dag.container()
            .from_("python:3.11-bookworm")
            .with_exec(
                [
                    "sh",
                    "-c",
                    f"curl -sSL https://install.python-poetry.org | python3 - {pinned_version}",
                ]
            ).with_env_variable("PATH", "/root/.local/bin:$PATH", expand=True)
        )
        return ctr
