# How to Parse and Use PDF Data in Agents

You can extract text from PDFs (e.g., resumes, LinkedIn profiles) and use it as agent context or for downstream tasks.

## Example: Reading PDF Content

```python
from pypdf import PdfReader

reader = PdfReader("me/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text
```
