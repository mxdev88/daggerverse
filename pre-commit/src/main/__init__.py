"""Module for running pre-commit functions"""

import dagger
from dagger import dag, function, object_type

PRE_COMMIT_VERSION = "3.8.0"


@object_type
class PreCommit:
    @function
    def base(
        self,
        version: str = PRE_COMMIT_VERSION,
    ) -> dagger.Container:
        """Build base environment"""
        ctr = (
            dag.container()
            .from_("python:3.11-bookworm")
            .with_exec(["pip", "install", f"pre-commit=={version}"])
        )
        return ctr

    @function
    async def run(
        self,
        source: dagger.Directory,
        version: str = PRE_COMMIT_VERSION,
    ) -> str:
        PRE_COMMIT_CACHE = "/root/pre-commit"
        return await (
            self.base()
            .with_env_variable("PRE_COMMIT_HOME", PRE_COMMIT_CACHE)
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
