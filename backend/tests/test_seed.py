from dataclasses import replace
from types import SimpleNamespace

from scripts import seed as seed_module


class FakeDB:
    def __init__(self):
        self.deleted = []

    def delete(self, record):
        self.deleted.append(record)


def test_diagnostic_problem_and_topic_cleanup_is_narrowly_scoped():
    diagnostic_problem = SimpleNamespace(slug="c54d-diagnostic")
    unrelated_problem = SimpleNamespace(slug="unrelated-problem")
    diagnostic_topic = SimpleNamespace(slug="c54d-diagnostic")
    unrelated_topic = SimpleNamespace(slug="unrelated-topic")
    canonical_topic = SimpleNamespace(slug="arrays")

    db = FakeDB()
    removed_problems = seed_module._remove_obsolete_problems(
        db,
        [diagnostic_problem, unrelated_problem],
        dry_run=False,
    )
    removed_topics = seed_module._remove_obsolete_topics(
        db,
        [diagnostic_topic, unrelated_topic, canonical_topic],
        dry_run=False,
    )

    assert removed_problems == {"c54d-diagnostic"}
    assert removed_topics == {"c54d-diagnostic"}
    assert db.deleted == [diagnostic_problem, diagnostic_topic]


def test_diagnostic_cleanup_is_dry_run_only():
    db = FakeDB()
    diagnostic_problem = SimpleNamespace(slug="c54d-diagnostic")
    diagnostic_topic = SimpleNamespace(slug="c54d-diagnostic")

    seed_module._remove_obsolete_problems(
        db,
        [diagnostic_problem],
        dry_run=True,
    )
    seed_module._remove_obsolete_topics(
        db,
        [diagnostic_topic],
        dry_run=True,
    )

    assert db.deleted == []


def test_seed_case_identity_excludes_configuration_flags():
    canonical = seed_module.SeedCase(
        case_key="H1",
        input="1 2 3",
        expected_output="6",
        run_enabled=True,
        submit_enabled=True,
        is_sample=False,
        display_order=2,
    )

    changed_configuration = replace(
        canonical,
        run_enabled=False,
        submit_enabled=True,
        is_sample=False,
    )

    changed_content = replace(
        canonical,
        input="9 9 9",
        expected_output="27",
    )

    assert seed_module._case_identity(canonical) == (2,)
    assert (
        seed_module._case_identity(canonical)
        == seed_module._case_identity(changed_configuration)
    )
    assert seed_module._case_identity(canonical) != seed_module._case_identity(
        replace(canonical, display_order=3)
    )
    assert seed_module._case_identity(canonical) == seed_module._case_identity(
        changed_content
    )


def test_canonical_payload_has_expected_shape_and_starters():
    topics, problems = seed_module.load_canonical_data()

    assert len(topics) == 5
    assert len(problems) == 25
    assert {topic.name for topic in topics} == {
        "Arrays",
        "Strings",
        "Linked List",
        "Stack & Queue",
        "Dynamic Programming",
    }
    assert all(len(problem.tags) == 3 for problem in problems)
    assert all(len(problem.examples) == 2 for problem in problems)
    assert all(len(problem.cases) == 10 for problem in problems)
    assert sum(len(problem.cases) for problem in problems) == 250
    assert all(problem.python_starter.find("TODO") >= 0 for problem in problems)
    assert all(problem.cpp_starter.find("TODO") >= 0 for problem in problems)

    for problem in problems:
        assert [case.case_key for case in problem.cases] == [
            "P1",
            "P2",
            "H1",
            "H2",
            "H3",
            "H4",
            "H5",
            "H6",
            "H7",
            "H8",
        ]
        assert [case.display_order for case in problem.cases] == list(range(1, 11))
        assert all(case.submit_enabled for case in problem.cases)
        assert [case.run_enabled for case in problem.cases[:2]] == [True, True]
        assert not any(case.run_enabled for case in problem.cases[2:])
        assert [case.is_sample for case in problem.cases[:2]] == [True, True]
        assert not any(case.is_sample for case in problem.cases[2:])
