#!/usr/bin/env python
import os
import shutil
import subprocess
from pathlib import Path

PROJECT_DIRECTORY = Path(os.path.abspath(os.path.curdir)).resolve()

UNUSED_DOCS_DIRS = [
    PROJECT_DIRECTORY / 'docs-mkdocs',
    PROJECT_DIRECTORY / 'docs-sphinx',
    PROJECT_DIRECTORY / 'docs-jupyter-book'
]

DOCUMENTATION_ENGINE = "{{ cookiecutter.documentation_engine }}"
DOCS_SPEC_DIR = UNUSED_DOCS_DIRS.pop(
    UNUSED_DOCS_DIRS.index(
        PROJECT_DIRECTORY / f'docs-{DOCUMENTATION_ENGINE}'
    )
)

USE_SRC_LAYOUT = {{ cookiecutter.project_layout == "src" }}
if USE_SRC_LAYOUT:
    PACKAGE_PATH = PROJECT_DIRECTORY / "src" / "{{ cookiecutter.package_slug}}"
else:
    PACKAGE_PATH = PROJECT_DIRECTORY / "{{ cookiecutter.package_slug}}"

USE_BLACK = {{ cookiecutter.use_black == "yes" }}
USE_BLUE = {{ cookiecutter.use_blue == "yes" }}
USE_BANDIT = {{ cookiecutter.use_bandit == "yes" }}
USE_CONTAINERS = {{ cookiecutter.use_containers in ['Docker', 'Podman'] }}
USE_CLI = {{ cookiecutter.command_line_interface != "No command-line interface" }}
USE_CONDA = {{ cookiecutter.use_conda == "yes" }}
{% if cookiecutter.code_of_conduct == "contributor-covenant" -%}
COC_PATH = PROJECT_DIRECTORY / 'coc' / 'CONTRIBUTOR_COVENANT.md'
{%- elif cookiecutter.code_of_conduct == "citizen-code-of-conduct" -%}
COC_PATH = PROJECT_DIRECTORY / 'coc' / 'CITIZEN.md'
{% else %}
COC_PATH = None
{%- endif %}
{% if cookiecutter.governance_document == "numpy-governance" -%}
GOVERNANCE_PATH = PROJECT_DIRECTORY / 'governance' / 'numpy_governance.md'
{% elif cookiecutter.code_of_conduct == "sciml-governance" -%}
GOVERNANCE_PATH = PROJECT_DIRECTORY / 'governance' / 'sciml_governance.md'
{% else -%}
GOVERNANCE_PATH = None
{%- endif %}
{% if cookiecutter.roadmap_document == "pytorch-ignite-roadmap" -%}
ROADMAP_PATH = PROJECT_DIRECTORY / 'roadmap' / 'ignite_roadmap.md'
{%- else %}
ROADMAP_PATH = None
{%- endif %}


def remove_dirs(dirs: list):
    for dirs in dirs:
        shutil.rmtree(dirs)


def remove_dir(dir_path):
    """Remove a directory located at PROJECT_DIRECTORY/dir_path"""
    shutil.rmtree(PROJECT_DIRECTORY/dir_path)


def remove_project_file(filepath: str):
    os.remove(PROJECT_DIRECTORY / filepath)


def remove_package_file(filepath: str):
    os.remove(PACKAGE_PATH / filepath)


def move_selected_doc_dir():
    docs_target_dir = PROJECT_DIRECTORY / "docs"
    for file_name in os.listdir(DOCS_SPEC_DIR):
        shutil.move(DOCS_SPEC_DIR / file_name, docs_target_dir)

    if DOCUMENTATION_ENGINE == "sphinx":
        remove_project_file(Path("docs") / "index.md")
        remove_project_file(Path("docs/api") / "references.md")

    shutil.rmtree(DOCS_SPEC_DIR)

def clean_up_docs():
    remove_dirs(UNUSED_DOCS_DIRS)
    move_selected_doc_dir()


def clean_up_project_layout():
    if USE_SRC_LAYOUT:
        if not os.path.exists("src"):
            os.mkdir("src")
            shutil.move('{{cookiecutter.package_slug}}', 'src')


def clean_up_code_of_conduct():
    if COC_PATH:
        shutil.move(
            COC_PATH,
            PROJECT_DIRECTORY / 'CODE_OF_CONDUCT.md'
        )
    remove_dir("coc")


def clean_up_conda():
    if not USE_CONDA:
        remove_dir("conda")


def clean_up_governance():
    if GOVERNANCE_PATH:
        shutil.move(
            GOVERNANCE_PATH,
            PROJECT_DIRECTORY / 'governance.md'
        )
    remove_dir("governance")


def clean_up_roadmap():
    if ROADMAP_PATH:
        shutil.move(
            ROADMAP_PATH,
            PROJECT_DIRECTORY / 'roadmap.md'
        )
    remove_dir("roadmap")


def clean_up_containers():
    if not USE_CONTAINERS:
        remove_dir("containers")


def clean_up_cli():
    if not USE_CLI:
        remove_package_file("__main__.py")


def http2ssh(url):
    url = url.replace("https://", "git@")
    return url.replace("/", ":", 1)


def validation():
    if USE_BLUE and USE_BLACK:
        raise Exception(
            "The libs Blue and Black were selected, but you need to choose "
            "just one of them."
        )


def prepare_git():
    subprocess.call(["git", "init"])

    git_https_origin = http2ssh("{{cookiecutter.git_https_origin}}")
    git_https_upstream = http2ssh("{{cookiecutter.git_https_upstream}}")
    git_main_branch = http2ssh("{{cookiecutter.git_main_branch}}")
    git_new_branch = "add-initial-structure"

    if git_https_origin != "":
        subprocess.call(["git", "remote", "add", "origin", git_https_origin])
        subprocess.call(["git", "fetch", "--all"])

    if git_https_upstream != "":
        subprocess.call(
            ["git", "remote", "add", "upstream", git_https_upstream]
        )
        subprocess.call(["git", "checkout", f"upstream/{git_main_branch}"])
        subprocess.call(["git", "fetch", "--all"])

    subprocess.call(
        ["git", "config", "user.name", "{{cookiecutter.author_full_name}}"]
    )
    subprocess.call(
        ["git", "config", "user.email", "{{cookiecutter.author_email}}"]
    )

    subprocess.call(["git", "checkout", "-b", git_new_branch])
    subprocess.call(["git", "add", "."])
    subprocess.call(["git", "commit", "-m", "Initial commit", "--no-verify"])
    print("=" * 80)
    print("NOTE: Run `git rebase -i upstream/{{ cookiecutter.git_main_branch }}`")
    print("=" * 80)


def post_gen():
    validation()

    # keep this one first, because it changes the package folder
    clean_up_project_layout()

    clean_up_cli()
    clean_up_code_of_conduct()
    clean_up_conda()
    clean_up_containers()
    clean_up_docs()
    clean_up_governance()
    clean_up_roadmap()

    # keep it at the end, because it will create a new git commit
    prepare_git()


if __name__ == "__main__":
    post_gen()
