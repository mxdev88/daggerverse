"""Module for running scrapyd-client commands."""

import dagger
from dagger import dag, function, object_type


@object_type
class ScrapydClient:
    @function
    def base(
        self,
        url: str | None,
        username: str | None,
        password: dagger.Secret | None,
        ssh_sock: dagger.Socket | None,
    ) -> dagger.Container:
        """Build base environment"""
        ctr = (
            dag.container()
            .from_("python:3.11-bookworm")
            .with_exec(["pip", "install", "scrapyd-client"])
        )
        if ssh_sock:
            ctr = (
                ctr.with_unix_socket("/tmp/ssh.sock", ssh_sock)
                .with_env_variable("SSH_AUTH_SOCK", "/tmp/ssh.sock")
                .with_env_variable("GIT_SSH_COMMAND", "ssh -o StrictHostKeyChecking=no")
            )
        if url:
            ctr = ctr.with_env_variable("SCRAPYD_URL", url)
        if username:
            ctr = ctr.with_env_variable("SCRAPYD_USERNAME", username)
        if password:
            ctr = ctr.with_secret_variable("SCRAPYD_PASSWORD", password)
        return ctr

    @function
    async def deploy(
        self,
        source: dagger.Directory,
        include_dependencies: bool = True,
        url: str | None = None,
        username: str | None = None,
        password: dagger.Secret | None = None,
        ssh_sock: dagger.Socket | None = None,
    ) -> dagger.Container:
        args = []
        if include_dependencies:
            args.append("--include-dependencies")

        return (
            await self.base(
                url=url,
                username=username,
                password=password,
                ssh_sock=ssh_sock,
            )
            .with_directory("/src", source, exclude=[".venv"])
            .with_workdir("/src")
            .with_exec(["scrapyd-deploy", *args])
        )
