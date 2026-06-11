# modules/skill_manager.py
import os
from pathlib import Path
from typing import Dict, List, Optional

class Skill:
    def __init__(self, name: str, folder_path: str):
        self.name = name
        self.folder = Path(folder_path)
        self.description = ""
        self.prompt = ""
        self.commands = []
        self._load()
    
    def _load(self):
        skill_file = self.folder / "SKILL.md"
        if not skill_file.exists():
            return
        content = skill_file.read_text(encoding='utf-8')
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ':' in line:
                        key, val = line.split(':', 1)
                        key = key.strip().lower()
                        val = val.strip()
                        if key == 'description':
                            self.description = val
                        elif key == 'commands':
                            self.commands = [c.strip() for c in val.split(',')]
                self.prompt = parts[2].strip()
            else:
                self.prompt = content
        else:
            self.prompt = content
    
    def get_prompt(self) -> str:
        return f"## Skill: {self.name}\n{self.description}\n\n{self.prompt}"

class SkillManager:
    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            skills_dir = os.path.expanduser("~/.nexcorix/skills")
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.skills: Dict[str, Skill] = {}
        self._load_all()
    
    def _load_all(self):
        self.skills.clear()
        for item in self.skills_dir.iterdir():
            if item.is_dir():
                skill = Skill(item.name, str(item))
                self.skills[item.name] = skill
    
    def get(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)
    
    def list(self) -> List[str]:
        return list(self.skills.keys())
    
    def create(self, name: str, description: str = "", commands: list = None) -> bool:
        skill_dir = self.skills_dir / name
        if skill_dir.exists():
            return False
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        frontmatter = f"""---
description: {description}
commands: {', '.join(commands) if commands else ''}
---

# {name} Skill

Write your instructions here.
"""
        skill_file.write_text(frontmatter)
        self._load_all()
        return True
    
    def get_all_prompts(self) -> str:
        if not self.skills:
            return "No skills installed."
        prompts = ["## Available Skills (load with skill_load tool)\n"]
        for name, skill in self.skills.items():
            prompts.append(f"- **{name}**: {skill.description or 'no description'}")
        return "\n".join(prompts)
