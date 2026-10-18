"""Structural checks for the joey-agent plugin package.

The checks use only the standard library, so they run with a plain Python 3.9
or later: `python3 -I -m unittest discover -s tests -v`. They also run with
`python3 -I -m pytest`. The SKILL.md frontmatter is simple `key: value` YAML,
and the tests read it by hand.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest
import zipfile
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
TOOLS_JSON = SKILLS_DIR / "joey" / "references" / "tools.json"
TOOLS_MD = SKILLS_DIR / "joey" / "references" / "tools.md"
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build_skill_zips.py"

PLUGIN_NAME = "joey-agent"
MCP_URL = "https://pouch.getjoey.io/api/customer/mcp"
MCP_HOST_PATH = MCP_URL.split("://", 1)[1]
EXPECTED_SKILLS = {"joey", "joey-activate-path", "joey-path-follow-up", "joey-tracker-sync", "joey-attest", "joey-trust"}
# The server prompts and their arguments.
EXPECTED_PROMPTS = {"joey_make_intro": {"requestId"}, "joey_follow_up": set(), "joey_weekly_review": set()}
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_KEYS = {"name", "description", "allowed-tools", "license"}
# The top-level keys of https://agent-plugins.org/schemas/1.0.0/plugin.schema.json.
AGENT_PLUGIN_KEYS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "extensions",
}
JOEY_NAME = re.compile(r"(?<![A-Za-z0-9_])joey_[a-z0-9_]+")
SKIPPED_DIRS = {".git", "dist", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv"}


def load_json(relative: str) -> dict:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


def parse_frontmatter(text: str) -> dict[str, str]:
    """Read a `---` block of one-line `key: value` fields."""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise AssertionError("SKILL.md must start with a --- frontmatter block")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if line[0].isspace():
            raise AssertionError(f"Each frontmatter field must be one line: {line!r}")
        key, separator, value = line.partition(":")
        if not separator:
            raise AssertionError(f"Frontmatter line without a key: {line!r}")
        fields[key.strip()] = value.strip()
    return fields


def without_fences(text: str) -> str:
    """Remove fenced code blocks before links and headings are read."""
    return re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", text)


def heading_anchors(text: str) -> set[str]:
    """Give the GitHub heading anchors of a Markdown text."""
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for heading in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", without_fences(text)):
        heading = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", heading)
        heading = re.sub(r"<[^>]+>", "", heading).lower()
        slug = "".join(
            c for c in heading if c in " -_" or unicodedata.category(c)[0] in "LN"
        ).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchors.add(f"{slug}-{count}" if count else slug)
    return anchors


def local_links(source: Path) -> list[tuple[str, Path, str]]:
    """Give each relative link of a Markdown file: (text, resolved path, anchor)."""
    links = []
    for target in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", without_fences(source.read_text(encoding="utf-8"))):
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        path, _, anchor = unquote(target).partition("#")
        resolved = (source.parent / path).resolve() if path else source.resolve()
        links.append((target, resolved, anchor))
    return links


def skill_markdown_files() -> list[Path]:
    return sorted(SKILLS_DIR.rglob("*.md"))


def repository_text_files() -> list[Path]:
    files = []
    for path in sorted(REPO_ROOT.rglob("*")):
        if SKIPPED_DIRS.intersection(path.relative_to(REPO_ROOT).parts) or not path.is_file():
            continue
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        files.append(path)
    return files


def tool_catalog() -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Give the tools and the prompts in tools.json, each with its argument names.

    tools.json is the snapshot of the Pouch customer MCP: each tool has `name`,
    `scope`, `arguments` and `annotations`, and each prompt has `name` and
    `arguments`.
    """
    catalog = json.loads(TOOLS_JSON.read_text(encoding="utf-8"))
    tools = {entry["name"]: set(entry["arguments"]) for entry in catalog["tools"]}
    prompts = {entry["name"]: set(entry["arguments"]) for entry in catalog["prompts"]}
    return tools, prompts


def tools_md_inputs() -> dict[str, set[str]]:
    """Give the arguments that tools.md lists under "- Input:" for each tool.

    Each argument is a bullet with two spaces of indent that starts with the
    argument name in backticks. A deeper bullet (a field of an argument) does
    not count. "- Input: none." gives no argument.
    """
    text = without_fences(TOOLS_MD.read_text(encoding="utf-8"))
    inputs: dict[str, set[str]] = {}
    for name, body in re.findall(r"(?ms)^### (joey_[a-z0-9_]+)\s*\n(.*?)(?=^#{1,3} |\Z)", text):
        block = re.search(r"(?ms)^- Input:(.*?)(?=^- )", body)
        if not block:
            raise AssertionError(f"{name} has no '- Input:' line in tools.md")
        inputs[name] = set(re.findall(r"(?m)^  - `([A-Za-z]+)`", block.group(1)))
    return inputs


class ManifestTests(unittest.TestCase):
    def test_claude_manifest(self):
        manifest = load_json(".claude-plugin/plugin.json")
        self.assertEqual(manifest["name"], PLUGIN_NAME)
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue(manifest["description"])
        self.assertNotIn("mcpServers", manifest, "The plugin loads .mcp.json by itself")

    def test_claude_marketplace(self):
        marketplace = load_json(".claude-plugin/marketplace.json")
        self.assertEqual(marketplace["name"], PLUGIN_NAME)
        plugins = {plugin["name"]: plugin for plugin in marketplace["plugins"]}
        self.assertEqual(set(plugins), {PLUGIN_NAME})
        self.assertEqual(plugins[PLUGIN_NAME]["source"], "./")

    def test_codex_manifest_follows_the_agent_plugins_schema(self):
        manifest = load_json("plugin.json")
        self.assertEqual(
            manifest["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
        )
        self.assertEqual(manifest["name"], PLUGIN_NAME)
        self.assertLessEqual(set(manifest), AGENT_PLUGIN_KEYS)
        interface = manifest["extensions"]["com.openai"]["interface"]
        self.assertEqual(interface["displayName"], "Joey")
        for prompt in interface["defaultPrompt"]:
            skill = re.match(r"Use \$([a-z0-9-]+) ", prompt)
            self.assertTrue(skill, prompt)
            self.assertIn(skill.group(1), EXPECTED_SKILLS, prompt)

    def test_codex_marketplace(self):
        marketplace = load_json(".agents/plugins/marketplace.json")
        plugins = {plugin["name"]: plugin for plugin in marketplace["plugins"]}
        self.assertEqual(set(plugins), {PLUGIN_NAME})
        entry = plugins[PLUGIN_NAME]
        self.assertEqual(entry["source"], {"source": "local", "path": "./"})
        self.assertEqual(
            entry["policy"], {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
        )
        self.assertTrue(entry["category"])

    def test_one_semantic_version_in_all_manifests_and_the_changelog(self):
        versions = {
            ".claude-plugin/plugin.json": load_json(".claude-plugin/plugin.json")["version"],
            "plugin.json": load_json("plugin.json")["version"],
            ".claude-plugin/marketplace.json": next(
                p["version"] for p in load_json(".claude-plugin/marketplace.json")["plugins"]
                if p["name"] == PLUGIN_NAME
            ),
            ".agents/plugins/marketplace.json": next(
                p["version"] for p in load_json(".agents/plugins/marketplace.json")["plugins"]
                if p["name"] == PLUGIN_NAME
            ),
        }
        self.assertEqual(len(set(versions.values())), 1, versions)
        version = versions["plugin.json"]
        self.assertRegex(version, SEMVER)
        changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        latest = re.search(r"(?m)^## (\S+)", changelog)
        self.assertTrue(latest, "CHANGELOG.md has no version entry")
        self.assertEqual(latest.group(1), version)
        for skill in SKILLS_DIR.iterdir():
            if skill.is_dir():
                update = (skill / "references/updates.md").read_text()
                installed = re.search(r"Installed release: `([^`]+)`", update)
                self.assertIsNotNone(installed, str(skill))
                self.assertEqual(installed.group(1), version)

    def test_one_description_in_all_manifests(self):
        descriptions = {
            load_json(".claude-plugin/plugin.json")["description"],
            load_json("plugin.json")["description"],
            load_json(".claude-plugin/marketplace.json")["plugins"][0]["description"],
        }
        self.assertEqual(len(descriptions), 1, descriptions)


class McpServerTests(unittest.TestCase):
    def test_claude_mcp_json_is_the_exact_remote_server(self):
        self.assertEqual(
            load_json(".mcp.json"),
            {"mcpServers": {"joey": {"type": "http", "url": MCP_URL}}},
        )

    def test_codex_mcp_json_is_the_same_server_with_oauth(self):
        config = load_json("mcp.json")
        self.assertEqual(
            config["$schema"], "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
        )
        self.assertEqual(set(config["mcpServers"]), {"joey"})
        server = config["mcpServers"]["joey"]
        self.assertEqual(server["type"], "streamable-http")
        self.assertEqual(server["url"], MCP_URL)
        self.assertNotIn("headers", server)
        auth = server["extensions"]["com.openai"]["auth"]
        self.assertEqual(auth, {"type": "oauth", "client": {"mode": "dcr"}})

    def test_mcp_configs_have_no_variables_or_secrets(self):
        for relative in (".mcp.json", "mcp.json"):
            text = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn("${", text, relative)
            self.assertNotIn("http://", text, relative)
            self.assertNotRegex(text, r"(?i)authorization|bearer|token|secret", relative)

    def test_every_mention_of_the_mcp_server_uses_the_exact_url(self):
        mentions = 0
        for path in repository_text_files():
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"[A-Za-z]*:?/*" + re.escape(MCP_HOST_PATH) + r"[^\s\"'`)<>]*", text):
                mentions += 1
                self.assertEqual(match.group(0), MCP_URL, f"{path.relative_to(REPO_ROOT)}")
        self.assertGreater(mentions, 2)


class SkillTests(unittest.TestCase):
    def test_skills_folder_has_exactly_the_six_skills(self):
        found = {path.name for path in SKILLS_DIR.iterdir() if path.is_dir()}
        self.assertEqual(found, EXPECTED_SKILLS)

    def test_frontmatter_name_and_description(self):
        for skill in sorted(EXPECTED_SKILLS):
            with self.subTest(skill=skill):
                fields = parse_frontmatter((SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8"))
                self.assertLessEqual(set(fields), FRONTMATTER_KEYS)
                self.assertEqual(fields.get("name"), skill)
                self.assertRegex(skill, SKILL_NAME)
                self.assertLessEqual(len(skill), 64)
                description = fields.get("description", "")
                self.assertTrue(description, "description must not be empty")
                self.assertLessEqual(len(description), 1024)
                # A plain YAML line: no XML tags, no `: ` or ` #`, and no YAML indicator first.
                self.assertNotRegex(description, r"[<>]")
                self.assertNotIn(": ", description)
                self.assertNotIn(" #", description)
                self.assertNotRegex(description, r"^[-?:,\[\]{}#&*!|>'\"%@`]")

    def test_skill_links_resolve_inside_their_own_skill(self):
        for source in skill_markdown_files():
            skill_dir = SKILLS_DIR / source.relative_to(SKILLS_DIR).parts[0]
            for target, resolved, anchor in local_links(source):
                with self.subTest(source=str(source.relative_to(REPO_ROOT)), link=target):
                    self.assertTrue(
                        str(resolved).startswith(str(skill_dir.resolve()) + "/"),
                        "A skill links only to files in its own folder",
                    )
                    self.assertTrue(resolved.is_file())
                    if anchor:
                        self.assertIn(anchor, heading_anchors(resolved.read_text(encoding="utf-8")))

    def test_repository_links_resolve(self):
        for name in ("README.md", "AGENTS.md", "CHANGELOG.md"):
            source = REPO_ROOT / name
            for target, resolved, anchor in local_links(source):
                with self.subTest(source=name, link=target):
                    self.assertTrue(str(resolved).startswith(str(REPO_ROOT.resolve()) + "/"))
                    self.assertTrue(resolved.exists())
                    if anchor:
                        self.assertIn(anchor, heading_anchors(resolved.read_text(encoding="utf-8")))

    def test_skills_link_to_their_references(self):
        for skill in sorted(EXPECTED_SKILLS):
            references = SKILLS_DIR / skill / "references"
            if not references.is_dir():
                continue
            linked = {
                resolved
                for source in (SKILLS_DIR / skill).rglob("*.md")
                for _, resolved, _ in local_links(source)
            }
            for reference in sorted(references.iterdir()):
                with self.subTest(reference=str(reference.relative_to(REPO_ROOT))):
                    self.assertIn(reference.resolve(), linked, "Link each reference file")


class ToolCatalogTests(unittest.TestCase):
    def test_tools_json_lists_unique_joey_tools(self):
        catalog = json.loads(TOOLS_JSON.read_text(encoding="utf-8"))
        names = [entry["name"] for entry in catalog["tools"]]
        names += [entry["name"] for entry in catalog["prompts"]]
        self.assertTrue(catalog["tools"])
        self.assertEqual(len(names), len(set(names)), "A name is in tools.json twice")
        for name in names:
            self.assertRegex(name, r"^joey_[a-z0-9_]+$")
        for entry in catalog["tools"]:
            with self.subTest(tool=entry["name"]):
                self.assertIn(entry["scope"], {"workspace:read", "intros:write", "icp:write", "trust:read", "trust:write"})
                self.assertIsInstance(entry["annotations"]["readOnlyHint"], bool)

    def test_the_server_prompts(self):
        _, prompts = tool_catalog()
        self.assertEqual(prompts, EXPECTED_PROMPTS)

    def test_every_named_joey_tool_is_in_tools_json(self):
        tools, prompts = tool_catalog()
        known = set(tools) | set(prompts)
        sources = skill_markdown_files() + [REPO_ROOT / "README.md"]
        for source in sources:
            for name in sorted(set(JOEY_NAME.findall(source.read_text(encoding="utf-8")))):
                with self.subTest(source=str(source.relative_to(REPO_ROOT)), name=name):
                    self.assertIn(name, known)

    def test_every_tool_has_a_section_in_tools_md(self):
        tools, _ = tool_catalog()
        sections = set(re.findall(r"(?m)^### (joey_[a-z0-9_]+)\s*$", TOOLS_MD.read_text(encoding="utf-8")))
        self.assertEqual(sections, set(tools))

    def test_tools_md_lists_the_real_arguments_of_each_tool(self):
        tools, _ = tool_catalog()
        inputs = tools_md_inputs()
        self.assertEqual(set(inputs), set(tools))
        for name, arguments in sorted(inputs.items()):
            with self.subTest(tool=name):
                self.assertEqual(arguments, tools[name])


class SkillZipTests(unittest.TestCase):
    def build(self, out_dir: Path) -> None:
        subprocess.run(
            [sys.executable, "-I", str(BUILD_SCRIPT), "--out", str(out_dir)],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_one_zip_for_each_skill_with_skill_md_in_the_root_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            out_dir = Path(temp)
            self.build(out_dir)
            zips = {path.stem: path for path in out_dir.glob("*.zip")}
            self.assertEqual(set(zips), EXPECTED_SKILLS)
            for skill, path in sorted(zips.items()):
                with self.subTest(skill=skill), zipfile.ZipFile(path) as archive:
                    names = archive.namelist()
                    self.assertIn(f"{skill}/SKILL.md", names)
                    self.assertTrue(all(name.startswith(f"{skill}/") for name in names), names)
                    expected = sorted(
                        f"{skill}/{file.relative_to(SKILLS_DIR / skill).as_posix()}"
                        for file in (SKILLS_DIR / skill).rglob("*")
                        if file.is_file() and file.name != ".DS_Store"
                    )
                    self.assertEqual(sorted(names), expected)
                    self.assertEqual(
                        archive.read(f"{skill}/SKILL.md"),
                        (SKILLS_DIR / skill / "SKILL.md").read_bytes(),
                    )

    def test_zips_are_deterministic(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            self.build(Path(first))
            self.build(Path(second))
            for skill in sorted(EXPECTED_SKILLS):
                with self.subTest(skill=skill):
                    self.assertEqual(
                        (Path(first) / f"{skill}.zip").read_bytes(),
                        (Path(second) / f"{skill}.zip").read_bytes(),
                    )


class RepositoryTests(unittest.TestCase):
    def test_license_is_proprietary(self):
        text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("All rights reserved", text)
        self.assertIn("Joey", text)

    def test_claude_md_is_a_symlink_to_agents_md(self):
        claude = REPO_ROOT / "CLAUDE.md"
        self.assertTrue(claude.is_symlink())
        self.assertEqual(os.readlink(claude), "AGENTS.md")

    def test_dist_is_ignored(self):
        ignored = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").split()
        self.assertIn("dist/", ignored)


if __name__ == "__main__":
    unittest.main()
