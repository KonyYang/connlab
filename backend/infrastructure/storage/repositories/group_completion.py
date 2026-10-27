from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select
from backend.infrastructure.storage.models_group_completion import GroupCompletionEventModel


class GroupCompletionRepository:
    def __init__(self, session):
        self.session = session

    def list_by_project(self, project_id):
        return list(self.session.scalars(select(GroupCompletionEventModel).where(
            GroupCompletionEventModel.project_id == project_id
        ).order_by(GroupCompletionEventModel.recorded_at.desc(), GroupCompletionEventModel.event_id.desc())))

    def save(self, project_id, group_lineage, group_key, matrix_revision, signature, completed, completed_at):
        self.session.add(GroupCompletionEventModel(event_id=uuid4().hex, project_id=project_id,
                         group_lineage=group_lineage, group_key=group_key, matrix_revision=matrix_revision, signature=signature, completed=completed,
                         completed_at=completed_at, recorded_at=datetime.now(timezone.utc).isoformat()))
        self.session.flush()
