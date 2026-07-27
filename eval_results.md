# Değerlendirme Sonuçları

Bu rapor `python eval.py` ile otomatik üretildi.

## Özet

| | |
|---|---|
| Geçen test | **9/12** |
| Ortalama cevap süresi | 16.6 sn |
| Toplam süre | 200 sn |
| İndeks | 9 belge / 279 parça |
| Arama modeli | `qwen3-embedding-0.6b` |
| Cevap modeli | `qwen2.5-7b` |
| Motor | `foundry` |
| Getirilen parça sayısı (top_k) | 5 |

## Test tablosu

| # | Soru | Tür | Sonuç | Süre |
|---|------|-----|-------|------|
| 1 | TOK sergisinde kaç nesne seçmem gerekiyor? | cevaplanabilir | ✅ geçti | 14.6s |
| 2 | Sergi yorumu en fazla kaç kelime olabilir? | cevaplanabilir | ✅ geçti | 14.4s |
| 3 | Nesnelerin gerçek dünya bağlamı neden önemli? | cevaplanabilir | ✅ geçti | 22.3s |
| 4 | Değerlendirmede en üst seviyeyi (9-10) almak için ne gerekiyor? | cevaplanabilir | ❌ kaldı | 16.4s |
| 5 | IA prompt listesinde kaç tane soru var? | cevaplanabilir | ✅ geçti | 16.6s |
| 6 | TOK sergisi kaç puan üzerinden değerlendiriliyor? | cevaplanabilir | ❌ kaldı | 13.0s |
| 7 | Bilgi soruları (knowledge questions) nedir? | cevaplanabilir | ✅ geçti | 23.5s |
| 8 | TOK dersinin bilgi alanları (areas of knowledge) hangileridir? | cevaplanabilir | ✅ geçti | 17.2s |
| 9 | Sergi için nesne seçerken nelerden kaçınmalıyım? | cevaplanabilir | ✅ geçti | 24.3s |
| 10 | Matematik HL sınavının 2026 tarihi ne zaman? | cevaplanamaz | ❌ kaldı | 15.5s |
| 11 | Okul kantininde tost kaç lira? | cevaplanamaz | ✅ geçti | 10.7s |
| 12 | Ay'a ilk kim ayak bastı? | cevaplanamaz | ✅ geçti | 11.1s |

## Cevapların tamamı

### 1. TOK sergisinde kaç nesne seçmem gerekiyor?

*Tür:* cevaplanabilir  
*Not:* Temel bilgi — sergi kuralı  
*Sonuç:* ✅ geçti — geçti  
*Süre:* 14.6 sn

**Cevap:**

> TOK sergisinde üç nesne seçmelisiniz. [TOK Subject Guide 2020 (published version).pdf, s.45]

**Getirilen kaynaklar:**

- `TOK Subject Guide 2020 (published version).pdf` s.45 — benzerlik 0.618
- `TOK Subject Guide 2020 (published version).pdf` s.47 — benzerlik 0.549
- `TOK Subject Guide 2020 (published version).pdf` s.46 — benzerlik 0.538
- `TOK Subject Guide 2020 (published version).pdf` s.49 — benzerlik 0.532
- `TOK Exhibition prompts - full list of the 35 KQs, March 2026.pdf` s.1 — benzerlik 0.525

### 2. Sergi yorumu en fazla kaç kelime olabilir?

*Tür:* cevaplanabilir  
*Not:* Sayısal kural, uydurmaya çok müsait  
*Sonuç:* ✅ geçti — geçti  
*Süre:* 14.4 sn

**Cevap:**

> Sergi yorumu en fazla 950 kelime olabilir. [TOK Subject Guide 2020 (published version).pdf, s.48]

**Getirilen kaynaklar:**

- `TOK Subject Guide 2020 (published version).pdf` s.50 — benzerlik 0.490
- `IB HL COURSE DESCRIPTION 2025-2026.pdf` s.3 — benzerlik 0.470
- `TOK Subject Guide 2020 (published version).pdf` s.48 — benzerlik 0.439
- `Improve Your Exhibition  What Does The Ib Say_ 1.pdf` s.8 — benzerlik 0.396
- `Improve Your Exhibition  What Does The Ib Say_ 1.pdf` s.8 — benzerlik 0.374

### 3. Nesnelerin gerçek dünya bağlamı neden önemli?

*Tür:* cevaplanabilir  
*Not:* Kavramsal soru  
*Sonuç:* ✅ geçti — geçti  
*Süre:* 22.3 sn

**Cevap:**

> Nesnelerin gerçek dünya bağlamı önemlidir çünkü her nesne bir belirli zaman ve yerde var olan bir şey olmalıdır. Bu bağlam, nesnenin gerçeklikte nasıl ortaya çıktığı ve niyetine dair kanıtlar sağlar. Ayrıca, nesnelerin seçimi, konuyla ilgili tartışılabilecek bir gerilim veya anlaşmazlık göstermesi için de kritik bir rol oynar. [TOK Subject Guide 2020 (published version).pdf, s.48]

**Getirilen kaynaklar:**

- `TOK Subject Guide 2020 (published version).pdf` s.48 — benzerlik 0.638
- `TOK Subject Guide 2020 (published version).pdf` s.48 — benzerlik 0.562
- `TOK Exhibition prompts - full list of the 35 KQs, March 2026.pdf` s.1 — benzerlik 0.562
- `Shared Exhibition Checklist revised Nov 2025.pdf` s.1 — benzerlik 0.551
- `TOK Exhibition Outline Template.pdf` s.1 — benzerlik 0.544

### 4. Değerlendirmede en üst seviyeyi (9-10) almak için ne gerekiyor?

*Tür:* cevaplanabilir  
*Not:* Değerlendirme ölçeğinden cevaplanmalı  
*Sonuç:* ❌ kaldı — beklenen ifadelerden hiçbiri yok: ('açık', 'clearly', 'gerekçe', 'justification', 'kanıt', 'evidence', 'bağlantı', 'güçlü', 'detaylı', 'destek', 'iyi açıkla')  
*Süre:* 16.4 sn

**Cevap:**

> Öğrencinin çalışma, o seviyede tanımlanan nitelikleri büyük ölçüde göstermelidir. [TOK Subject Guide 2020 (published version).pdf, s.52]

**Getirilen kaynaklar:**

- `TOK Subject Guide 2020 (published version).pdf` s.52 — benzerlik 0.595
- `TOK Subject Guide 2020 (published version).pdf` s.54 — benzerlik 0.574
- `TOK Subject Guide 2020 (published version).pdf` s.52 — benzerlik 0.541
- `TOK Subject Guide 2020 (published version).pdf` s.52 — benzerlik 0.524
- `TOK Subject Guide 2020 (published version).pdf` s.52 — benzerlik 0.482

### 5. IA prompt listesinde kaç tane soru var?

*Tür:* cevaplanabilir  
*Not:* 35 KQ listesi belgesinden  
*Sonuç:* ✅ geçti — geçti  
*Süre:* 16.6 sn

**Cevap:**

> IA prompt listesinde 35 soru var. [TOK Exhibition prompts - full list of the 35 KQs, March 2026.pdf, s.1]

**Getirilen kaynaklar:**

- `TOK Exhibition Outline Template.pdf` s.1 — benzerlik 0.562
- `TOK Subject Guide 2020 (published version).pdf` s.46 — benzerlik 0.501
- `TOK Exhibition prompts - full list of the 35 KQs, March 2026.pdf` s.1 — benzerlik 0.472
- `TOK Subject Guide 2020 (published version).pdf` s.17 — benzerlik 0.452
- `Exhibition Rubric from TOK Subject Guide 2020 1.pdf` s.1 — benzerlik 0.447

### 6. TOK sergisi kaç puan üzerinden değerlendiriliyor?

*Tür:* cevaplanabilir  
*Not:* Değerlendirme yapısı  
*Sonuç:* ❌ kaldı — cevap belgelerde var ama bulamadı  
*Süre:* 13.0 sn

**Cevap:**

> Bu belgelerde bulamadım. [TOK Subject Guide 2020 (published version).pdf, s.11]

**Getirilen kaynaklar:**

- `TOK Subject Guide 2020 (published version).pdf` s.52 — benzerlik 0.618
- `TOK Subject Guide 2020 (published version).pdf` s.54 — benzerlik 0.574
- `TOK Subject Guide 2020 (published version).pdf` s.15 — benzerlik 0.566
- `TOK Subject Guide 2020 (published version).pdf` s.54 — benzerlik 0.556
- `TOK Subject Guide 2020 (published version).pdf` s.11 — benzerlik 0.556

### 7. Bilgi soruları (knowledge questions) nedir?

*Tür:* cevaplanabilir  
*Not:* Temel TOK kavramı  
*Sonuç:* ✅ geçti — geçti  
*Süre:* 23.5 sn

**Cevap:**

> Bilgi soruları, bilgi hakkında nasıl üretildiğini, nasıl kazandırılıp paylaşıldığını ve ne olduğunun ve olmamasının hakkında sorularda yer alır. Öğrenciler, bilgi ve bilgi oluşturma sürecini incelemek için konseptleri ve konuları inceliyor ve bilgiyi değerlendirme yöntemlerini ve araçlarını da ele alıyorlar. Bu sorular, bilgi ve bilgi oluşturma sürecinin nasıl yapıldığına dair genel görüşleri ve perspektifleri de ele alır. [TOK Subject Guide 2020 (published version).pdf, s.22]

**Getirilen kaynaklar:**

- `TOK Subject Guide 2020 (published version).pdf` s.23 — benzerlik 0.593
- `TOK Subject Guide 2020 (published version).pdf` s.8 — benzerlik 0.576
- `TOK Subject Guide 2020 (published version).pdf` s.22 — benzerlik 0.574
- `TOK Subject Guide 2020 (published version).pdf` s.22 — benzerlik 0.556
- `TOK Subject Guide 2020 (published version).pdf` s.17 — benzerlik 0.554

### 8. TOK dersinin bilgi alanları (areas of knowledge) hangileridir?

*Tür:* cevaplanabilir  
*Not:* Müfredat yapısı  
*Sonuç:* ✅ geçti — geçti  
*Süre:* 17.2 sn

**Cevap:**

> TOK dersinin bilgi alanları (areas of knowledge) şunlardır: tarih, insan bilimleri, doğal bilimler, matematik ve sanat. [TOK Subject Guide 2020 (published version).pdf, s.11]

**Getirilen kaynaklar:**

- `TOK Subject Guide 2020 (published version).pdf` s.11 — benzerlik 0.680
- `TOK Subject Guide 2020 (published version).pdf` s.14 — benzerlik 0.628
- `TOK Subject Guide 2020 (published version).pdf` s.12 — benzerlik 0.625
- `TOK Subject Guide 2020 (published version).pdf` s.11 — benzerlik 0.609
- `TOK Subject Guide 2020 (published version).pdf` s.22 — benzerlik 0.608

### 9. Sergi için nesne seçerken nelerden kaçınmalıyım?

*Tür:* cevaplanabilir  
*Not:* Pratik tavsiye  
*Sonuç:* ✅ geçti — geçti  
*Süre:* 24.3 sn

**Cevap:**

> Nesne seçerken, fikirleri aşina hissetmekten veya gerçeği yansıtmayan fikirlerden kaçınmalısın. Örneğin, belgelerde belirtildiği üzere, genel kavramları (örneğin, "teleskop") tercih etmeyi ve yerine gerçek dünya bağlamındaki spesifik nesneler (örneğin, "Edwin Hubble'nin uzay genişlemesini araştırmak için kullandığı teleskop") kullanmayı tercih etmelisin. Ayrıca, sanal veya yapılmış örneklerden de kaçınmalısın. [Shared Exhibition Checklist revised Nov 2025.pdf, s.1]

**Getirilen kaynaklar:**

- `Shared Exhibition Checklist revised Nov 2025.pdf` s.1 — benzerlik 0.430
- `TOK Exhibition Outline Template.pdf` s.1 — benzerlik 0.375
- `TOK Exhibition Outline Template.pdf` s.1 — benzerlik 0.365
- `Improve Your Exhibition  What Does The Ib Say_ 1.pdf` s.5 — benzerlik 0.361
- `TOK Subject Guide 2020 (published version).pdf` s.35 — benzerlik 0.355

### 10. Matematik HL sınavının 2026 tarihi ne zaman?

*Tür:* **cevaplanamaz** (asistan bilmediğini söylemeli)  
*Not:* Belgelerde yok — uydurursa kalır  
*Sonuç:* ❌ kaldı — UYDURDU — belgelerde olmayan soruya cevap verdi  
*Süre:* 15.5 sn

**Cevap:**

> Matematik HL sınavının 2026 tarihi, üçüncü yılın sonbahar aylarında, yani Kasım aylarında gerçekleşecektir. [IB HL COURSE DESCRIPTION 2025-2026.pdf, s.4]

**Getirilen kaynaklar:**

- `IB HL COURSE DESCRIPTION 2025-2026.pdf` s.3 — benzerlik 0.422
- `theoryofknowledgeassessedstudentworken_9f19b53bdd8f4e48b5eb3a991ac3ef38.pdf` s.10 — benzerlik 0.387
- `IB HL COURSE DESCRIPTION 2025-2026.pdf` s.2 — benzerlik 0.382
- `IB HL COURSE DESCRIPTION 2025-2026.pdf` s.4 — benzerlik 0.373
- `TOK Exhibition Outline Template.pdf` s.1 — benzerlik 0.359

### 11. Okul kantininde tost kaç lira?

*Tür:* **cevaplanamaz** (asistan bilmediğini söylemeli)  
*Not:* Tamamen alakasız konu  
*Sonuç:* ✅ geçti — doğru şekilde 'bulamadım' dedi  
*Süre:* 10.7 sn

**Cevap:**

> Bu belgelerde bulamadım.

**Getirilen kaynaklar:**

- `theoryofknowledgeassessedstudentworken_9f19b53bdd8f4e48b5eb3a991ac3ef38.pdf` s.10 — benzerlik 0.364
- `theoryofknowledgeassessedstudentworken_9f19b53bdd8f4e48b5eb3a991ac3ef38.pdf` s.8 — benzerlik 0.358
- `TOK Subject Guide 2020 (published version).pdf` s.41 — benzerlik 0.304
- `TOK Subject Guide 2020 (published version).pdf` s.49 — benzerlik 0.301
- `TOK Subject Guide 2020 (published version).pdf` s.14 — benzerlik 0.298

### 12. Ay'a ilk kim ayak bastı?

*Tür:* **cevaplanamaz** (asistan bilmediğini söylemeli)  
*Not:* Modelin genel bilgisinde var ama BELGELERDE yok — asıl sınav bu  
*Sonuç:* ✅ geçti — doğru şekilde 'bulamadım' dedi  
*Süre:* 11.1 sn

**Cevap:**

> Bu belgelerde bulamadım.

**Getirilen kaynaklar:**

- `Copy of A TOK TALE.pdf` s.1 — benzerlik 0.250
- `Copy of A TOK TALE.pdf` s.2 — benzerlik 0.234
- `Improve Your Exhibition  What Does The Ib Say_ 1.pdf` s.5 — benzerlik 0.218
- `TOK Exhibition prompts - full list of the 35 KQs, March 2026.pdf` s.4 — benzerlik 0.215
- `Shared Exhibition Checklist revised Nov 2025.pdf` s.1 — benzerlik 0.209
