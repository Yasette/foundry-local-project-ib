# Embedding ve Vektör Arama

## Embedding nedir?

Embedding, bir metni sabit uzunlukta bir sayı dizisine (vektöre) çeviren
modeldir. Bu projede kullanılan `qwen3-embedding-0.6b` modeli her metni 1024
boyutlu bir vektöre çevirir.

Bu vektörün özelliği şudur: **anlamca benzer metinler, uzayda birbirine yakın
vektörlere dönüşür.** Kelimeler farklı olsa bile. Hatta diller farklı olsa bile:
çok dilli bir embedding modelinde "three objects" ile "üç nesne" birbirine
yakın çıkar.

## Kosinüs benzerliği

İki vektörün ne kadar benzer olduğunu ölçmek için aralarındaki açının
kosinüsüne bakılır:

    benzerlik(a, b) = (a · b) / (|a| × |b|)

Burada:
- `a · b` iki vektörün nokta çarpımıdır (karşılıklı elemanların çarpımlarının
  toplamı).
- `|a|` vektörün uzunluğudur (elemanların karelerinin toplamının karekökü).

Sonuç -1 ile 1 arasında bir sayıdır:
- **1'e yakın:** aynı yöne bakıyorlar, yani aynı şeyden bahsediyorlar.
- **0 civarı:** alakasızlar.
- **Negatif:** zıt yönlüler (metin embedding'lerinde nadiren görülür).

Uzunluk yerine yöne bakmamızın sebebi şu: uzun bir paragraf ile kısa bir cümle
aynı konudaysa, vektör büyüklükleri farklı olsa bile yönleri benzer olur.

## Neden normalize ediyoruz?

Tüm vektörleri önceden birim uzunluğa (uzunluk = 1) getirirsek, formülün
paydası 1 olur ve kosinüs benzerliği sadece nokta çarpımına iner. Böylece tüm
belge parçalarıyla karşılaştırma tek bir matris çarpımına dönüşür ve binlerce
parça milisaniyelerde taranır.

## Vektör veritabanı ne zaman gerekir?

Birkaç bin parçaya kadar, tüm vektörleri belleğe alıp tek matris çarpımı
yapmak fazlasıyla hızlıdır. Yüz binlerce parçaya çıkıldığında yaklaşık en yakın
komşu (ANN) araması yapan özel veritabanları (FAISS, Qdrant, pgvector gibi)
gerekir.
