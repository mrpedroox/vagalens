"""Command-line interface. Commands are added as the roadmap advances."""

import typer
from dotenv import load_dotenv

from vagalens import __version__
from vagalens.config import load_config

app = typer.Typer(help="VagaLens: internship screening and cover letters with local RAG.")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"vagalens {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    load_dotenv()


@app.command()
def config() -> None:
    """Print the effective configuration."""
    typer.echo(load_config().model_dump_json(indent=2))


@app.command()
def index() -> None:
    """Index the personal knowledge base (planned for v0.1)."""
    typer.echo("Not implemented yet (planned for v0.1).")
    raise typer.Exit(code=1)


@app.command()
def screen(job: str = typer.Option(..., "--job", help="Path to a posting text file.")) -> None:
    """Screen a posting against the profile (planned for v0.1)."""
    typer.echo(f"Not implemented yet (planned for v0.1). Posting: {job}")
    raise typer.Exit(code=1)
