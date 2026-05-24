  范围只包括：

  - 删除无用占位符按钮。
  - 增加附件下载 API。
  - 前端 Download 按钮可点击。
  - 测试和文档更新。

  不要顺手做批量下载、打开所在文件夹、下载源邮件、权限系统、下载审计等扩展。

  实施步骤

  1. 后端新增下载用例服务
     建议新建或扩展 application 层服务，例如：

     backend/application/intake_asset_download_service.py

     定义：
      - IntakeAssetDownloadNotFoundError
      - IntakeAssetDownloadError
      - DownloadableIntakeAsset dataclass:
          - path: Path
          - filename: str
          - media_type: str | None

     服务逻辑：
      - 用 IntakeAssetRepository.get(asset_id) 查资产。
      - asset 不存在：404。
      - asset.stored_path 不存在或不是文件：400 或 404，建议 404/400 均可，但错
        误文案要清晰。
      - 返回原始文件名 asset.original_name，不要用内部存储文件名。
      - media_type 用 asset.mime_type，为空时可 fallback 到 application/octet-
        stream。
  2. 在依赖注入里注册服务
     修改 backend/api/dependencies.py：
      - import IntakeAssetDownloadService
      - 增加 get_intake_asset_download_service(session=Depends(get_session))
      - 注入 IntakeAssetRepository(session)
  3. 增加 API route
     修改 backend/api/routes_intake.py：
      - import FileResponse
      - 增加：

     GET /api/intake-assets/{asset_id}/download

     返回：
      - FileResponse(path=download.path, filename=download.filename,
        media_type=download.media_type)
      - 捕获 not found/error 转成 HTTPException

     注意：
      - 不要把 stored_path 放进 JSON。
      - filename 用原始附件名，让浏览器下载显示业务文件名。

  4. 前端 API client 增加 URL helper
     因为下载不是 JSON，不建议走 requestJson。

     在 frontend/src/api/client.ts 增加：

     export function intakeAssetDownloadUrl(assetId: string): string {
       return `${API_BASE}/api/intake-assets/${encodeURIComponent(assetId)}/
  download`;
     }

     如果 API_BASE 当前是模块内 const，可以直接在同文件新增 helper。

  5. 修改 AttachmentPreviewPanel.tsx
     当前 AttachmentPreviewActions() 没有 asset 参数，而且两个按钮都 disabled。

     改成：
      - AttachmentPreviewActions({ asset })
      - 删除右侧 columns icon button。
      - Download 改为 <a> 或 button。

     推荐用 <a>：

     <a
       className="secondary-action ui-secondary-action"
       href={intakeAssetDownloadUrl(asset.asset_id)}
       download={asset.original_name}
     >
       Download
     </a>

     然后所有调用位置传入 asset 或 preview.metadata.asset_id。更简单是从
     preview.metadata 构造下载 URL，但按钮还需要原文件名，
     preview.metadata.original_name 已经有。

  6. 样式清理
     修改 frontend/src/intake-inbox.css：
      - .details-actions 保留 flex。
      - 删除或不再依赖 .toolbar-button.toolbar-icon-button 在此处的占位用途。
      - .secondary-action 如果现在只写 button，也要支持 <a>：
          - display: inline-grid
      - 断言 200
      - 断言 response content 等于原文件 bytes
      - 断言 content-disposition 包含原始文件名
      - missing asset 返回 404
      - stored file missing 返回清晰错误

     前端静态测试加在 tests/unit/test_frontend_shell_files.py：
      - 断言 intakeAssetDownloadUrl
      - 断言 /download
      - 断言 AttachmentPreviewActions
      - 断言没有 toolbar-icon-button 或 columns 出现在
        AttachmentPreviewPanel.tsx 的 actions 区域
      - 断言 Download 不再 disabled
  8. 验证命令
     运行：

     py -m pytest tests\integration\test_msg_package_intake_api.py
  tests\unit\test_frontend_shell_files.py -q
     npm run build
     py -m pytest -q

  9. 文档更新
     需要更新：
      - docs/task_board.md
      - docs/archive/historical_plans/current_session_state.md

     记录：
      - 下载通过 API 返回已存储 intake asset。
      - 不暴露本地 stored_path。
      - 删除无功能占位按钮。
      - 验证结果。