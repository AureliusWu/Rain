"""Run all authoring checks; stop on the first failure."""
import subprocess
import sys


def main():
    for args in [
        ["-m", "unittest", "discover", "-s", "tests", "-v"],
        ["-m", "tools.route_validator", "--report", "reports/routes.json"],
        ["-m", "tools.story_lint"],
        ["-m", "tools.prompt_registry", "--check"],
        ["-m", "tools.asset_validator", "--report", "reports/assets.json"],
        ["-m", "tools.audio_validator", "--report", "reports/audio.json"],
        ["-m", "tools.image_process.import_asset", "--check"],
        ["-m", "tools.character_validator", "--report", "reports/characters.json"],
        ["-m", "tools.compile_story", "--check"],
        ["-m", "tools.compile_tests", "--check"],
    ]:
        subprocess.run([sys.executable, *args], check=True)


if __name__ == "__main__":
    main()
