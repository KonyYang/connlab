"""Read-only recovery fence; callers already own the canonical project lock."""

def require_project_file_generation_clear(journal, project_id):
    state = journal.read(project_id)
    if state and state["status"] != "completed":
        raise ValueError("Project file generation is unfinished. Resume it before changing project data or files.")
