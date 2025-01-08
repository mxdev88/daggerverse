"""Module for running pre-commit commands."""

import dataclasses

import dagger
from dagger import dag, function, object_type


@object_type
class PreCommit:
    ctr: dagger.Container = dataclasses.field(init=False)
    version: dataclasses.InitVar[str | None] = None

    def __post_init__(self, version: str | None = None):
        precommit_version = ""
        if version:
            precommit_version = f"=={version}"

        self.ctr = (
            dag.container()
            .from_("python:3.11-bookworm")
            .with_exec(["pip", "install", f"pre-commit{precommit_version}"])
        )

    @function
    async def run(
        self,
        source: dagger.Directory,
    ) -> str:
        PRE_COMMIT_CACHE = "/root/pre-commit"
        return await (
            self.ctr.with_env_variable("PRE_COMMIT_HOME", PRE_COMMIT_CACHE)
            .with_mounted_cache(
                PRE_COMMIT_CACHE,
                dag.cache_volume("pre-commit-cache"),
                sharing=dagger.CacheSharingMode.SHARED,
            )
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["pre-commit", "run", "--all-files"])
            .stdout()
        )
