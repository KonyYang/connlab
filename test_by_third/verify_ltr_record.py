"""验证 LTR 记录和审计信息。"""

import argparse
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.storage.database import SessionLocal
from backend.infrastructure.storage.models import LtrRecordModel, ProjectModel


def verify_ltr_record(project_id: str) -> bool:
    """验证项目的 LTR 记录。"""
    session = SessionLocal()
    try:
        print(f"\n{'='*60}")
        print(f"验证 LTR 记录: {project_id}")
        print(f"{'='*60}\n")

        # 1. 验证项目状态
        project = session.query(ProjectModel).filter_by(project_id=project_id).first()
        if not project:
            print("❌ Project 未找到")
            return False
        
        print(f"📋 项目状态: {project.status}")
        print()

        # 2. 验证 LTR 记录
        ltrs = session.query(LtrRecordModel).filter_by(project_id=project_id).all()
        if not ltrs:
            print("❌ LTR 记录未找到")
            print(f"   项目状态为 '{project.status}'，但无 LTR 记录")
            return False
        
        print(f"✅ LTR 记录存在 ({len(ltrs)} 个)")
        for i, ltr in enumerate(ltrs, 1):
            print(f"\n   [{i}] LTR 详情:")
            print(f"       ltr_id: {ltr.ltr_id}")
            print(f"       ltr_number: {ltr.ltr_number}")
            print(f"       status: {ltr.status}")
            print(f"       registered_on: {ltr.registered_on}")
            print(f"       requested_by: {ltr.requested_by or 'N/A'}")
            print(f"       requested_date: {ltr.requested_date or 'N/A'}")
            
            # 检查审计笔记
            if ltr.notes:
                print(f"       notes:")
                try:
                    # 尝试解析 JSON 格式的笔记
                    notes_data = json.loads(ltr.notes)
                    for key, value in notes_data.items():
                        print(f"         - {key}: {value}")
                except (json.JSONDecodeError, AttributeError):
                    # 如果不是 JSON，直接显示
                    print(f"         {ltr.notes}")
            else:
                print(f"       notes: (无)")
        
        print()

        # 3. 验证项目状态与 LTR 的一致性
        expected_status = "ltr_registered"
        if project.status != expected_status:
            print(f"⚠️  项目状态不一致")
            print(f"   期望: {expected_status}")
            print(f"   实际: {project.status}")
        else:
            print(f"✅ 项目状态正确: {project.status}")
        
        print()

        # 4. 总结
        print(f"{'='*60}")
        print("验证完成")
        print(f"{'='*60}")
        
        has_ltr = len(ltrs) > 0
        status_correct = project.status == expected_status
        
        if has_ltr and status_correct:
            print("✅ LTR 记录完整且状态一致")
            return True
        else:
            print("⚠️  存在问题，请检查上述输出")
            return False

    except Exception as e:
        print(f"❌ 验证过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="验证 LTR 记录")
    parser.add_argument("--project-id", required=True, help="项目 ID")
    args = parser.parse_args()

    success = verify_ltr_record(args.project_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
