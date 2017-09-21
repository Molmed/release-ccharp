import click
from release_ccharp.snpseq_workflow import SnpseqWorkflow


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


@cli.command("accept")
@click.argument("repo")
@click.pass_context
def accept(ctx, repo):
    workflow = SnpseqWorkflow(whatif=ctx.obj['whatif'], repo=repo)
    workflow.accept()


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


def cli_main():
    cli(obj={})

if __name__ == "__main__":
    cli_main()

