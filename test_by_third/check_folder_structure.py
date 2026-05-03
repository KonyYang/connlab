"""检查生成的文件夹结构和证据放置。"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.storage.database import SessionLocal
from backend.infrastructure.storage.models import ProjectFolderRecordModel


def check_folder_structure(project_id: str) -> bool:
    """检查项目的文件夹结构和证据放置。"""
    session = SessionLocal()
    try:
        print(f"\n{'='*60}")
        print(f"检查文件夹结构: {project_id}")
        print(f"{'='*60}\n")

        # 1. 获取文件夹记录
        folders = session.query(ProjectFolderRecordModel).filter_by(project_id=project_id).all()
        if not folders:
            print("❌ 项目文件夹记录未找到")
            return False
        
        print(f"✅ 找到 {len(folders)} 个文件夹记录\n")
        
        # 使用最新的文件夹
        latest_folder = folders[-1]
        folder_path = Path(latest_folder.folder_path)
        
        print(f"📁 最新文件夹路径: {folder_path}")
        print()

        # 2. 检查文件夹是否存在
        if not folder_path.exists():
            print(f"❌ 文件夹不存在: {folder_path}")
            return False
        
        print(f"✅ 文件夹存在于磁盘")
        print()

        # 3. 列出文件夹结构
        print("📂 文件夹结构:")
        print("-" * 60)
        
        expected_subdirs = [
            "E-mail",
            "Submitted Material",
            "Photos",
        ]
        
        found_subdirs = []
        for item in folder_path.iterdir():
            if item.is_dir():
                found_subdirs.append(item.name)
                indent = "   "
                print(f"{indent}📁 {item.name}/")
                
                # 列出子目录内容（最多 5 个文件）
                try:
                    files = list(item.rglob("*"))[:5]
                    for f in files:
                        if f.is_file():
                            rel_path = f.relative_to(folder_path)
                            size_kb = f.stat().st_size / 1024
                            print(f"{indent}   📄 {rel_path} ({size_kb:.1f} KB)")
                    if len(list(item.rglob("*"))) > 5:
                        print(f"{indent}   ... (更多文件)")
                except Exception as e:
                    print(f"{indent}   ⚠️  无法读取内容: {e}")
        
        print()

        # 4. 检查预期的证据子目录
        print("🔍 预期证据目录检查:")
        print("-" * 60)
        
        all_checks_passed = True
        for subdir in expected_subdirs:
            subdir_path = folder_path / subdir
            if subdir_path.exists() and subdir_path.is_dir():
                file_count = len(list(subdir_path.rglob("*")))
                print(f"   ✅ {subdir}/ (包含 {file_count} 个项目)")
            else:
                print(f"   ⚠️  {subdir}/ (不存在或为空)")
                # 这不是致命错误，因为可能没有相关证据
        
        print()

        # 5. 检查源文件是否仍然存在（不应被删除）
        print("🔒 源文件完整性检查:")
        print("-" * 60)
        
        # 这里需要知道 intake package ID，暂时跳过详细检查
        print("   ℹ️  源文件检查需要 package_id，请使用 verify_entities.py 验证")
        print()

        # 6. 总结
        print(f"{'='*60}")
        print("验证完成")
        print(f"{'='*60}")
        
        if folder_path.exists():
            print("✅ 文件夹结构存在且可访问")
            print(f"   路径: {folder_path}")
            print(f"   子目录数: {len(found_subdirs)}")
            return True
        else:
            print("❌ 文件夹不存在")
            return False

    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="检查文件夹结构")
    parser.add_argument("--project-id", required=True, help="项目 ID")
    args = parser.parse_args()

    success = check_folder_structure(args.project_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
