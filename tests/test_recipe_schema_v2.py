"""Lint: every shipped recipe that delegates to a namespaced agent must be portable.

A recipe with an `agent:` reference but no `schema_version: 2` manifest is
*caller-bound*: it only runs from a session whose bundle already happens to
carry those agents, and it fails with "agent not found in configuration"
everywhere else. Declaring `schema_version: 2` plus a `dependencies:` block
makes the recipe resolve its agents from its own declared closure instead.

These tests are the guard rail: they fail if a new recipe ships an `agent:`
reference without the manifest, or if a manifest under-declares the agents the
recipe actually uses.
"""

import re
from pathlib import Path

import yaml

RECIPES_DIR = Path(__file__).parent.parent / "recipes"

# Files deliberately left on the legacy schema, each with the reason why.
# A recipe belongs here ONLY when schema v2 cannot express it -- e.g. it uses
# `agent: self`, which has no declarable source (an agent identity that only
# exists inside the calling session cannot be pinned to a bundle). Convenience
# is not a reason.
LEGACY_EXEMPT: dict[str, str] = {}

AGENT_REF = re.compile(r'^\s*agent:\s*"?(?P<ref>[A-Za-z0-9_-]+:[A-Za-z0-9_-]+)"?\s*$', re.M)


def recipe_files() -> list[Path]:
    """Every shipped recipe, including any nested under subdirectories."""
    return sorted(RECIPES_DIR.glob("**/*.yaml"))


def referenced_agents(path: Path) -> set[str]:
    """The `ns:name` agent references a recipe delegates to."""
    return set(AGENT_REF.findall(path.read_text()))


def declared_agents(recipe: dict) -> set[str]:
    """Every agent named under any dependency's `required_agents`."""
    declared: set[str] = set()
    for dep in recipe.get("dependencies") or []:
        declared.update(dep.get("required_agents") or [])
    return declared


def test_recipes_directory_is_not_empty():
    """Guard the guard: an empty glob would make every test below vacuous."""
    assert recipe_files(), f"no recipes found under {RECIPES_DIR}"


class TestSchemaVersionDeclared:
    def test_every_recipe_with_an_agent_declares_schema_version_2(self):
        """A recipe that delegates must declare its dependency closure."""
        offenders = []
        for path in recipe_files():
            if path.name in LEGACY_EXEMPT:
                continue
            if not referenced_agents(path):
                continue
            recipe = yaml.safe_load(path.read_text())
            if recipe.get("schema_version") != 2:
                offenders.append(
                    f"{path.relative_to(RECIPES_DIR.parent)}: references "
                    f"{sorted(referenced_agents(path))} but schema_version is "
                    f"{recipe.get('schema_version')!r}"
                )
        assert not offenders, "recipes missing `schema_version: 2`:\n  " + "\n  ".join(offenders)

    def test_every_v2_recipe_declares_at_least_one_dependency(self):
        """`schema_version: 2` with no `dependencies:` declares an empty closure."""
        offenders = []
        for path in recipe_files():
            recipe = yaml.safe_load(path.read_text())
            if recipe.get("schema_version") != 2:
                continue
            if not (recipe.get("dependencies") or []):
                offenders.append(str(path.relative_to(RECIPES_DIR.parent)))
        assert not offenders, "v2 recipes with no `dependencies:` block:\n  " + "\n  ".join(offenders)


class TestDependenciesCoverEveryAgent:
    def test_every_referenced_agent_is_declared(self):
        """An agent used but not declared is unresolvable in a closed world."""
        offenders = []
        for path in recipe_files():
            if path.name in LEGACY_EXEMPT:
                continue
            recipe = yaml.safe_load(path.read_text())
            if recipe.get("schema_version") != 2:
                continue
            missing = referenced_agents(path) - declared_agents(recipe)
            if missing:
                offenders.append(
                    f"{path.relative_to(RECIPES_DIR.parent)}: undeclared {sorted(missing)}"
                )
        assert not offenders, "agents used but not declared:\n  " + "\n  ".join(offenders)

    def test_every_dependency_pins_a_ref(self):
        """A `source:` with no `@ref` floats; the resolver needs a branch or tag."""
        offenders = []
        for path in recipe_files():
            recipe = yaml.safe_load(path.read_text())
            for dep in recipe.get("dependencies") or []:
                source = dep.get("source", "")
                # `git+https://host/org/repo@ref` -- the `@ref` is the pin.
                if source.startswith("git+") and "@" not in source.rsplit("/", 1)[-1]:
                    offenders.append(f"{path.relative_to(RECIPES_DIR.parent)}: unpinned {source!r}")
        assert not offenders, "dependency sources with no pinned ref:\n  " + "\n  ".join(offenders)


class TestLegacyExemptionsAreHonest:
    def test_exempt_files_exist(self):
        """A stale exemption silently un-guards a file that was later renamed."""
        missing = [name for name in LEGACY_EXEMPT if not (RECIPES_DIR / name).exists()]
        assert not missing, f"LEGACY_EXEMPT names files that do not exist: {missing}"

    def test_exempt_files_have_a_reason(self):
        """An exemption without a reason is an exemption nobody can review."""
        blank = [name for name, reason in LEGACY_EXEMPT.items() if not reason.strip()]
        assert not blank, f"LEGACY_EXEMPT entries with no reason: {blank}"
