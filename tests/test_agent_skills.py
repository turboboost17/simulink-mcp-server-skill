import asyncio
from pathlib import Path

from simulink_mcp_server.mcp_server import handle_list_tools

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / ".agents" / "skills"

EXPECTED_SKILLS = {
    "building-simulink-models",
    "generate-requirement-drafts",
    "matlab-build-app",
    "matlab-create-live-script",
    "matlab-debugging",
    "matlab-install-products",
    "matlab-list-products",
    "matlab-map-database-objects",
    "matlab-modernize-code",
    "matlab-read-database",
    "matlab-review-code",
    "matlab-testing",
    "matlab-use-duckdb",
    "matlab-write-database",
    "simulating-simulink-models",
    "specifying-mbd-algorithms",
    "specifying-plant-models",
    "testing-simulink-models",
}

EXCLUDED_SKILLS = {
    "filing-bug-reports",
    "matlab-agentic-toolkit-setup",
    "simulink-agentic-toolkit-setup",
}

UPSTREAM_NONLOCAL_TOOLS = {
    "check_matlab_code",
    "detect_matlab_toolboxes",
    "evaluate_matlab_code",
    "model_edit",
    "model_overview",
    "model_query_params",
    "model_read",
    "model_resolve_params",
    "model_test",
    "run_matlab_file",
    "run_matlab_test_file",
}


def _registered_tool_names() -> set[str]:
    return {tool.name for tool in asyncio.run(handle_list_tools())}


def _manifest_required_tools(manifest_path: Path) -> set[str]:
    tools: set[str] = set()
    in_requires_tools = False

    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("requires-tools:"):
            in_requires_tools = True
            continue
        if in_requires_tools and stripped.startswith("-"):
            tools.add(stripped.removeprefix("-").strip())
            continue
        if in_requires_tools and stripped and not line.startswith(" "):
            break

    return tools


def test_expected_agent_skills_are_installed() -> None:
    installed = {path.name for path in SKILLS_DIR.iterdir() if path.is_dir()}

    assert EXPECTED_SKILLS <= installed
    assert EXCLUDED_SKILLS.isdisjoint(installed)

    for skill_name in EXPECTED_SKILLS:
        skill_dir = SKILLS_DIR / skill_name
        assert (skill_dir / "SKILL.md").is_file()
        assert (skill_dir / "manifest.yaml").is_file()


def test_agent_skills_do_not_include_p_files() -> None:
    assert not list((ROOT / ".agents").rglob("*.p"))


def test_agent_skills_do_not_include_upstream_eval_fixtures() -> None:
    assert not list(SKILLS_DIR.glob("*/evals"))


def test_agent_skill_manifests_require_only_local_tools() -> None:
    registered_tools = _registered_tool_names()

    for manifest_path in SKILLS_DIR.glob("*/manifest.yaml"):
        required_tools = _manifest_required_tools(manifest_path)

        assert required_tools <= registered_tools, manifest_path
        assert UPSTREAM_NONLOCAL_TOOLS.isdisjoint(required_tools), manifest_path
