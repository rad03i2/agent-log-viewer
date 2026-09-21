# Agent Log Viewer

A small, local-first CLI for reading, filtering, summarizing, and following AI-agent logs without sending them to an external service.

**Author:** Radwan Abdulhadi Ahmed · رضوان عبدالهادي أحمد · GitHub: @rad03i2

## English

### Overview
Agent systems often produce JSONL or plain-text logs that become difficult to inspect during debugging. Agent Log Viewer turns those files into a consistent stream of entries, supports practical filters, and produces compact run summaries. It is deliberately dependency-free at runtime and works on Python 3.10+.

### Key features
- Parses JSONL fields such as `timestamp/time/ts`, `level/severity`, `message/msg/content`, `agent/agent_id`, and `event/type`.
- Parses common text lines such as `2026-09-21T10:00:00Z [ERROR] tool failed` and preserves unstructured lines.
- Filters by minimum severity, text or regex, exact agent, exact event, and ISO-8601 time range.
- Reads multiple files in one command and records source path/line number in JSON output.
- Summarizes level, agent, and event counts plus the observed timestamp range.
- Follows a live file with configurable polling, similar to `tail -f`.
- JSON output for scripts and CI pipelines.
- Local-only: no network calls, telemetry, API keys, or runtime dependencies.

### Requirements and installation
- Python 3.10 or newer

```bash
git clone https://github.com/rad03i2/agent-log-viewer.git
cd agent-log-viewer
python -m pip install -e .
agent-log-viewer --version
```

### Usage
Inspect errors across one or more logs:

```bash
agent-log-viewer view run.jsonl worker.log --level ERROR
```

Search a specific agent and emit JSONL:

```bash
agent-log-viewer view run.jsonl --agent planner --query timeout --json
```

Use regex and a time boundary:

```bash
agent-log-viewer view run.jsonl --query "tool_(call|error)" --regex --since 2026-09-21T00:00:00Z
```

Summarize a run:

```bash
agent-log-viewer stats examples/sample-agent.jsonl
agent-log-viewer stats examples/sample-agent.jsonl --json
```

Follow a growing log (Ctrl+C to stop):

```bash
agent-log-viewer follow run.jsonl --level WARN
```

By default `follow` starts at the end; add `--from-start` to read existing content first.

### Configuration
There is intentionally no configuration file or environment variable. All behavior is explicit through CLI flags. Timestamps used by `--since`/`--until` must be ISO-8601; timestamps without a timezone are treated as UTC.

### Supported input
JSON objects are read one per line. Unknown JSON fields are ignored. Malformed JSON is treated as ordinary text instead of crashing the reader. Files are decoded as UTF-8 with replacement for invalid byte sequences.

### Project structure
```text
src/agent_log_viewer/core.py   parsing, filtering, summaries
src/agent_log_viewer/cli.py    command-line interface
examples/sample-agent.jsonl    synthetic safe example
tests/                         unit and CLI integration tests
.github/workflows/ci.yml       cross-platform CI
```

### Testing
```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```
CI runs the suite and CLI smoke checks on Ubuntu, Windows, and macOS with Python 3.10, 3.12, and 3.13.

### Preview guidance
This is a terminal application. For a repository screenshot, run `agent-log-viewer stats examples/sample-agent.jsonl` and `agent-log-viewer view examples/sample-agent.jsonl --level WARN` in a clean terminal; no bundled screenshot is needed to use the project.

### Security and privacy
Processing stays on the machine. Source logs are read-only. Logs may themselves contain prompts, credentials, personal data, or tool results; this project does **not** automatically redact them, so inspect output before sharing it. Regex patterns are Python regular expressions and should only be accepted from trusted operators in automated services.

### Limitations
- This is a CLI, not a browser dashboard or distributed observability platform.
- JSON parsing is line-oriented; pretty-printed multi-line JSON is not supported.
- Plain-text parsing recognizes one common timestamp/level shape; other text remains searchable as INFO.
- `follow` watches one regular file and does not currently handle log rotation or truncation specially.
- No secret redaction, OpenTelemetry ingestion, compressed-file streaming, or persistent index is implemented.

### Optional roadmap
Potential additions include configurable field mapping, safe redaction rules, rotated-log following, and compressed log input. These are not required for current functionality.

### Contributing and license
See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Licensed under the [MIT License](LICENSE).

### Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

## العربية

### نظرة عامة
**Agent Log Viewer** أداة سطر أوامر محلية لقراءة سجلات وكلاء الذكاء الاصطناعي بصيغة JSONL أو النص العادي، ثم توحيدها وتصفيتها وتلخيصها ومتابعتها أثناء نمو الملف. صُممت لتكون صغيرة وواضحة وتعمل على Python 3.10+ من دون تبعيات تشغيل خارجية.

### لماذا توجد؟
سجلات أنظمة الوكلاء قد تصبح طويلة ويصعب العثور فيها على أخطاء أداة معينة أو أحداث وكيل محدد. توفر الأداة طريقة موحدة للبحث والتصفية والحصول على ملخص سريع من دون رفع السجل إلى خدمة خارجية.

### المزايا
- قراءة حقول JSONL الشائعة للتوقيت والمستوى والرسالة والوكيل والحدث.
- فهم صيغة نصية شائعة مثل `2026-09-21T10:00:00Z [ERROR] tool failed` مع الاحتفاظ بالأسطر غير المنظمة.
- تصفية حسب مستوى الخطورة والنص أو التعبير النمطي والوكيل والحدث والفترة الزمنية.
- قراءة عدة ملفات في أمر واحد، مع تضمين اسم المصدر ورقم السطر في مخرجات JSON.
- إحصاءات لعدد المستويات والوكلاء والأحداث وأول/آخر توقيت صالح.
- متابعة ملف حي بأسلوب `tail -f`.
- مخرجات JSON مناسبة للأتمتة وCI.
- تشغيل محلي بلا شبكة أو Telemetry أو مفاتيح API أو تبعيات تشغيل خارجية.

### المتطلبات والتثبيت
يتطلب Python 3.10 أو أحدث:

```bash
git clone https://github.com/rad03i2/agent-log-viewer.git
cd agent-log-viewer
python -m pip install -e .
agent-log-viewer --version
```

### الاستخدام
عرض الأخطاء:
```bash
agent-log-viewer view run.jsonl --level ERROR
```

البحث لوكيل محدد وإخراج JSON:
```bash
agent-log-viewer view run.jsonl --agent planner --query timeout --json
```

تلخيص سجل:
```bash
agent-log-viewer stats examples/sample-agent.jsonl
```

متابعة سجل أثناء الكتابة إليه:
```bash
agent-log-viewer follow run.jsonl --level WARN
```

### الإعداد
لا يوجد ملف إعداد أو متغيرات بيئة مطلوبة. جميع الخيارات تمرر صراحة عبر سطر الأوامر. يجب أن تكون حدود الوقت بصيغة ISO-8601، ويعامل الوقت الذي لا يحتوي منطقة زمنية على أنه UTC.

### بنية المشروع
- `src/agent_log_viewer/core.py`: التحليل والتصفية والإحصاءات.
- `src/agent_log_viewer/cli.py`: واجهة سطر الأوامر.
- `examples/sample-agent.jsonl`: مثال اصطناعي آمن.
- `tests/`: اختبارات المنطق والـCLI.
- `.github/workflows/ci.yml`: اختبارات متعددة الأنظمة.

### الاختبارات
```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```
ويشغّل CI الاختبارات وفحوص CLI على Ubuntu وWindows وmacOS مع Python 3.10 و3.12 و3.13.

### إرشاد المعاينة
المشروع طرفي؛ للحصول على لقطة مناسبة للمستودع شغّل أمر `stats` على ملف المثال ثم أمر `view` بمستوى WARN في نافذة طرفية نظيفة. لا تعتمد الأداة على أي صورة كي تعمل.

### الخصوصية والأمان
تتم المعالجة محليًا وتُقرأ ملفات المصدر دون تعديلها. قد تحتوي السجلات نفسها على أسرار أو بيانات شخصية أو نتائج أدوات؛ الأداة **لا تخفيها تلقائيًا**، لذلك راجع المخرجات قبل مشاركتها. في الخدمات المؤتمتة يجب قبول أنماط Regex من مشغل موثوق فقط.

### القيود
لا توجد لوحة ويب أو مراقبة موزعة. JSON متعدد الأسطر غير مدعوم، ومحلل النص يتعرف على صيغة شائعة واحدة بينما يعامل البقية كرسائل INFO قابلة للبحث. أمر `follow` يتابع ملفًا واحدًا ولا يعالج تدوير السجلات بصورة خاصة. لا يوجد حاليًا إخفاء أسرار أو OpenTelemetry أو فهرس دائم أو قراءة مباشرة للملفات المضغوطة.

### تطوير اختياري
يمكن مستقبلًا إضافة خرائط حقول قابلة للتخصيص، وقواعد إخفاء آمنة، ودعم تدوير السجلات والملفات المضغوطة. هذه إضافات اختيارية وليست وعودًا بميزات موجودة حاليًا.

### المساهمة والترخيص
راجع [CONTRIBUTING.md](CONTRIBUTING.md) و[SECURITY.md](SECURITY.md). المشروع مرخص تحت [MIT](LICENSE).

### المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
