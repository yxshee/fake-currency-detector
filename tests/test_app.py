from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "app.py"


def test_app_analyses_the_default_sample_without_errors():
    app = AppTest.from_file(str(APP), default_timeout=120).run()
    assert not app.exception
    assert app.title[0].value == "Fake Currency Detector"
    shown = " ".join(element.value for element in list(app.success) + list(app.error))
    assert "Verdict:" in shown
    assert any("/ 10 features passed" in header.value for header in app.subheader)


def test_every_committed_note_can_be_selected():
    app = AppTest.from_file(str(APP), default_timeout=120).run()
    options = app.selectbox[0].options
    assert len(options) == 31
    app.selectbox[0].select(options[-1]).run()
    assert not app.exception
