import sqlite3
import time
from fetch_questions import init_db, insert_question, DB_PATH

SAMPLE_QUESTIONS = [
    {
        "question": "Bu trafik işareti neyi ifade eder? (Kırmızı sekizgen)",
        "option_a": "Dur",
        "option_b": "Yol ver",
        "option_c": "Park yasağı",
        "option_d": "Hız sınırı",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Şehir içi yerleşim alanında otomobiller için genel hız sınırı kaçtır?",
        "option_a": "30 km/s",
        "option_b": "50 km/s",
        "option_c": "70 km/s",
        "option_d": "90 km/s",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Emniyet şeridi hangi amaçla kullanılmalıdır?",
        "option_a": "Hızlı sollama yapmak",
        "option_b": "Acil durum ve görevli araçlar",
        "option_c": "Park etmek",
        "option_d": "Telefonla konuşmak için",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Yaya geçidinde ilk geçiş hakkı kimindir?",
        "option_a": "Araç",
        "option_b": "Yaya",
        "option_c": "Bisiklet",
        "option_d": "Motosiklet",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Kavşakta sağdaki araca yol vermek kuralı hangi durumda geçerlidir?",
        "option_a": "Işıklı kavşaklarda",
        "option_b": "Kontrolsüz kavşaklarda",
        "option_c": "Dönel kavşaklarda",
        "option_d": "Hepsinde",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Emniyet kemeri ne zaman takılmalıdır?",
        "option_a": "Yalnızca yüksek hızda",
        "option_b": "Yalnızca şehir dışı yollarda",
        "option_c": "Her zaman, sürüş boyunca",
        "option_d": "Sadece ön koltukta",
        "correct": "C",
        "source": "seed",
    },
    {
        "question": "Hangi durumda sis farları kullanılmalıdır?",
        "option_a": "Gece açık havada",
        "option_b": "Yoğun sis, kar veya yağmurda",
        "option_c": "Gündüz şehir içinde",
        "option_d": "Uzun yolda sürekli",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Arka arkaya takip mesafesi en az ne kadar olmalıdır?",
        "option_a": "Öndeki aracın hızının yarısı (metre)",
        "option_b": "2 saniye kuralı",
        "option_c": "1 araç boyu",
        "option_d": "5 metre",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Hız limitini aşmanın cezası nedir?",
        "option_a": "Sadece uyarı",
        "option_b": "Para cezası ve puan",
        "option_c": "Sadece ehliyete el koyma",
        "option_d": "Hiçbiri",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Araç kullanırken telefonla konuşma nasıl yapılmalıdır?",
        "option_a": "Elde telefonla",
        "option_b": "Kulaklık veya araç sistemi ile",
        "option_c": "Mesajlaşarak",
        "option_d": "Hiçbir şekilde gerek yok",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Park yasağını gösteren işaretin rengindeki çizgi nedir?",
        "option_a": "Mavi",
        "option_b": "Kırmızı",
        "option_c": "Sarı",
        "option_d": "Yeşil",
        "correct": "Soru işaret türüne göre değişir",
        "source": "seed",
    },
    {
        "question": "Dönel kavşakta öncelik kime aittir?",
        "option_a": "Kavşağa girene",
        "option_b": "Kavşakta dönene",
        "option_c": "Yayaya",
        "option_d": "Hiçbiri",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Aracın kör noktasını azaltmak için ne yapılmalıdır?",
        "option_a": "Aynalar doğru ayarlanmalı",
        "option_b": "Sürekli şerit değiştirmeli",
        "option_c": "Yüksek hızla gitmeli",
        "option_d": "Arka koltukları yatırmalı",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Okul geçitlerinde dikkat edilmesi gereken en önemli husus nedir?",
        "option_a": "Hızlanmak",
        "option_b": "Yayalara yol vermek",
        "option_c": "Kornaya basmak",
        "option_d": "Geçiş üstünlüğünü kullanmak",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Aracın farları hangi durumda kısa far olmalıdır?",
        "option_a": "Karşıdan araç geliyorsa",
        "option_b": "Hiçbir zaman",
        "option_c": "Gündüz açık hava",
        "option_d": "Sisli hava",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Geçiş üstünlüğü hangi araçlara aittir?",
        "option_a": "Ambulans, itfaiye, polis",
        "option_b": "Taksi",
        "option_c": "Toplu taşıma",
        "option_d": "Kamyon",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Trafikte sabır ve saygı neden önemlidir?",
        "option_a": "Ceza yememek için",
        "option_b": "Güvenliği artırır, kazaları önler",
        "option_c": "Hızlı gitmek için",
        "option_d": "Yakıt tasarrufu için",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Kış koşullarında hangi lastikler kullanılmalıdır?",
        "option_a": "Yaz lastiği",
        "option_b": "Kış lastiği",
        "option_c": "Dişsiz lastik",
        "option_d": "Patlak lastik",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Arıza halinde yol kenarında ne yapılmalıdır?",
        "option_a": "Üçgen reflektör yerleştirmek",
        "option_b": "Yolda beklemek",
        "option_c": "Aracı yol ortasında bırakmak",
        "option_d": "Farları kapatmak",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Seyir halinde emniyet şeridine girmek ne zaman serbesttir?",
        "option_a": "Hiçbir zaman",
        "option_b": "Acil durum ve görevli araçlar",
        "option_c": "Trafik yoğunsa",
        "option_d": "Hiçbiri",
        "correct": "B",
        "source": "seed",
    },
]


def seed():
    init_db(DB_PATH)
    added = 0
    for q in SAMPLE_QUESTIONS:
        if insert_question(DB_PATH, q):
            added += 1
    print(f"Seed eklendi: {added} soru")


if __name__ == "__main__":
    seed()