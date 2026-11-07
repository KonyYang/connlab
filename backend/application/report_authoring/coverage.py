"""Matrix evidence coverage, separate from file generation and engineering approval."""
from collections import Counter
from dataclasses import asdict


def report_coverage(state, context, *, applied_result_ids, result_errors, projected_results=()):
    applied = set(applied_result_ids)
    rows = []
    for step in context["steps"]:
        results = [item for item in (*state.results, *projected_results) if all(
            item["target"][key] == step[key] for key in ("group_id", "row_id", "step_token"))]
        valid = [item for item in results if item["result_id"] not in result_errors]
        active = [item for item in valid if item["result_id"] in applied]
        # The working copy records the operator's selection. Historical alternatives
        # remain available, but do not make a valid applied choice ambiguous again.
        relevant = active or valid
        reasons = []
        status = "missing"
        if results:
            if not active:
                reasons.extend(dict.fromkeys(result_errors[item["result_id"]]
                                             for item in results if item["result_id"] in result_errors))
            if not relevant:
                status = "needs_review"
            elif len(relevant) > 1:
                status = "needs_review"
                reasons.append("Multiple confirmed results address this step. Choose the applicable evidence before assembly.")
            else:
                result = relevant[0]
                if result['data'].get('missing') or result['data'].get('selection_confirmed') is False:
                    status = 'needs_review'
                    reasons.append('Source measurements are incomplete or their stage/quantity mapping is not confirmed.')
                elif result["outcome"] == "pending":
                    status = "needs_review"
                    reasons.append("Measurements are available for a review copy; engineering acceptance is still pending.")
                elif result["outcome"] == "not_applicable":
                    status = "not_applicable"
                else:
                    status = "ready"
                if result["kind"] == "temperature" and not result["data"].get("sample_ids"):
                    status = "needs_review"
                    reasons.append("Confirm the specimen identities; channel groups alone are not sample IDs.")
        else:
            reasons.append("No confirmed result is retained for this Matrix step.")
        ids = [item["result_id"] for item in results]
        rows.append({**step, "status": status, "reasons": reasons, "result_ids": ids,
                     "usable_result_ids": [item["result_id"] for item in valid],
                     "applied_result_ids": [item["result_id"] for item in active]})
    pending = [asdict(item) for item in state.mappings if item.status != "confirmed"]
    # Ready is an assembly state, not Pass. Even a checked Fail can be reported.
    complete = bool(rows) and not pending and all(
        row["status"] in {"ready", "not_applicable"} and row["applied_result_ids"] for row in rows)
    return {"matrix_id": context["matrix_id"], "has_confirmed_matrix": bool(context["matrix_id"]),
            "rows": rows, "pending_mappings": pending, "complete": complete,
            "counts": dict(Counter(row["status"] for row in rows)),
            "note": "Evidence coverage is not formal approval or report release."}
