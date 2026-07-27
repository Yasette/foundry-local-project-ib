# Microsoft Foundry Local

Foundry Local, dil modellerini tamamen kullanıcının cihazında çalıştırmak için
geliştirilen bir çalışma zamanı ve SDK'dır. Bulut aboneliği, API anahtarı veya
internet bağlantısı gerektirmez.

## Temel özellikleri

- **Model kataloğu.** Önceden optimize edilmiş modeller (Qwen, Phi, Mistral,
  Whisper ve diğerleri) takma adlarıyla indirilebilir.
- **Donanım hızlandırma.** ONNX Runtime üzerinden CPU, GPU veya NPU kullanır.
  Apple Silicon makinelerde GPU'ya erişim Metal üzerinden sağlanır.
- **Çoklu dil desteği.** SDK Python, C#, JavaScript ve Rust için mevcuttur.
- **Yerel önbellek.** İndirilen model ağırlıkları diskte tutulur; ikinci
  çalıştırmada indirme adımı atlanır.

## Python'da tipik kullanım

Yönetici başlatılır, katalogdan bir model alınır, indirilir ve yüklenir.
Ardından modelden bir sohbet istemcisi veya embedding istemcisi alınır.
Sohbet istemcisi hem tek seferlik hem de akış (streaming) modunda cevap
üretebilir.

## Sistem gereksinimleri

- Windows, macOS veya Linux.
- En az 8 GB RAM, 16 GB önerilir.
- macOS tarafında Apple Silicon işlemci gerekir.
- Python SDK'sı Python 3.11, 3.12 veya 3.13 sürümleriyle çalışır.

## Neden yerel çalıştırmak isteyelim?

- **Gizlilik.** Belgeler ve sorular cihazdan hiç çıkmaz.
- **Maliyet.** Token başına ücret yoktur.
- **Çevrimdışı çalışma.** Model bir kez indikten sonra internet gerekmez.
- **Gecikme.** Ağ turu olmadığı için ilk token daha çabuk gelebilir.

Buna karşılık yerel modeller, bulutta çalışan çok büyük modellere göre daha
küçüktür; karmaşık akıl yürütme gerektiren işlerde daha zayıf kalırlar. RAG
kalıbı tam da bu açığı kapatır: modelden bilgi hatırlamasını değil, önüne
konan metni okumasını isteriz.
