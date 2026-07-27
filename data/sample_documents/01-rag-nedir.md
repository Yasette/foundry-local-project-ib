# RAG (Retrieval-Augmented Generation) Nedir?

RAG, bir dil modelinin kendi eğitim bilgisine değil, sen verdiğin belgelere
dayanarak cevap vermesini sağlayan bir tasarım kalıbıdır. Adı üç adımdan gelir:

## 1. Retrieve — Bul

Kullanıcının sorusu bir embedding modeliyle sayısal vektöre çevrilir. Aynı
işlem daha önce tüm belge parçalarına da uygulanmıştır. Soru vektörüne en yakın
belge vektörleri bulunur. Yakınlık ölçüsü genellikle kosinüs benzerliğidir.

## 2. Augment — Bağlama Ekle

Bulunan belge parçaları, modele gönderilecek prompt'un içine bağlam olarak
yerleştirilir. Modele "sadece bu metinlere bakarak cevapla" talimatı verilir.

## 3. Generate — Üret

Model cevabı üretir. Cevap, eğitim verisinden değil, verilen bağlamdan gelir.

## RAG neden kullanılır?

- **Halüsinasyon azalır.** Model uydurmak yerine önüne konan metinden okur.
- **Kaynak gösterilebilir.** Hangi belgeden geldiğini biliriz.
- **Model eğitmek gerekmez.** Yeni bilgi eklemek için sadece belge eklenir;
  fine-tuning yapmaya, GPU saatleri harcamaya gerek yoktur.
- **Bilgi güncellenebilir.** Belgeyi değiştirirsin, indeksi yenilersin, biter.

## RAG'ın sınırları

- Retrieval yanlış parçayı getirirse model doğru cevap veremez. Cevap
  kalitesinin tavanını arama adımı belirler, model değil.
- Belge parçalama (chunking) kötüyse arama da kötü olur.
- Çok geniş, "belgenin genelini özetle" tarzı sorularda zayıftır; RAG nokta
  atışı soru-cevap için tasarlanmıştır.
