# TASK_152 可执行方案（Standard / Equipment 只读模型）

## 0. 执行前声明（Anti-Skip）

- 当前 Phase：`Phase 10E - External resource settings and LTR workbook authority`
- 当前 Active Task：`TASK_152_STANDARD_AND_EQUIPMENT_RESOURCE_READ_MODELS`
- 允许原因：`docs/task_board.md` 已将 `TASK_151` 标记完成，并将 `TASK_152` 作为下一推荐任务（待批准后实施）。

---

## 1. 任务目标（Step 1）

1. 目标  
   为 `standard_record_excel` 和 `equipment_calibration_excel` 建立“可复用、只读、结构化”的读取模型与查询入口，避免后续功能重复做 ad hoc Excel 解析。

2. 输入数据  
   - Settings / External Resources 中已配置并可验证的 Excel 文件路径（`.xlsx` 主路径，保留 `.xls` 兼容边界）。
   - 查询参数（如关键字 query，必要时 sheet 过滤）。

3. 输出数据  
   - 标准记录结构化行（DTO）。
   - 设备校准结构化行（DTO）。
   - 业务可读的结构错误/读取错误（不泄露底层异常堆栈）。

4. 涉及模块  
   - `backend/application`（新增 read service）
   - `backend/infrastructure/office`（复用现有 `ExcelWorkbookGateway`，补充只读行提取能力）
   - `backend/api`（新增薄路由）
   - `tests/unit`、`tests/integration`（夹具与用例）

5. 不允许做什么  
   - 不实现写回 Excel  
   - 不实现报表生成/Matrix/设备校准流程  
   - 不跨层（API 直接操作 Office）  
   - 不引入与任务无关的新依赖

---

## 2. 设计方案（Step 2）

### 2.1 数据结构设计

- 新增应用层 DTO（只读）：
  - `StandardRecordRow`
    - `standard_code: str`
    - `test_item: str`
    - `sample_description: str | None`
    - `source_sheet: str`
  - `EquipmentCalibrationRow`
    - `equipment_id: str`
    - `equipment_name: str | None`
    - `calibration_due_date: str | None`
    - `source_sheet: str`

- 新增响应聚合：
  - `StandardRecordReadResult` / `EquipmentCalibrationReadResult`
    - `rows: list[...]`
    - `resource_path: str`
    - `matched_sheets: list[str]`

### 2.2 架构与依赖

```text
API route
  -> application read service
      -> office facade / excel gateway (read-only)
```

- API 只调 application service。
- application service 先读 external resource registry（路径/active/validation 状态），再走 office 只读适配器。
- infrastructure 仅做 XLSX 读取和基础结构解析，不包含业务过滤策略。

### 2.3 文件级改动清单（计划）

1. 新增 `backend/application/external_excel_read_service.py`
   - 负责：
     - 读取注册资源（`standard_record_excel` / `equipment_calibration_excel`）
     - 调用 office 只读读取
     - 转换为结构化 DTO
     - 提供简易 query 过滤（大小写不敏感 contains）

2. 更新 `backend/infrastructure/office/excel_workbook_gateway.py`
   - 增加只读“表头 + 数据行”提取函数（`read_tabular_rows` 级别）
   - 复用现有 `_read_xlsx_sheet_rows`，不引入写操作

3. 更新 `backend/infrastructure/office/office_facade.py`
   - 暴露新的只读表格读取入口（Facade 封装）

4. 新增 `backend/api/routes_external_excel_resources.py`
   - 拟提供：
     - `GET /api/external-resources/standard-record/rows`
     - `GET /api/external-resources/equipment-calibration/rows`
   - 参数：
     - `query: str | None = None`

5. 更新 `backend/api/main.py`
   - 注册新 router

6. 更新 `backend/api/dependencies.py`
   - 新增 read service 依赖工厂

7. 测试
   - 新增 `tests/unit/test_external_excel_read_service.py`
   - 新增 `tests/integration/test_external_excel_read_api.py`
   - 必要时补 `tests/unit/test_excel_workbook_gateway.py`（若当前无对应文件则放在服务测试里覆盖）

### 2.4 API/函数签名草案

- `ExternalExcelReadService.read_standard_records(query: str | None) -> StandardRecordReadResult`
- `ExternalExcelReadService.read_equipment_calibrations(query: str | None) -> EquipmentCalibrationReadResult`
- `OfficeFacade.read_excel_tabular_rows(...) -> ...`

---

## 3. 实施边界与风险

1. Excel 现实结构可能不一致  
   - 策略：基于已存在结构探针规则先验匹配，再做“首行表头 -> 行映射”。

2. `.xls` 兼容  
   - 本任务先保证 `.xlsx` 主路径稳定；`.xls` 若遇到读取限制，返回明确错误并引导转换或使用受支持路径。

3. 性能  
   - 默认按需读取，不做长期缓存，保证公共盘更新可见性。

---

## 4. 验证计划（Step 5/7）

执行命令（实现后）：

```powershell
py -m pytest tests\unit\test_excel_structure_probe.py tests\unit\test_external_resource_service.py -q
py -m pytest tests\unit\test_external_excel_read_service.py -q
py -m pytest tests\integration\test_external_resource_api.py tests\integration\test_external_excel_read_api.py -q
```

手工验证：

1. Settings 配置并激活 `standard_record_excel` 与 `equipment_calibration_excel`。
2. 调用两个读取 API（可带 query）。
3. 确认返回为结构化业务字段，且公共盘文件改动后下次调用可见。

---

## 5. 自检清单（对应 TASK_REVIEW_CHECKLIST）

- 分层：API → application → infrastructure，符合。  
- 范围：只读模型与查询，不做写入与报表，符合。  
- 设计：DTO 明确、复用现有 OfficeFacade，避免重复解析。  
- 质量：全量类型标注与 docstring，补单元与集成测试。  

---

## 6. 实施后停止点

- 完成 `TASK_152` 后仅更新 `docs/task_board.md` 到下一任务建议，停止并等待你确认，不自动进入 `TASK_153`。

