from pyjj.config import PyjjConfig, handle_exception


def test_handle_exception_decorator(capsys):
    @handle_exception
    def dummy_os():
        raise OSError("dummy os error")

    dummy_os()
    captured = capsys.readouterr()
    assert captured.out == "Failed to open config file: dummy os error\n"

    @handle_exception
    def dummy_val():
        raise ValueError("dummy value error")

    dummy_val()
    captured = capsys.readouterr()
    assert captured.out == "Unexpected error: dummy value error\n"


def test_parse_config(tmp_path, capsys):
    config = PyjjConfig()

    # happy content
    good_content = """division: must be test"""
    tmp_file = tmp_path / "config.yaml"
    tmp_file.write_text(good_content)

    config.path = tmp_file
    config.parse()
    assert config.division == "must be test"

    tmp_file.unlink()

    # bad content
    ill_content = """x$@&*(djkw!@()GL"""
    tmp_file.write_text(ill_content)

    config.path = tmp_file
    config.parse()
    captured = capsys.readouterr()
    assert captured.out.startswith("Falied to parse config file: ")


def test_update_config(tmp_path, capsys):
    config = PyjjConfig()
    tmp_file = tmp_path / "config.yaml"
    config.path = tmp_file

    config.update(name="test_name", environment="test_env")
    assert config.name == "test_name"
    assert config.environment == "test_env"

    tmp_file.unlink()
    del config.name
    del config.environment

    config.path = "$%^@#@&*)///"
    config.update(name="test_name", environment="test_env")
    captured = capsys.readouterr()
    assert captured.out.startswith("Falied to serialize config file:")
