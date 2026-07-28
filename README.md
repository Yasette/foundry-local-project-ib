# TOK Çalışma Asistanı

IB TOK belgelerime soru sorabildiğim, tamamen kendi bilgisayarımda çalışan bir
soru-cevap uygulaması. İnternet bağlantısı ve bulut hesabı gerekmiyor, belgeler
cihazdan dışarı çıkmıyor.

Microsoft Foundry Local ile cihaz üzerinde çalışan bir dil modeli ve RAG
(Retrieval-Augmented Generation) yöntemi kullanıyor.

Demo videosu (2 dk): `<DRIVE_LINKINI_BURAYA_YAPIŞTIR>`

Ayrıca: [IB Notebook](docs/ib-notebook.md) — Extended Essay, Internal Assessment
ve TOK için topladığım kaynak listesi.

## Amaç

TOK sergisi hazırlarken "kaç nesne isteniyordu", "yorum kaç kelime olabilir",
"değerlendirme ölçeğinde en üst seviye ne diyor" gibi soruların cevabını beş
ayrı PDF içinde aramak zaman alıyordu. Bu uygulama aynı belgelere doğrudan
soru sormamı sağlıyor ve cevabın hangi dosyanın hangi sayfasından geldiğini
gösteriyor.

Örnek:

> **Soru:** Sergi yorumu en fazla kaç kelime olabilir?
>
> **Cevap:** Sergi yorumu en fazla 950 kelime olabilir. [TOK Subject Guide 2020, s.45]

Belgelerde olmayan bir şey sorulduğunda "Bu belgelerde bulamadım" diyor.

Uygulama TOK belgeleriyle kuruldu ama herhangi bir belge koleksiyonuyla
çalışıyor: ders notları, yarışma şartnameleri, kullanım kılavuzları.

## Nasıl çalışıyor

RAG üç adımdan oluşuyor.

**1. Bul.** Belgeler yaklaşık 900 karakterlik parçalara bölünüyor. Her parça bir
embedding modeliyle sayı dizisine (vektöre) çevrilip SQLite veritabanına
kaydediliyor. Soru sorulduğunda soru da vektöre çevriliyor ve hangi parçaların
vektörü soruya en yakınsa onlar seçiliyor. Yakınlık ölçüsü kosinüs benzerliği:

```
benzerlik(a, b) = (a · b) / (|a| × |b|)
```

Bu, iki vektör arasındaki açının kosinüsü, yani derste gördüğümüz vektör
konusunun aynısı. 1'e yakınsa iki metin aynı yöne bakıyor, yani aynı şeyden
bahsediyor. Uzunluk değil yön önemli olduğu için uzun bir paragrafla kısa bir
cümle aynı konudaysa yine yüksek skor alıyor.

**2. Ekle.** Seçilen parçalar modele gönderilen mesajın içine bağlam olarak
konuyor ve modele "sadece bu metinlere bakarak cevapla, burada yoksa
bilmediğini söyle" deniyor.

**3. Üret.** Model cevabı yazıyor. Cevap eğitim verisinden değil, benim
belgelerimden geliyor.

Bu projede hiçbir model eğitilmiyor. Hazır modeller indiriliyor, belgeler bir
kez vektörleştirilip kaydediliyor. Modele yeni bilgi öğretmenin diğer yolu olan
fine-tuning saatler sürer, güçlü bir GPU ister ve kaynak gösteremez; RAG
dakikalar sürüyor ve her cevabın arkasında gösterebileceğim bir sayfa var.

Katmanların hangi dosyada olduğu ve tasarım gerekçeleri:
[docs/architecture.md](docs/architecture.md)

### Aramaya sonradan eklediğim iki şey

Sadece vektör araması yeterli olmadı, ölçtükten sonra iki ekleme yaptım.

**Kelime eşleşmesi.** "Yorum kaç kelime olabilir" diye sorduğumda konu olarak
yakın ama içinde 950 geçmeyen paragraflar öne çıkıyordu, çünkü embedding'ler
tam sayıları bulanıklaştırıyor. Vektör skoruna bir de kelime eşleşmesi skoru
ekledim (nadir kelimelere daha çok ağırlık veren IDF yöntemiyle). Son skor:
`0.7 × vektör + 0.3 × kelime`.

**Sorgu çevirisi.** Belgeler İngilizce, sorularım Türkçe. Ölçtüğümde Türkçe
soruların benzerlik skorları 0.35–0.55 aralığında sıkışıyordu, yani cevabı
içeren parça ile alakasız parça neredeyse aynı skoru alıyordu. Bu yüzden arama
yapmadan önce soruyu kısa bir İngilizce arama sorgusuna çeviriyorum, sonra hem
orijinal hem çevrilmiş sorguyla arayıp sonuçları birleştiriyorum. Böylece kötü
bir çeviri sadece yeni aday ekleyebiliyor, mevcut sonuçları eleyemiyor.

Embedding modelinin çok dilli olması bu işin temeli. Ölçtüm: aynı anlamın
Türkçe-İngilizce benzerliği 0.72, alakasız bir cümleyle benzerliği 0.17.

## Kurulum

Gereksinimler:

- macOS (Apple Silicon), Windows veya Linux
- En az 8 GB RAM
- Python 3.11, 3.12 veya 3.13
- Modeller için yaklaşık 5 GB boş disk

Python 3.10 ve öncesi ile 3.14 çalışmıyor, Foundry Local SDK bu sürümleri
desteklemiyor. macOS'ta sistem Python'ı genelde 3.9 olduğu için önce:

```bash
brew install python@3.12
```

Sonra kurulum scripti:

```bash
bash setup.sh
```

Bu script uygun Python sürümünü bulup `.venv` sanal ortamını oluşturuyor ve
paketleri kuruyor.

## Kullanım

**1. Belgelerini ekle.** Dosyaları `data/documents/` klasörüne koy. PDF, DOCX,
TXT ve MD destekleniyor. Klasörü boş bırakırsan `data/sample_documents/`
içindeki örnek dosyalar kullanılıyor, yani depoyu indiren biri hiçbir şey
eklemeden de deneyebiliyor.

**2. İndeksle.**

```bash
./.venv/bin/python ingest.py
```

İlk çalıştırmada modeller iniyor, birkaç dakika sürüyor. Sonraki
çalıştırmalarda sadece değişen dosyalar işleniyor, çünkü her dosyanın içerik
özeti (sha256) veritabanında tutuluyor. Bende ilk indeksleme 51 saniye, ikincisi
0.2 saniye sürdü.

**3. Başlat.**

```bash
./.venv/bin/streamlit run app.py
```

Tarayıcıda açılıyor (açılmazsa terminalde yazan `http://localhost:8501`
adresine git). Alttaki kutuya soru yazıp Enter'a bas. Cevabın altındaki
"Kaynaklar" kutusunu açınca hangi belgeden hangi sayfadan alındığı, benzerlik
skoru ve alıntılanan metnin kendisi görünüyor.

Kapatmak için terminalde `Ctrl+C`.

## Test

Bir chatbot'un iyi görünmesi ile doğru olması farklı şeyler. `eval.py` iki tür
soru soruyor: cevabı belgelerde olanlar (doğru kaynağı getirmeli) ve cevabı
belgelerde olmayanlar (bilmediğini söylemeli). İkincisi daha önemli, çünkü
bilmediğini uyduran bir asistanın yanlış olduğunu anlamıyorsun.

```bash
./.venv/bin/python eval.py
```

Son ölçüm (qwen2.5-7b, 9 belge / 279 parça, MacBook Air M2): **12 testin 9'u
geçti**, ortalama cevap süresi 16.6 saniye. Her sorunun cevabı, getirilen
kaynaklar ve süreleri [eval_results.md](eval_results.md) dosyasında.

Testin kendisi de bir ders oldu. İlk çalıştırmada üç test kaldı ve "model
uydurdu" diye raporladı. Cevaplara bakınca model aslında doğru davranmıştı,
sadece "Bu belgelerde bulamadım" yerine "Bağlamda bulamadım" demişti. Yani test,
modelin doğruluğunu değil kelime tercihini ölçüyormuş. Reddetme tespitini kalıp
listesine çevirdim (`eval.py` içindeki `REFUSAL_PATTERNS`).

## Model seçimi

Katalogdaki modellerden dördünü aynı soruyla denedim:

| Model | Boyut | Cevap süresi | Sonuç |
|---|---|---|---|
| qwen2.5-1.5b | 1.5B | ~1 sn | Cevap bağlamda olduğu halde "bulamadım" dedi, serbest üretimde anlamsız cümleler kurdu |
| qwen3.5-4b | 4B | 129 sn | Cevaptan önce 6462 karakterlik iç monolog üreten bir "düşünen" model |
| phi-4-mini | 3.8B | ~9 sn | Türkçede kelime tekrarına giriyor, ayrıca bu bilgisayarda kararsız (aşağıda) |
| **qwen2.5-7b** | 7B | ~17 sn | Varsayılan. 12 testin tamamını sorunsuz tamamladı, Türkçesi en temizi |

phi-4-mini hızlı olduğu için ilk tercihimdi ama iki ayrı denemede süreç ikinci
sorudan sonra sessizce öldü. macOS çökme raporuna bakınca sebep kendi kodum
değildi:

```
exception: EXC_CRASH (SIGABRT)
Microsoft.AI.Foundry.Local.Core.dylib  ...Threading_WaitSubsystem...
```

Foundry Local çalışma zamanı bu model ve platform birleşiminde çöküyor.
qwen2.5-7b aynı testleri arka arkaya sorunsuz tamamladı, o yüzden onu seçtim.

Buradan çıkardığım şey: model küçüldükçe sadece "daha az bilgi" olmuyor,
talimata uyma becerisi de düşüyor. 1.5B'lik model cevabın önüne konmuş olmasına
rağmen bilmiyorum demeyi seçebiliyor ya da tam tersi, uydurabiliyor.

Modeli değiştirmek için:

```bash
RAG_CHAT_MODEL=phi-4-mini ./.venv/bin/streamlit run app.py
```

## Ayarlar

Hepsi [config.py](config.py) içinde.

| Ayar | Varsayılan | Ne işe yarıyor |
|---|---|---|
| `CHUNK_SIZE` | 900 | Parça boyutu (karakter). Büyütürsen alakasız metin de modele gider ve cevap bulanıklaşır, küçültürsen cümleler ortadan bölünür |
| `CHUNK_OVERLAP` | 150 | Ardışık parçaların örtüşmesi. Parça sınırına denk gelen bir cümlenin kaybolmasını engelliyor |
| `TOP_K` | 5 | Modele kaç parça verileceği. Arayüzdeki kaydırıcıyla da değiştirilebiliyor |
| `MIN_SCORE` | 0.20 | Bu benzerliğin altındaki parçalar alakasız sayılıyor |
| `TEMPERATURE` | 0.2 | Düşük değer daha tutarlı, uydurmaya daha az meyilli cevap veriyor |
| `TRANSLATE_QUERY` | True | Türkçe soruyu aramadan önce İngilizceye çeviriyor. Belgelerin de Türkçe olduğu bir kurulumda False yapılmalı |

## Bilinen sınırlar

12 testin 9'u geçiyor. Kalan üçünü saklamak yerine buraya yazıyorum, çünkü
öğretici olan kısım orası.

**En ciddi hata.** "Matematik HL sınavının 2026 tarihi ne zaman?" sorusuna
asistan şunu cevapladı:

> "Matematik HL sınavının 2026 tarihi, üçüncü yılın sonbahar aylarında, yani
> Kasım aylarında gerçekleşecektir. [IB HL COURSE DESCRIPTION 2025-2026.pdf, s.4]"

Bu bilgi belgelerde yok. Model uydurdu ve üstüne kaynak gösterdi, yani yanlış
cevabı doğru gibi paketledi. RAG halüsinasyonu azaltıyor ama sıfırlamıyor.
Arayüzde kaynak kutusunun olmasının sebebi bu: modelin gösterdiği sayfaya
gidip kendin bakabilmelisin.

Diğer sınırlar:

- **Benzerlik skoru tek başına "bilmiyorum" demeye yetmiyor.** Cevabı belgelerde
  olan sorular 0.35–0.57 bandında skor alıyor, olmayanlar 0.26–0.42. Bantlar
  çakışıyor, yani bir eşik değeriyle "bu soru belgelerde yok" diyemiyorum.
  Reddetme kararı modelin talimata uymasına kalıyor.
- **Kaynak atfı her zaman doğru dosyayı göstermiyor.** Model bilgiyi doğru
  okuyup doğru cevap verse bile beş alıntı arasından yanlış olanın etiketini
  yapıştırabiliyor.
- **Küçük modeller tekrar döngüsüne girebiliyor.** phi-4-mini açık uçlu bir
  soruda aynı cümleyi token sınırına kadar tekrarladı. Akışa bir tekrar koruması
  ekledim (`RepetitionGuard`, [src/rag.py](src/rag.py)).
- **Geniş sorularda zayıf.** "Bu belgeyi özetle" gibi sorular RAG'ın tasarım
  amacı değil, sistem nokta atışı soru-cevap için kurgulandı.

## Sorun giderme

| Belirti | Çözüm |
|---|---|
| `ModuleNotFoundError: foundry_local_sdk` | Sanal ortamı kullanmıyorsun, `./.venv/bin/python` ile çalıştır |
| Kurulumda "uygun Python bulunamadı" | `brew install python@3.12` |
| İlk çalıştırma çok uzun sürüyor | Modeller iniyor (~5 GB), bir kerelik |
| Açılışta uzun bekleme | Modelin ilk çıkarımı sonrakilerden yavaş (98 saniyeye karşı 8 saniye ölçtüm). `app.py` bu bedeli açılışta ödüyor ki ilk soru hızlı gelsin |
| "Veritabanı boş" uyarısı | Önce `python ingest.py` çalıştır |
| Bir PDF indekslenmedi | Taranmış (görüntü) PDF olabilir, metin katmanı yok. `ingest.py` bunu uyarı olarak yazıyor |
| Bildiği şeye "bulamadım" diyor | `TOP_K`'yı artır veya soruyu belgedeki terimlerle sor |
| Foundry Local hiç açılmıyor | Yedek motora geç: `RAG_BACKEND=ollama ./.venv/bin/streamlit run app.py` (önce `ollama pull nomic-embed-text && ollama pull qwen2.5:3b`) |

## Gizlilik

Belgeler hiçbir yere yüklenmiyor. İnternet sadece modellerin ilk indirilmesinde
kullanılıyor, sonrası tamamen çevrimdışı. `data/documents/` klasörü `.gitignore`
ile depo dışında tutuluyor: proje IB'nin telifli yayınlarıyla geliştirildi,
onları paylaşmak doğru olmazdı.

## Kaynaklar

Takip ettiğim Microsoft dokümanları:

- [Foundry Local — Get started](https://learn.microsoft.com/en-us/azure/foundry-local/get-started)
- [Tutorial: Build a RAG application](https://learn.microsoft.com/en-us/azure/foundry-local/tutorials/tutorial-build-rag-app)
- [Building Your First Local RAG Application with Foundry Local](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968)
- [Microsoft AI For Beginners](https://microsoft.github.io/AI-For-Beginners/)

## Lisans

Kod: [MIT](LICENSE). `data/` içine eklenen belgeler kendi telif haklarına tabi
ve bu depoya dahil değil.
