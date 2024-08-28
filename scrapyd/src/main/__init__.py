"""Module for running scrapyd"""

import dagger
from dagger import dag, function, object_type


@object_type
class Scrapyd:
    @function
    def base(
        self,
        source: dagger.Directory,
        url: str | None,
        username: str | None,
        password: dagger.Secret | None,
        ssh: dagger.Directory | None,
        ssh_sock: dagger.Socket | None,
    ) -> dagger.Container:
        """Build base environment"""
        ctr = (
            dag.container()
            .from_("python:3.11-bookworm")
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["pip", "install", "scrapyd-client"])
        )

        if ssh:
            ctr = (
                ctr.with_directory("/root/.ssh", ssh)
                .with_exec(["chmod", "700", "/root/.ssh"])
                .with_exec(["chmod", "600", "/root/.ssh/*"])
                .with_exec(["chmod", "644", "/root/.ssh/known_hosts"])
                .with_exec(["ssh-add", "/root/.ssh/*"])
            )
        if ssh_sock:
            ctr = ctr.with_unix_socket("/tmp/ssh.sock", ssh_sock).with_env_variable(
                "SSH_AUTH_SOCK", "/tmp/ssh.sock"
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
        ssh: dagger.Directory | None = None,
        ssh_sock: dagger.Socket | None = None,
    ) -> dagger.Container:
        args = []
        if include_dependencies:
            args.append("--include-dependencies")

        return await self.base(
            source, url=url, username=username, password=password, ssh=ssh, ssh_sock=ssh_sock
        ).with_exec(["scrapyd-deploy", *args])
