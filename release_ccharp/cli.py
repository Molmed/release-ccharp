import click
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.snpseq_paths import SnpseqPathProperties
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.config import Config
from release_ccharp.apps.common.base import ApplicationFactory
from release_ccharp.utility.os_service import OsService


@click.group()
@click.option('--whatif/--not-whatif', default=False)
@click.pass_context
def cli(ctx, whatif):
    ctx.obj['whatif'] = whatif


@cli.command("create-cand")
@click.argument("repo")
@click.option("--major", is_flag=True, default=False)
@click.pass_context
def create_cand(ctx, repo, major):
    workflow = SnpseqWorkflow(whatif=ctx.obj['whatif'], repo=repo)
    workflow.create_cand(major_inc=major)


@cli.command("create-hotfix")
@click.argument("repo")
@click.pass_context
def create_hotfix(ctx, repo):
    workflow = SnpseqWorkflow(whatif=ctx.obj['whatif'], repo=repo)
    workflow.create_hotfix()


@cli.command("download")
@click.argument("repo")
@click.pass_context
def download(ctx, repo):
    workflow = SnpseqWorkflow(whatif=ctx.obj['whatif'], repo=repo)
    workflow.download()


@cli.command("build")
@click.argument("repo")
@click.pass_context
def build(ctx, repo):
    factory = ApplicationFactory()
    instance = factory.get_instance(whatif=ctx.obj['whatif'], repo=repo)
    instance.build()


@cli.command("deploy-validation")
@click.argument("repo")
@click.pass_context
def deploy_validation(ctx, repo):
    factory = ApplicationFactory()
    instance = factory.get_instance(whatif=ctx.obj['whatif'], repo=repo)
    instance.deploy_validation()


@cli.command("accept")
@click.argument("repo")
@click.pass_context
def accept(ctx, repo):
    workflow = SnpseqWorkflow(whatif=ctx.obj['whatif'], repo=repo)
    workflow.accept()


@cli.command("deploy")
@click.argument("repo")
@click.pass_context
def deploy(ctx, repo):
    factory = ApplicationFactory()
    instance = factory.get_instance(whatif=ctx.obj['whatif'], repo=repo)
    instance.deploy()


@cli.command("download-release-history")
@click.argument("repo")
@click.pass_context
def download_release_history(ctx, repo):
    workflow = SnpseqWorkflow(whatif=ctx.obj['whatif'], repo=repo)
    workflow.download_release_history()


@cli.command("generate-user-manual")
@click.argument("repo")
@click.option("--copy-latest", is_flag=True, default=False)
@click.pass_context
def generate_user_manual(ctx, repo, copy_latest):
    workflow = SnpseqWorkflow(whatif=ctx.obj['whatif'], repo=repo)
    if copy_latest:
        print("Copy user manual from latest accepted directory")
        workflow.copy_previous_user_manual()
    else:
        print("Generate user manual from confluence workspace")
        workflow.generate_user_manual()


@cli.command("generate-folder-tree")
@click.argument("repo")
@click.pass_context
def generate_folder_tree(ctx, repo):
    c = Config()
    config = c.open_config(repo)
    path_properites = SnpseqPathProperties(config, repo)
    path_actions = SnpseqPathActions(whatif=ctx.obj['whatif'],
                                     path_properties=path_properites,
                                     os_service=OsService())
    path_actions.generate_folder_tree()

def cli_main():
    cli(obj={})

if __name__ == "__main__":
    cli_main()

