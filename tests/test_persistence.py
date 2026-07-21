from app import repository
from app.models import AnalysisBlockedRecord, ConsentRecord, CreatorProfile, EvidenceItem, Project, SourceAsset
from app.storage import InMemoryStorage
from tests.conftest import make_fake_mp4_bytes


def test_project_round_trip():
    storage = InMemoryStorage()
    project = Project(name="Test Project")
    repository.save_project(storage, project)

    loaded = repository.get_project(storage, project.id)
    assert loaded is not None
    assert loaded.id == project.id
    assert loaded.name == "Test Project"


def test_get_project_returns_none_when_absent():
    storage = InMemoryStorage()
    assert repository.get_project(storage, "nope") is None


def test_source_round_trip_including_original_bytes():
    storage = InMemoryStorage()
    project = Project(name="Test Project")
    repository.save_project(storage, project)

    consent = ConsentRecord(
        project_id=project.id, statement="I authorize this.", permitted_uses=["analysis"]
    )
    repository.save_consent(storage, consent)

    original_bytes = make_fake_mp4_bytes()
    source = SourceAsset(
        project_id=project.id,
        consent_id=consent.id,
        original_filename="clip.mp4",
        content_type="video/mp4",
        size_bytes=len(original_bytes),
        checksum_sha256="deadbeef",
        storage_key=repository.source_original_key(project.id, "placeholder", "clip.mp4"),
        storage_backend="local-disk-fallback",
    )
    repository.save_source(storage, source, original_bytes)

    loaded = repository.get_source(storage, project.id, source.id)
    assert loaded is not None
    assert loaded.original_filename == "clip.mp4"
    assert loaded.checksum_sha256 == "deadbeef"

    retrieved_bytes = storage.get_object(
        repository.source_original_key(project.id, source.id, "clip.mp4")
    )
    assert retrieved_bytes == original_bytes


def test_analysis_result_round_trip_creator_profile():
    storage = InMemoryStorage()
    profile = CreatorProfile(
        project_id="p1",
        source_id="s1",
        audience="test audience",
        content_pillars=["a"],
        evidence=[EvidenceItem(source_reference="0:01", observation="x")],
        confidence=0.5,
        limitations=["single example"],
        analysis_provider="gmi-cloud",
        analysis_model="test-model",
        prompt_schema_version="v1",
        source_asset_hash="hash",
    )
    repository.save_profile(storage, profile)

    loaded = repository.get_analysis_result(storage, "p1", "s1")
    assert isinstance(loaded, CreatorProfile)
    assert loaded.audience == "test audience"


def test_analysis_result_round_trip_blocked_record():
    storage = InMemoryStorage()
    blocked = AnalysisBlockedRecord(
        project_id="p1", source_id="s1", reason="GMI_API_KEY is not configured."
    )
    repository.save_blocked_record(storage, blocked)

    loaded = repository.get_analysis_result(storage, "p1", "s1")
    assert isinstance(loaded, AnalysisBlockedRecord)
    assert loaded.status == "blocked"
    assert "not configured" in loaded.reason


def test_analysis_result_none_when_not_yet_analyzed():
    storage = InMemoryStorage()
    assert repository.get_analysis_result(storage, "p1", "s1") is None


def test_data_survives_across_repository_calls_simulating_restore_after_refresh():
    """The same storage instance persisting across multiple, independent
    repository calls is the realistic analogue of 'restore after refresh'
    for this architecture: a running server backed by durable storage,
    where each HTTP request is a fresh call into the repository layer."""
    storage = InMemoryStorage()
    project = Project(name="Persisted Project")
    repository.save_project(storage, project)

    # Simulate a later, independent "request" reading from the same store.
    reloaded = repository.get_project(storage, project.id)
    assert reloaded is not None
    assert reloaded.name == "Persisted Project"
