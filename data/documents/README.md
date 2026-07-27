# Kendi belgelerini buraya koy

Bu klasör **kasıtlı olarak boş** gönderiliyor.

Projenin geliştirildiği kurulumda burada IB'nin TOK Subject Guide'ı, sergi
değerlendirme ölçekleri ve kişisel ders çalışmaları vardı. Bunlar telifli ve
özel içerikler olduğu için depoya dahil edilmedi — `.gitignore` bu klasördeki
her şeyi (bu dosya hariç) dışarıda tutuyor.

Aslında projenin bütün iddiası da bu: **belgeler senin cihazından hiç çıkmaz.**
Ne bir buluta yüklenir, ne bir API'ye gönderilir, ne de bu depoya girer.

## Nasıl kullanılır

1. İstediğin dosyaları bu klasöre at. Desteklenen türler:
   - `.pdf`
   - `.docx`
   - `.txt`
   - `.md`

2. İndeksle:

   ```bash
   ./.venv/bin/python ingest.py
   ```

3. Asistanı çalıştır:

   ```bash
   ./.venv/bin/streamlit run app.py
   ```

## Bu klasörü boş bırakırsan ne olur?

Hiçbir şey bozulmaz — proje otomatik olarak `data/sample_documents/` içindeki
örnek korpusa düşer, böylece depoyu klonlayan biri hiçbir dosya eklemeden de
projeyi çalıştırıp görebilir.

## İpuçları

- **Taranmış PDF'ler çalışmaz.** İçinde metin katmanı olmayan (fotoğraf gibi)
  PDF'lerden yazı çıkarılamaz. `ingest.py` bunları fark eder ve uyarır.
- **Dosya adları önemli.** Cevapların altında kaynak olarak dosya adı
  gösteriliyor, o yüzden `belge1.pdf` yerine anlamlı isimler kullan.
- **Dosyayı güncellersen** `ingest.py`'yi tekrar çalıştır. Sadece değişen
  dosyalar yeniden işlenir, diğerleri saniyeler içinde atlanır.
