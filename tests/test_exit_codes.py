from redloop.regressions import suite_exit_code


def s(red=0, errors=0):
    return {"red": red, "errors": errors}


def test_pass():
    assert suite_exit_code(s()) == 0


def test_vulnerability_wins_over_infra():
    assert suite_exit_code(s(red=1, errors=2)) == 1


def test_infra_only_is_unknown_exit_3():
    assert suite_exit_code(s(errors=1)) == 3


def test_pixelinject_stub_skips_offline(monkeypatch):
    from redloop.scenarios.visual import pixelinject_stub as p
    monkeypatch.delenv("MUSE_API_KEY", raising=False)
    assert p.SCENARIO["status"] == "stub" and not p.available()
