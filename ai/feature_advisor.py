"""
Feature Engineering Advisor powered by LLM.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class FeatureEngineeringAdvisor:
    """Uses the Baseten LLM client to suggest feature engineering ideas."""

    def __init__(self, llm_client: Any) -> None:
        self.llm_client = llm_client

    def generate_suggestions(
        self,
        dataset_info: Dict[str, Any],
        outlier_summary: Optional[List[Dict[str, Any]]] = None,
        erd_summary: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        columns = dataset_info.get("columns", [])
        dtypes = dataset_info.get("dtypes", {})
        shape = dataset_info.get("shape")

        outlier_text = ""
        if outlier_summary:
            formatted = [
                f"{item['column']}: {item['outlier_count']} outliers (~{item['percentage']:.1f}%)"
                for item in outlier_summary[:5]
            ]
            outlier_text = "\n- ".join(formatted)

        erd_text = ""
        if erd_summary:
            erd_text = "\n- ".join(erd_summary[:8])

        context = f"""
أنت خبير Feature Engineering. نريد أفكارًا عملية لبناء ميزات جديدة تساعد النماذج في التعلم من البيانات.

معلومات عن البيانات:
- عدد الصفوف: {shape[0] if shape else 'غير معروف'}
- عدد الأعمدة: {shape[1] if shape else 'غير معروف'}
- الأعمدة المتاحة: {', '.join(columns)}
- نوع كل عمود:
{chr(10).join([f"- {col}: {dtype}" for col, dtype in dtypes.items()])}

ملخص outliers (إن وجد):
- {outlier_text or 'لا يوجد Outliers ملحوظة'}

ملخص العلاقات (ERD):
- {erd_text or 'لا توجد علاقات قوية متاحة'}

المطلوب:
1. اقترح 5-7 أفكار Feature Engineering محددة (معادلات، نسب، تحويلات وقت/تواريخ، تجميعات، Encoding ...)
2. صنّفها إلى (إحصائية، زمنية، تفاعلية، Encoding، استخراج نصي ...) إن أمكن
3. وضّح سبب أهمية كل فكرة وكيف تساعد النماذج
4. نبّه إلى أي خطوة تتطلب معالجة إضافية (مثل normalization أو log transform)

اكتب الإجابة بالعربية وبشكل واضح.
"""

        suggestions_text = self.llm_client.get_full_response(
            messages=[{"role": "user", "content": context}],
            max_tokens=1200,
            temperature=0.4,
        )

        return {
            "text": suggestions_text.strip(),
            "columns_used": columns,
        }

