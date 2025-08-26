"""
questions.db içine örnek trafik soruları ekler (test amaçlı).
Kullanım:
  python seed_questions.py
"""

import os
from typing import Dict, List

from fetch_questions import DB_PATH, init_db, insert_question


SAMPLE_QUESTIONS: List[Dict] = [
    {
        "question": "Işıklı trafik işaret cihazında kırmızı ışık yanıyorsa ne yapılmalıdır?",
        "option_a": "Durulmalı ve beklenmeli",
        "option_b": "Hız azaltılarak dikkatli geçilmeli",
        "option_c": "Yaya yoksa geçilmeli",
        "option_d": "Sadece sağa dönüş yapılmalı",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Aşağıdakilerden hangisi geçiş üstünlüğüne sahiptir?",
        "option_a": "Toplu taşıma araçları",
        "option_b": "İtfaiye aracı",
        "option_c": "Okul servisi",
        "option_d": "Taksi",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Yerleşim yeri içinde iki yönlü karayolunda azami hız sınırı binek araçlar için kaç km/saattir?",
        "option_a": "30",
        "option_b": "50",
        "option_c": "70",
        "option_d": "90",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Aşağıdakilerden hangisi araçta bulundurulması zorunlu değilidir?",
        "option_a": "İlk yardım çantası",
        "option_b": "Yangın söndürücü",
        "option_c": "Stepne",
        "option_d": "Kar zinciri (yaz mevsimi)",
        "correct": "D",
        "source": "seed",
    },
    {
        "question": "Şerit değiştirmeden önce ilk yapılması gereken işlem nedir?",
        "option_a": "Sinyal vermek",
        "option_b": "Omuz üstü kontrol yapmak",
        "option_c": "Ayna kontrolü yapmak",
        "option_d": "Hızlanmak",
        "correct": "C",
        "source": "seed",
    },
    {
        "question": "Aracın fren mesafesini en çok etkileyen faktör hangisidir?",
        "option_a": "Lastik hava basıncı",
        "option_b": "Hava sıcaklığı",
        "option_c": "Araç rengi",
        "option_d": "Yakıt türü",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Aşağıdaki trafik işaretinin anlamı nedir? (Üçgen içinde ünlem)",
        "option_a": "Azami hız",
        "option_b": "Genel tehlike",
        "option_c": "Dur",
        "option_d": "Park yasağı",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Emniyet kemeri kullanımının amacı aşağıdakilerden hangisidir?",
        "option_a": "Yakıt tasarrufu sağlamak",
        "option_b": "Gürültüyü azaltmak",
        "option_c": "Kaza anında yaralanmayı azaltmak",
        "option_d": "Aracın performansını artırmak",
        "correct": "C",
        "source": "seed",
    },
    {
        "question": "Sağa dönüşlerde öncelik aşağıdakilerden hangisine aittir?",
        "option_a": "Karşıdan gelen araçlara",
        "option_b": "Soldan gelen araçlara",
        "option_c": "Yayalara",
        "option_d": "Hiçbirine",
        "correct": "C",
        "source": "seed",
    },
    {
        "question": "Aracınızı park ederken tekerleklerinizi kaldırıma ne şekilde konumlandırmalısınız?",
        "option_a": "Kaldırıma paralel ve yakın",
        "option_b": "Kaldırıma dik",
        "option_c": "Kaldırımdan uzak",
        "option_d": "Fark etmez",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Sisli havalarda hangi ışıkları kullanmalısınız?",
        "option_a": "Uzun farlar",
        "option_b": "Kısa farlar ve sis farları",
        "option_c": "Park lambaları",
        "option_d": "Hiçbiri",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Aşağıdakilerden hangisi takip mesafesini etkiler?",
        "option_a": "Sürücünün yaşı",
        "option_b": "Hava şartları",
        "option_c": "Araç rengi",
        "option_d": "Koltuk sayısı",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Kavşakta sola dönecek sürücü ilk olarak ne yapmalıdır?",
        "option_a": "Sola yaklaşmalı",
        "option_b": "Hızlanmalı",
        "option_c": "Korna çalmalı",
        "option_d": "Uzun far yakmalı",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Bir yaralıyı araçtan çıkarırken ilk dikkat edilmesi gereken nedir?",
        "option_a": "Hızlıca çekmek",
        "option_b": "Baş-boyun-gövde eksenini korumak",
        "option_c": "Önce ayaklarını çıkarmak",
        "option_d": "Önce kollarını çıkarmak",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Aşağıdakilerden hangisi geçiş hakkı kuralıdır?",
        "option_a": "Dönüş yapan araç düz giden araca yol verir",
        "option_b": "Düz giden araç dönüş yapana yol verir",
        "option_c": "Hiçbiri",
        "option_d": "Her zaman sağdaki geçer",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Okul geçidinde sürücüler ne yapmalıdır?",
        "option_a": "Hızlanmalı",
        "option_b": "Durup yayalara yol vermeli",
        "option_c": "Korna çalmalı",
        "option_d": "Geçiş üstünlüğü kullanmalı",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Aşağıdaki durumların hangisinde sollama yasaktır?",
        "option_a": "Tek yönlü yollarda",
        "option_b": "Dönemeçlerde ve tepe üstlerinde",
        "option_c": "Çevre yollarında",
        "option_d": "Otoyollarda",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Seyir halinde cep telefonu kullanmak neden tehlikelidir?",
        "option_a": "Yakıt tüketimini artırır",
        "option_b": "Dikkat dağınıklığına yol açar",
        "option_c": "Aracın frenlerini etkiler",
        "option_d": "Lastik aşınmasını artırır",
        "correct": "B",
        "source": "seed",
    },
    {
        "question": "Arka koltukta emniyet kemeri takmak zorunlu mudur?",
        "option_a": "Evet",
        "option_b": "Hayır",
        "option_c": "Sadece uzun yolda",
        "option_d": "Sadece şehir içinde",
        "correct": "A",
        "source": "seed",
    },
    {
        "question": "Aşağıdaki işaretin anlamı nedir? (Mavi zemin, beyaz P)",
        "option_a": "Park yasağı",
        "option_b": "Park yeri",
        "option_c": "Dur",
        "option_d": "Yol ver",
        "correct": "B",
        "source": "seed",
    },
]


def seed(db_path: str = DB_PATH) -> int:
    init_db(db_path)
    added = 0
    for q in SAMPLE_QUESTIONS:
        if insert_question(db_path, q):
            added += 1
    print(f"Eklendi: {added} soru (seed)")
    return added


if __name__ == "__main__":
    seed()