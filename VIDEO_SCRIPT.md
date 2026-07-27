# 2 Dakikalık Demo Videosu — Çekim Metni

> "Kısa konuşmalar, uzun anlatmaktan 100 kat daha zordur."

Bu metin ezberlenmek için değil, **konuşulmak** için yazıldı. Cümleleri kendi
ağzına göre değiştir. Tek kural: süreyi aşma.

---

## Çekimden önce hazırlık (5 dakika)

1. **Modeli önceden yükle.** `streamlit run app.py` ile uygulamayı aç ve
   videodan önce bir soru sor. Böylece modeller belleğe yüklenir ve kayıt
   sırasında ilk cevabı beklemezsin.
2. **Tarayıcıyı temizle.** Sekmeleri kapat, yer imleri çubuğunu gizle
   (`Cmd+Shift+B`), bildirimleri sustur (Rahatsız Etmeyin modu).
3. **Ekran kaydı:** `Cmd+Shift+5` → "Seçili Bölümü Kaydet" → tarayıcı penceresi.
   Mikrofonu açmayı unutma (kayıt panelindeki "Seçenekler" menüsünden).
4. **Wi-Fi'ı kapat.** Videonun en güçlü anı bu: internet kapalıyken çalıştığını
   canlı gösterirsin.
5. **Soruları önceden belirle** ve bir kağıda yaz. Kayıtta düşünmek zaman kaybı.

---

## 0:00 – 0:20 · Problem

> "Merhaba, ben Yasemin. TOK sergimi hazırlarken beş ayrı PDF arasında sürekli
> ileri geri gidiyordum — kaç nesne isteniyor, yorum kaç kelime, rubric'te en
> üst seviye ne diyor. Her seferinde aynı belgeleri yeniden açmak yerine, bu
> belgelere **soru sorabildiğim** bir asistan yaptım."

*Ekranda:* açık duran uygulama, kenar çubuğunda "9 belge / 279 parça" görünüyor.

---

## 0:20 – 0:55 · Ne yaptım (canlı demo)

**Birinci soru — belgede cevabı olan bir şey:**

> "Mesela: sergi yorumu en fazla kaç kelime olabilir?"

*Cevabın akmasını bekle, sonra Kaynaklar kutusunu aç.*

> "Cevabı uydurmadı. Şuradan aldı — TOK Subject Guide, şu sayfa. Yani her
> iddianın arkasında gösterebileceğim bir kaynak var."

**İkinci soru — belgede cevabı OLMAYAN bir şey:** *(videonun en önemli 10
saniyesi, sakın atlama)*

> "Şimdi belgelerde olmayan bir şey sorayım: Ay'a ilk kim ayak bastı?"

*Asistan "Bu belgelerde bulamadım" diyecek.*

> "Model bunun cevabını aslında biliyor. Ama ben ona sadece benim belgelerimden
> konuşmasını söyledim — bilmediğinde bilmediğini söylüyor. Bir çalışma
> asistanında bu, doğru cevap vermekten daha önemli."

---

## 0:55 – 1:25 · Nasıl çalışıyor

*Ekranda:* `docs/architecture.md` diyagramı veya kısaca kod.

> "Arkasında RAG denen bir yöntem var, üç adım:
> **Bul** — belgeleri küçük parçalara böldüm, her parçayı bir embedding
> modeliyle sayı dizisine çevirdim. Sorduğum soruyu da sayıya çevirip hangi
> parçanın en yakın olduğuna bakıyorum.
> **Ekle** — en yakın dört parçayı modele bağlam olarak veriyorum.
> **Üret** — model sadece o metne bakarak cevabı yazıyor.
>
> Ve şuna dikkat: *(Wi-Fi simgesini göster)* internet kapalı. Model Microsoft
> Foundry Local ile benim bilgisayarımda çalışıyor. Belgelerim hiçbir yere
> gitmiyor — ki IB belgeleri ve kendi ödevlerim için bu önemliydi."

---

## 1:25 – 2:00 · Ne öğrendim

> "Üç şey öğrendim.
>
> **Bir:** embedding dediğimiz şey aslında anlamı sayıya çevirmek. Ve iki metnin
> benzerliğini ölçerken kullandığım kosinüs benzerliği, derste gördüğümüz vektör
> konusunun ta kendisi — iki ok arasındaki açı. Matematiğin nerede işe
> yaradığını ilk kez bu kadar somut gördüm.
>
> **İki:** en şaşırtıcısı — cevap kalitesini belirleyen şey model değil,
> belgeleri nasıl parçaladığım oldu. Parçalar çok büyük olunca alakasız metin de
> modele gidiyor ve cevap bulanıklaşıyordu; çok küçük olunca cümlenin ortasından
> kesiliyordu. Küçük bir modelle iyi bağlam, büyük bir modelle kötü bağlamdan
> daha iyi sonuç veriyor.
>
> **Üç:** test yazmak sandığımdan zormuş. Belgelerde olmayan sorular sorup
> uydurup uydurmadığını ölçtüm. İlk sonuçta üç test kaldı — sonra fark ettim ki
> model aslında doğru davranmış, sadece "bu belgelerde bulamadım" yerine
> "bağlamda bulamadım" demiş. Yani benim testim modeli değil, kelime tercihini
> ölçüyormuş. Düzelttim. Ölçtüğünü sandığın şeyi gerçekten ölçüyor musun —
> bunu sormak gerekiyormuş.
>
> Teşekkürler."

---

## Süre kontrolü

| Bölüm | Süre | Toplam |
|---|---|---|
| Problem | 20 sn | 0:20 |
| Canlı demo | 35 sn | 0:55 |
| Nasıl çalışıyor | 30 sn | 1:25 |
| Ne öğrendim | 35 sn | 2:00 |

## Sık yapılan hatalar

- **Kurulumu anlatmak.** Kimse `pip install` görmek istemiyor. Doğrudan
  çalışan ürünü göster.
- **Kod okumak.** Kod repoda zaten var. Videoda sonucu göster.
- **Özür dilemek.** "Çok basit ama…", "Tam bitiremedim ama…" deme. Ne
  yaptıysan onu göster.
- **Tek çekimde yapmaya çalışmak.** İki üç deneme normal. Ama her denemede
  baştan başla — montajla birleştirmeye çalışma, akıcılığı bozar.
