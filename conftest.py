# conftest.py
import pytest
from pytest_metadata.plugin import metadata_key
from tests.config_factory import ENV_CONFIGS


def pytest_addoption(parser):
    """Registers our environmental configuration flags."""
    parser.addoption(
        "--env",
        action="store",
        default="testing",
        help="Environment context: testing, qa, or production",
    )
    # New secondary safety flag required ONLY for production execution
    parser.addoption(
        "--force",
        action="store_true",  # Acts as a boolean flag (True if present, False if absent)
        help="Mandatory confirmation flag to execute tests against PRODUCTION",
    )


@pytest.fixture(scope="session")
def env_properties(request):
    """Returns the configuration map for the selected environment context."""
    env_name = request.config.getoption("--env").lower()

    if env_name not in ENV_CONFIGS:
        raise pytest.UsageError(
            f"Unsupported environment validation profile: {env_name}"
        )

    return ENV_CONFIGS[env_name]


def pytest_html_report_title(report):
    """Sets a professional title on your HTML test dashboard."""
    report.title = "Test Analytics Core Execution Report"


def pytest_collection_modifyitems(config, items):
    """
    Safety Guard Hook: Evaluates the configuration flags before execution begins.
    If production is targeted without --force, it skips all collected tests.
    """
    env_name = config.getoption("--env").lower()
    force_enabled = config.getoption("--force")

    # If the user targets production but forgot to append --force
    if env_name == "production" and not force_enabled:
        # Dynamically create an internal pytest skip marker with an explicit warning
        safety_skip_marker = pytest.mark.skip(
            reason="CRITICAL SAFETY BLOCK: Production run intercepted. Re-run with the '--force' flag to execute."
        )

        # Apply the skip marker to every single collected test case dynamically
        for item in items:
            item.add_marker(safety_skip_marker)


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    """Safely injects custom rows into the metadata storage."""
    active_env = session.config.getoption("--env")

    if metadata_key in session.config.stash:
        session.config.stash[metadata_key]["Target Environment"] = active_env.upper()
        session.config.stash[metadata_key]["Automation Lead"] = "Alok Barman"
