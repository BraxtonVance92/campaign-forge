"""Focused UI/route tests for the visual-refresh states that the existing
suite never exercised: the successful-analysis template (no prior test
constructed a real CreatorProfile and rendered it), long-content
handling, loading-state markup, and a broken-route scan cross-checking
every template href/form action against FastAPI's real route table.
"""

import re

from app.main import app, templates
from app.models import AnalysisBlockedRecord, CreatorProfile, EvidenceItem, Project, SourceAsset
from tests.conftest import make_fake_mp4_bytes
from tests.test_upload_validation import create_project


def _render_project_page(project, source, result, storage_backend="in-memory-fake"):
    template = templates.get_template("project.html")
    return template.render(
        project=project, source=source, result=result, storage_backend=storage_backend
    )


def _make_project_and_source():
    project = Project(name="Rendering Test")
    source = SourceAsset(
        project_id=project.id,
        consent_id="c1",
        original_filename="clip.mp4",
        content_type="video/mp4",
        size_bytes=2048,
        checksum_sha256="deadbeef",
        storage_key="projects/x/sources/y/original/clip.mp4",
        storage_backend="local-disk-fallback",
    )
    return project, source


def _full_profile(**overrides):
    base = dict(
        project_id="p1",
        source_id="s1",
        audience="solo creators building a personal brand",
        content_pillars=["productivity tips"],
        voice_traits=["direct", "encouraging"],
        hook_patterns=["opens with a question"],
        structure_patterns=["problem -> insight -> cta"],
        visual_patterns=["handheld camera"],
        cta_patterns=["ask viewers to comment"],
        avoid=["overly corporate tone"],
        evidence=[EvidenceItem(source_reference="0:03", observation="direct question to camera")],
        confidence=0.42,
        limitations=["based on a single example"],
        analysis_provider="gmi-cloud",
        analysis_model="nvidia/nemotron-3-nano-omni",
        prompt_schema_version="cf-run-001-v2",
        source_asset_hash="deadbeef",
        request_shape_verified=False,
    )
    base.update(overrides)
    return CreatorProfile(**base)


def test_successful_result_renders_all_required_sections_from_real_fields():
    project, source = _make_project_and_source()
    profile = _full_profile()
    html = _render_project_page(project, source, profile)

    # The required groupings per the redesign brief, built only from real
    # persisted CreatorProfile fields -- never fabricated copy.
    for heading in ["Content patterns", "Tone", "Hooks", "Visual style", "Recommendations"]:
        assert heading in html
    assert "Audience" in html and profile.audience in html
    assert "Confidence" in html and "0.42" in html
    assert "productivity tips" in html  # content_pillars
    # Jinja2 autoescaping renders "->" as "-&gt;" -- correct behavior for
    # provider-sourced text (defends against XSS in analysis output), so the
    # assertion checks the escaped form actually sent to the browser.
    assert "problem -&gt; insight -&gt; cta" in html  # structure_patterns, merged into content patterns
    assert "direct" in html and "encouraging" in html  # voice_traits (Tone)
    assert "opens with a question" in html  # hook_patterns
    assert "handheld camera" in html  # visual_patterns
    assert "ask viewers to comment" in html  # cta_patterns
    assert "overly corporate tone" in html  # avoid
    assert "based on a single example" in html  # limitations

    # Technical/debug info must be tucked inside a disclosure, not front-and-center.
    tech_block = html[html.index('<details class="technical-details">'):]
    assert "nvidia/nemotron-3-nano-omni" in tech_block
    assert "cf-run-001-v2" in tech_block

    # Experimental marker must be visible when request_shape_verified is False.
    assert "Experimental analysis" in html


def test_successful_result_marks_verified_shape_without_experimental_badge():
    project, source = _make_project_and_source()
    profile = _full_profile(request_shape_verified=True)
    html = _render_project_page(project, source, profile)
    assert "Experimental analysis" not in html


def test_successful_result_shows_honest_empty_state_for_missing_optional_fields():
    """Optional facets (voice_traits, hook_patterns, visual_patterns,
    cta_patterns, avoid) can legitimately come back empty from a real
    analysis. The UI must say so honestly, not render a blank section."""
    project, source = _make_project_and_source()
    profile = _full_profile(
        voice_traits=[], hook_patterns=[], visual_patterns=[], cta_patterns=[], avoid=[]
    )
    html = _render_project_page(project, source, profile)
    assert html.count("Not identified in this analysis.") >= 3


def test_blocked_state_renders_long_error_message_without_crashing():
    project, source = _make_project_and_source()
    long_reason = (
        "GMI returned HTTP 503. " + ("Detail segment without spaces. " * 40)
    )
    blocked = AnalysisBlockedRecord(project_id="p1", source_id="s1", reason=long_reason)
    html = _render_project_page(project, source, blocked)
    assert long_reason in html
    assert "No result was invented" in html
    # A retry action must be offered for a real (not just missing-credential) failure.
    assert "Try analysis again" in html


def test_source_row_renders_long_filename_with_truncation_markup():
    project, source = _make_project_and_source()
    long_name = "a" * 40 + "_extremely_long_creator_upload_filename_example.mp4"
    source = source.model_copy(update={"original_filename": long_name})
    html = _render_project_page(project, source, None)
    # The full name is present (in a title attribute for accessibility/copy)
    # and CSS handles the visual truncation (verified manually in-browser;
    # see the evidence packet -- pytest cannot assert rendered pixel width).
    assert long_name in html
    assert f'title="{long_name}"' in html


def test_upload_and_analyze_forms_declare_a_loading_state():
    project, source = _make_project_and_source()
    html_no_source = _render_project_page(project, None, None)
    assert 'data-loading-text="Uploading…"' in html_no_source

    html_ready = _render_project_page(project, source, None)
    assert 'data-loading-text="Analyzing…"' in html_ready

    home_html = templates.get_template("home.html").render()
    assert 'data-loading-text="Creating…"' in home_html


def test_all_three_forms_share_the_same_progressive_enhancement_script():
    project, _ = _make_project_and_source()
    project_html = _render_project_page(project, None, None)
    home_html = templates.get_template("home.html").render()
    for html in (project_html, home_html):
        assert "form[data-loading-text]" in html
        assert "btn.disabled = true" in html


def test_no_broken_internal_links_or_form_actions_in_rendered_templates():
    """Cross-checks every internal href/action in both templates against
    FastAPI's actual registered route table -- a real broken-route scan,
    not just a visual check."""
    def flatten_routes(routes):
        """FastAPI wraps app.include_router(...) results in an internal
        `_IncludedRouter` object (fastapi>=0.139) whose real routes live at
        `.original_router.routes` rather than directly on `app.routes` --
        walk both that shape and the plain Starlette `.routes` shape so this
        scan doesn't silently miss every route registered via a router."""
        flat = []
        for route in routes:
            nested = getattr(route, "original_router", None)
            if nested is not None:
                flat.extend(flatten_routes(nested.routes))
                continue
            sub_routes = getattr(route, "routes", None)
            if sub_routes:
                flat.append(route)  # keep Mount itself (for prefix matching)
                flat.extend(flatten_routes(sub_routes))
                continue
            flat.append(route)
        return flat

    all_routes = flatten_routes(app.routes)
    real_paths = {route.path for route in all_routes if hasattr(route, "path")}
    # Mounted sub-apps (e.g. StaticFiles at "/static") match any sub-path,
    # not just their exact mount point.
    mount_prefixes = tuple(
        route.path for route in all_routes if type(route).__name__ == "Mount"
    )

    def path_is_registered(path: str) -> bool:
        if any(path == prefix or path.startswith(prefix + "/") for prefix in mount_prefixes):
            return True
        # Convert a rendered Jinja path like /projects/abc-123/sources/xyz
        # into FastAPI's path-parameter form and check it matches a real route.
        for real in real_paths:
            pattern = re.sub(r"\{[^/]+\}", r"[^/]+", real)
            if re.fullmatch(pattern, path):
                return True
        return False

    project, source = _make_project_and_source()
    profile = _full_profile()

    samples = [
        templates.get_template("home.html").render(),
        _render_project_page(project, None, None),
        _render_project_page(project, source, None),
        _render_project_page(project, source, profile),
    ]

    found_any_internal_link = False
    for html in samples:
        for match in re.finditer(r'(?:href|action)="(/[^"]*)"', html):
            path = match.group(1)
            found_any_internal_link = True
            assert path_is_registered(path), f"No registered route matches: {path}"

    assert found_any_internal_link, "expected at least one internal link/action to check"
