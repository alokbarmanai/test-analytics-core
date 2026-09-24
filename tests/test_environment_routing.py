# tests/test_environment_routing.py


def test_api_endpoint_routing(env_properties):
    # Retrieve configuration properties cleanly
    target_url = env_properties["base_url"]
    db_string = env_properties["db_connection"]
    timeout_limit = env_properties["timeout"]

    print(f"\n[EXECUTION LOG] Target URL: {target_url}")
    print(f"[EXECUTION LOG] Timeout Limit Configured: {timeout_limit}s")

    # Run assertions against the active environment metrics
    assert target_url.startswith("http")

    # Corrected check: Only assert "prod" is absent if we are NOT hitting the production URL
    if target_url != "https://company.com":
        assert (
            "prod" not in db_string
        ), "Safety Check Failed: Production DB string detected in non-prod environment!"
