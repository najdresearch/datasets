"""Generate original synthetic development cases. No customer or employer data."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples/arabic-support-routing-v1"


def generate(output=OUT):
    prompts = [
        ("billing", "ظهر مبلغ العملية مرتين في فاتورتي، أحتاج مراجعة الفاتورة."),
        ("billing", "أبغى نسخة من فاتورتي الضريبية للطلب الأخير."),
        ("delivery", "طلبي متأخر، وين وصلت الشحنة؟"),
        ("delivery", "أبي أعدل عنوان توصيل الطلب قبل ما يطلع من المستودع."),
        ("returns", "وصلني المنتج وأبغى أرجعه، كيف أبدأ طلب الإرجاع؟"),
        ("returns", "المقاس ما ناسبني وأحتاج أستبدله."),
        ("handoff", "أحتاج أكلم موظف خدمة العملاء مباشرة."),
        ("handoff", "الموضوع ما انحل، حولني إلى المشرف لو سمحت."),
    ]
    cases = [
        {"id": f"support-dev-{i:02}", "prompt": prompt, "label": label}
        for i, (label, prompt) in enumerate(prompts, 1)
    ]
    raw = "".join(json.dumps(c, ensure_ascii=False, sort_keys=True) + "\n" for c in cases).encode()
    sha = hashlib.sha256(raw).hexdigest()
    manifest = {
        "schema_version": "1.0.0",
        "kind": "dataset_manifest",
        "id": "arabic-support-routing",
        "version": "1.0.0",
        "description": "Eight original synthetic Arabic support-routing development cases.",
        "split": "development",
        "source": {
            "url": "https://github.com/najdresearch/datasets",
            "revision": "support-template-v1",
            "method": "Deterministic original templates; no customer data.",
        },
        "rights": {
            "license": "CC0-1.0",
            "evidence_url": "https://github.com/najdresearch/datasets/blob/main/examples/arabic-support-routing-v1/README.md",
        },
        "cases": {"path": "cases.jsonl", "sha256": sha, "count": len(cases)},
        "case_ids": [c["id"] for c in cases],
        "created_at": "2026-09-27T00:00:00Z",
    }
    pack = {
        "schema_version": "1.0.0",
        "kind": "task_pack",
        "id": "arabic-support-routing",
        "version": "1.0.0",
        "description": "Route a customer message to a queue; this does not test support quality.",
        "dataset": {"id": manifest["id"], "version": manifest["version"], "cases_sha256": sha},
        "task_type": "classification",
        "labels": ["billing", "delivery", "returns", "handoff"],
        "system_prompt": (
            "صنف رسالة العميل إلى billing للفواتير، delivery للتوصيل، "
            "returns للإرجاع أو الاستبدال، handoff لطلب موظف أو مشرف. "
            "أعد JSON فقط بمفتاح label وقيمة واحدة من هذه القيم."
        ),
        "output_format": "json_label",
        "harness": {"id": "single-turn", "version": "1"},
        "scorer": {
            "id": "exact-label",
            "version": "1",
            "metrics": ["accuracy", "macro_f1", "confusion_matrix", "latency_ms"],
        },
        "budget": {"max_tokens": 128, "timeout_seconds": 30, "max_attempts": 1},
        "baseline": {
            "strategy": "always-billing",
            "description": "Constant billing predicts 2/8 correctly (25%).",
        },
        "uncertainty": {
            "method": "wilson-95",
            "limitations": "Eight public development cases; not a held-out test or model ranking.",
        },
        "stop_rules": [
            "Stop if dataset hash or case IDs differ.",
            "Count invalid output and provider failures in the accuracy denominator.",
            "Do not publish this development fixture as a model benchmark.",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "cases.jsonl").write_bytes(raw)
    for name, value in [("dataset-manifest", manifest), ("task-pack", pack)]:
        (output / (name + ".json")).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        )


if __name__ == "__main__":
    generate()
