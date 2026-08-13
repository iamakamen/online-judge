from dataclasses import replace

from scripts import seed as seed_module


def test_seed_case_identity_excludes_configuration_flags():
    canonical = seed_module.SeedCase(
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

    assert seed_module._case_identity(canonical) == (
        "1 2 3",
        "6",
        2,
    )
    assert (
        seed_module._case_identity(canonical)
        == seed_module._case_identity(changed_configuration)
    )
