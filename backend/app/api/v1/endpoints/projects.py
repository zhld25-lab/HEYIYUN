from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_permission
from app.core.permissions import (
    PERM_PROJECT_CREATE,
    PERM_PROJECT_DELETE,
    PERM_PROJECT_UPDATE,
    PERM_PROJECT_VIEW,
)
from app.crud.crud_project import crud_project
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import PageData, ResponseModel
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services import audit_service, project_service
from app.services.permission_service import mask_project_dict

router = APIRouter(prefix="/projects", tags=["projects"])

RESOURCE = "project"


def _serialize(project, user: User) -> ProjectOut:
    data = ProjectOut.model_validate(project).model_dump()
    data = mask_project_dict(data, user)
    return ProjectOut.model_validate(data)


@router.get("", response_model=ResponseModel[PageData[ProjectOut]])
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    project_name: str | None = None,
    project_code: str | None = None,
    project_type: str | None = None,
    voltage_level: str | None = None,
    project_status: str | None = None,
    risk_level: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_VIEW)),
) -> ResponseModel[PageData[ProjectOut]]:
    items, total = crud_project.list_filtered(
        db,
        skip=(page - 1) * page_size,
        limit=page_size,
        project_name=project_name,
        project_code=project_code,
        project_type=project_type,
        voltage_level=voltage_level,
        project_status=project_status,
        risk_level=risk_level,
    )
    data = PageData(
        items=[_serialize(p, current_user) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ResponseModel(data=data)


@router.post("", response_model=ResponseModel[ProjectOut])
def create_project(
    payload: ProjectCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_CREATE)),
) -> ResponseModel[ProjectOut]:
    if crud_project.get_by_code(db, payload.project_code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="项目编号已存在")
    project = project_service.create_project_obj(payload)
    project = crud_project.create(db, project)
    audit_service.record(
        db,
        user=current_user,
        action="CREATE",
        resource_type=RESOURCE,
        resource_id=project.id,
        detail={"project_code": project.project_code, "project_name": project.project_name},
        ip_address=request.client.host if request.client else None,
    )
    return ResponseModel(data=_serialize(project, current_user), message="项目创建成功")


@router.get("/{project_id}", response_model=ResponseModel[ProjectOut])
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_VIEW)),
) -> ResponseModel[ProjectOut]:
    project = crud_project.get(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return ResponseModel(data=_serialize(project, current_user))


@router.get("/{project_id}/overview", response_model=ResponseModel[ProjectOut])
def project_overview(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_VIEW)),
) -> ResponseModel[ProjectOut]:
    # Phase 2: overview returns the masked base project. Related modules
    # (contracts, costs, risks ...) are placeholders for later phases.
    project = crud_project.get(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return ResponseModel(data=_serialize(project, current_user))


@router.put("/{project_id}", response_model=ResponseModel[ProjectOut])
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_UPDATE)),
) -> ResponseModel[ProjectOut]:
    project = crud_project.get(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    project_service.apply_update(project, payload)
    db.commit()
    db.refresh(project)
    audit_service.record(
        db,
        user=current_user,
        action="UPDATE",
        resource_type=RESOURCE,
        resource_id=project.id,
        detail=payload.model_dump(exclude_unset=True),
        ip_address=request.client.host if request.client else None,
    )
    return ResponseModel(data=_serialize(project, current_user), message="项目更新成功")


@router.delete("/{project_id}", response_model=ResponseModel[None])
def delete_project(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_PROJECT_DELETE)),
) -> ResponseModel[None]:
    project = crud_project.get(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    code = project.project_code
    crud_project.remove(db, project)
    audit_service.record(
        db,
        user=current_user,
        action="DELETE",
        resource_type=RESOURCE,
        resource_id=project_id,
        detail={"project_code": code},
        ip_address=request.client.host if request.client else None,
    )
    return ResponseModel(message="项目删除成功")
