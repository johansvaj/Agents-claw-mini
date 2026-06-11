import subprocess
import tempfile
import shutil
from pathlib import Path
from .skill_manager import SkillManager

class SkillMarketplace:
    def __init__(self, skill_manager: SkillManager):
        self.skill_mgr = skill_manager
    def install_from_github(self, repo_url: str) -> str:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                subprocess.run(["git", "clone", repo_url, tmp], check=True, capture_output=True)
                tmp_path = Path(tmp)
                for item in tmp_path.iterdir():
                    if item.is_dir() and (item / "SKILL.md").exists():
                        dest = self.skill_mgr.dir / item.name
                        if dest.exists():
                            return f"Skill {item.name} already exists."
                        shutil.copytree(item, dest)
                        self.skill_mgr._reload()
                        return f"Skill {item.name} installed."
                return "No valid skill found in repo."
        except Exception as e:
            return f"Install failed: {e}"
