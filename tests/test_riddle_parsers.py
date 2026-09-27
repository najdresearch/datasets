from najd_datasets.riddle_parsers import html_to_lines, normalized, parse_almrsal_riddles


def test_html_parser_ignores_script_content():
    assert "secret" not in "\n".join(html_to_lines("<script>secret</script><p>visible</p>"))


def test_labelled_paragraphs_retain_question_and_answer():
    html = "<p>اللغز: ما مجموع واحد وواحد؟</p><p>الإجابة: اثنان</p>"
    assert parse_almrsal_riddles(html) == [("ما مجموع واحد وواحد؟", "اثنان")]


def test_historical_normalization_removes_diacritics():
    assert normalized("أَهْلاً") == normalized("اهلا")
