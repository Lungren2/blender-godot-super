from super_mcp.hygiene import find_layout_violations


def test_hygiene_accepts_established_layout() -> None:
    assert find_layout_violations(
        [
            "src/super_mcp/server.py",
            "scripts/check_repo_hygiene.py",
            "tests/unit/test_hygiene.py",
            "docs/architecture.md",
            "README.md",
        ]
    ) == []


def test_hygiene_rejects_root_code_and_generated_artifacts() -> None:
    violations = find_layout_violations(
        [
            "scratch.py",
            "src/super_mcp/__pycache__/server.pyc",
            ".super-mcp/audit/actions.jsonl",
            "integrations/blender/test.blend1",
        ]
    )

    assert any("unexpected top-level" in violation for violation in violations)
    assert any("generated/cache directory" in violation for violation in violations)
    assert any("generated/editor artifact" in violation for violation in violations)
