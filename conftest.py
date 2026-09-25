# conftest.py
import pytest
from pytest_metadata.plugin import metadata_key
from tests.config_factory import ENV_CONFIGS
from pytest_html import extras


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


# conftest.py (continued)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Lifecycle hook executed after setup, call, and teardown of each test.
    Intercepts failures and prepares custom artifact data.
    """
    # 1. Allow the test phase to execute and capture the outcome report
    outcome = yield
    report = outcome.get_result()

    # 2. We only care about errors that happen during the actual test execution phase ('call')
    if report.when == "call" and report.failed:
        # In a real-world scenario, you can grab contextual logs or client data from your test fixture
        # For this example, we will simulate embedding a raw API JSON error payload
        failed_api_payload = (
            "{\n"
            '  "error": "Internal Database Constraint Violation",\n'
            '  "status_code": 500,\n'
            f'  "failed_at_endpoint": "{item.name}",\n'
            '  "remediation": "Check DB foreign key relations."\n'
            "}"
        )

        # 3. Create a clean, scrollable code block snippet using pytest-html extras
        html_code_block = extras.text(
            failed_api_payload, name="Captured API Error Response"
        )

        # 4. Attach the artifact directly into the test case's report data list
        if not hasattr(report, "extras"):
            report.extras = []
        report.extras.append(html_code_block)
