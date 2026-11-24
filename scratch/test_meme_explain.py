import os
from src.explainability.openai_service import OpenAIExplainabilityService

svc = OpenAIExplainabilityService()
tokens = ['subhumanermin', 'celouloourlaimd']
res = svc.explain_and_attribute(
    text="SUBHUMANERMIN CELOULOOURLAIMD",
    label=1,
    confidence=0.65,
    language="EN",
    tokens=tokens,
    ocr_text="SUBHUMANERMIN CELOULOOURLAIMD"
)
print("Result with garbled OCR tokens:", res)
