# IB Notebook — Extended Essay, Internal Assessment, TOK

Bu bir ders anlatımı değil, **linkli bir kaynak listesi**. Amaç: EE/IA/TOK
hazırlarken hangi sayfaya bakman gerektiğini bir yerde toplamak.

**Önemli sınır:** IB'nin gerçek, resmi değerlendirme ölçekleri (subject guide'lar,
EE/IA marking criteria) **Programme Resource Centre (PRC)** üzerinde —
`resources.ibo.org` — ve girişe kapalı; sadece IB World School hesabınla
görebiliyorsun. Aşağıdaki linkler bunun **dışında kalan, herkese açık**
sayfalar + saygın üçüncü parti rehberler. Üçüncü parti olanlar açıkça
işaretlendi — resmi ölçüt yerine geçmezler, sadece yön verirler.

---

## Extended Essay (EE)

**Resmi (ibo.org, herkese açık):**
- [Extended essay — genel bakış](https://ibo.org/programmes/diploma-programme/curriculum/dp-core/extended-essay/)
- [What is the extended essay?](https://ibo.org/programmes/diploma-programme/curriculum/dp-core/extended-essay/what-is-the-extended-essay/)
- [Useful resources (ibo.org)](https://ibo.org/programmes/diploma-programme/curriculum/dp-core/extended-essay/useful-resources/)
- [Örnek öğrenci EE'leri + examiner yorumları](https://ibo.org/programmes/diploma-programme/curriculum/dp-core/extended-essay/example-essays/) — konu seçimi ve yazım tarzı için en değerli kaynak, gerçek örnekler

**Temel çerçeve:**
- 4.000 kelime, bağımsız araştırma, bir araştırma sorusu etrafında kurulu
- Değerlendirme ölçütleri derse göre değişir — **gerçek kriterler PRC'de**

**Üçüncü parti (resmi değil, ek okuma):**
- [Clastify — EE Guide](https://www.clastify.com/blog/ib-extended-essay-guide)
- [CASIE — EE 2027 güncellemeleri](https://www.casieonline.org/post/the-updated-ib-extended-essay-guide-new-criteria-full-writing-roadmap/)

---

## Internal Assessment (IA)

IA'nın **tek bir ortak ölçütü yok** — her dersin kendi kriterleri var ve bu
kriterler o dersin subject guide'ının içinde (yine PRC'de). Format da derse
göre çok değişiyor:

| Grup | Tipik IA formatı |
|---|---|
| Fen (Grup 4) | Bireysel araştırma / deney |
| Matematik | Exploration (keşif) |
| Beşeri bilimler (Grup 3) | Deneme / saha çalışması |
| Sanat (Grup 6) | Portfolyo |

**Örnek — Matematik IA'nın 5 ölçütü** (toplam 20 puan): Sunum (4), Matematiksel
İletişim (4), Kişisel Katılım (3), Yansıma/Refleksiyon (3), Matematik Kullanımı (6).
Bu oranlar derse göre değişir, kendi dersinin subject guide'ına bak.

**Resmi (ibo.org, herkese açık) — ders özeti sayfaları:**
- [DP curriculum — tüm dersler](https://www.ibo.org/programmes/diploma-programme/curriculum/) — her ders sayfasında "subject brief" PDF'i var (kamuya açık özet, tam kriter değil)

**Üçüncü parti (resmi değil, ek okuma):**
- [Lanterna — Ultimate IA Guide](https://lanterna.com/resources/ultimate-ib-internal-assessment-ia-guide)
- [Tiber Tutor — IB Assessment Criteria Explained](https://tibertutor.com/blog/what-is-ib-assessment-criteria)

---

## Theory of Knowledge (TOK)

Bu proje zaten TOK sergisi üzerine kurulu — [ana README](../README.md)'de
tüm mimari anlatılıyor. Ek kaynaklar:

**Resmi (ibo.org, herkese açık):**
- [Theory of knowledge — genel bakış](https://ibo.org/programmes/diploma-programme/curriculum/dp-core/theory-of-knowledge/)
- [Örnek TOK essay'leri](https://ibo.org/programmes/diploma-programme/curriculum/dp-core/theory-of-knowledge/example-essays/)

**Bağımsız, reklamsız, ücretsiz (en güvenilir üçüncü parti):**
- [TOKresource.org](https://www.tokresource.org/) — öğretmenler tarafından tutulan, paywall'sız, en kapsamlı TOK kaynağı

**Bu projedeki ilgili dosyalar:**
- `data/documents/` — kendi TOK Subject Guide, rubric, 35 KQ listesi kopyaların (git'e girmiyor)
- [`data/sample_documents/`](../data/sample_documents/) — RAG/embedding kavramlarının sade anlatımı

---

## Bunu asistana da sormak istersen

Bu notebook şimdilik sadece bir referans dosyası — RAG asistanının
veritabanına dahil değil. Eğer ileride EE/IA konularında da soru
sorabilmek istersen: bu sayfadaki linklerden indirdiğin (veya kendi
yazdığın) notları `data/documents/` klasörüne atıp `python ingest.py`
çalıştırman yeterli — sistem zaten herhangi bir PDF/DOCX/TXT/MD dosyasını
kabul ediyor, TOK'a özel bir kısıtlama yok.
