"""验证项目相关实体是否正确创建和关联。"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.storage.database import SessionLocal
from backend.infrastructure.storage.models import (
    ApplicationFormModel,
    FileAssetModel,
    IntakeCaseModel,
    ProjectModel,
    SampleInfoModel,
)


def verify_project_entities(project_id: str) -> bool:
    """验证项目的所有相关实体。"""
    session = SessionLocal()
    try:
        print(f"\n{'='*60}")
        print(f"验证项目实体: {project_id}")
        print(f"{'='*60}\n")

        # 1. 验证 Project
        project = session.query(ProjectModel).filter_by(project_id=project_id).first()
        if not project:
            print("❌ Project 未找到")
            return False
        
        print(f"✅ Project 存在")
        print(f"   - project_no: {project.project_no}")
        print(f"   - product_name: {project.product_name}")
        print(f"   - requestor: {project.requestor}")
        print(f"   - status: {project.status}")
        print()

        # 2. 验证 ApplicationForm
        forms = session.query(ApplicationFormModel).filter_by(project_id=project_id).all()
        if not forms:
            print("⚠️  ApplicationForm 未找到（可能尚未解析表单）")
        else:
            print(f"✅ ApplicationForm 存在 ({len(forms)} 个)")
            for i, form in enumerate(forms, 1):
                print(f"   [{i}] form_id: {form.form_id}")
                print(f"       form_no: {form.form_no}, revision: {form.revision}")
                print(f"       requester: {form.requester}")
                print(f"       email: {form.email}")
                print(f"       requested_testing: {form.requested_testing[:50] if form.requested_testing else 'N/A'}...")
            print()

        # 3. 验证 SampleInfo
        samples = session.query(SampleInfoModel).filter_by(project_id=project_id).all()
        if not samples:
            print("⚠️  SampleInfo 未找到")
        else:
            print(f"✅ SampleInfo 存在 ({len(samples)} 个)")
            for i, sample in enumerate(samples, 1):
                print(f"   [{i}] sample_id: {sample.sample_id}")
                print(f"       product_name: {sample.product_name}")
                print(f"       part_number: {sample.part_number}")
                print(f"       quantity: {sample.quantity}")
            print()

        # 4. 验证 FileAsset
        assets = session.query(FileAssetModel).filter_by(project_id=project_id).all()
        if not assets:
            print("⚠️  FileAsset 未找到")
        else:
            print(f"✅ FileAsset 存在 ({len(assets)} 个)")
            for i, asset in enumerate(assets, 1):
                print(f"   [{i}] asset_id: {asset.asset_id}")
                print(f"       type: {asset.asset_type}")
                print(f"       original_name: {asset.original_name}")
                print(f"       path: {asset.path}")
                # 检查文件是否存在
                if Path(asset.path).exists():
                    print(f"       ✅ 文件存在")
                else:
                    print(f"       ❌ 文件不存在")
            print()

        # 5. 验证 IntakeCase（如果有）
        cases = session.query(IntakeCaseModel).filter_by(confirmed_project_id=project_id).all()
        if not cases:
            print("ℹ️  IntakeCase 未关联到此项目（可能是直接上传的表单）")
        else:
            print(f"✅ IntakeCase 关联 ({len(cases)} 个)")
            for i, case in enumerate(cases, 1):
                print(f"   [{i}] case_id: {case.case_id}")
                print(f"       package_id: {case.package_id}")
                print(f"       status: {case.status}")
                print(f"       selected_form_asset_id: {case.selected_form_asset_id}")
            print()

        # 总结
        print(f"{'='*60}")
        print("验证完成")
        print(f"{'='*60}")
        
        has_project = project is not None
        has_form = len(forms) > 0
        has_sample = len(samples) > 0
        has_asset = len(assets) > 0
        
        if has_project and has_form and has_sample and has_asset:
            print("✅ 所有核心实体都存在且关联正确")
            return True
        else:
            print("⚠️  部分实体缺失，请检查上述输出")
            return False

    except Exception as e:
        print(f"❌ 验证过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="验证项目实体")
    parser.add_argument("--project-id", required=True, help="项目 ID")
    args = parser.parse_args()

    success = verify_project_entities(args.project_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
