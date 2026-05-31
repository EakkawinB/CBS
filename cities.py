"""77 จังหวัด + พิกัด + ชื่อภาษาอังกฤษสำหรับ OpenWeather"""

CITIES: dict[str, dict] = {
    "กรุงเทพ": {"lat": 13.7563, "lon": 100.5018, "en": "Bangkok"},
    "กระบี่": {"lat": 8.0863, "lon": 98.9063, "en": "Krabi"},
    "กาญจนบุรี": {"lat": 14.0227, "lon": 99.5328, "en": "Kanchanaburi"},
    "กาฬสินธุ์": {"lat": 16.4322, "lon": 103.5065, "en": "Kalasin"},
    "กำแพงเพชร": {"lat": 16.4828, "lon": 99.5227, "en": "Kamphaeng Phet"},
    "ขอนแก่น": {"lat": 16.4322, "lon": 102.8236, "en": "Khon Kaen"},
    "จันทบุรี": {"lat": 12.6083, "lon": 102.1035, "en": "Chanthaburi"},
    "ฉะเชิงเทรา": {"lat": 13.6888, "lon": 101.0713, "en": "Chachoengsao"},
    "ชลบุรี": {"lat": 13.3611, "lon": 100.9847, "en": "Chon Buri"},
    "ชัยนาท": {"lat": 15.1852, "lon": 100.1251, "en": "Chai Nat"},
    "ชัยภูมิ": {"lat": 15.8105, "lon": 102.0378, "en": "Chaiyaphum"},
    "ชุมพร": {"lat": 10.4930, "lon": 99.1800, "en": "Chumphon"},
    "เชียงราย": {"lat": 19.9071, "lon": 99.8310, "en": "Chiang Rai"},
    "เชียงใหม่": {"lat": 18.7883, "lon": 98.9853, "en": "Chiang Mai"},
    "ตรัง": {"lat": 7.5563, "lon": 99.6114, "en": "Trang"},
    "ตราด": {"lat": 12.2428, "lon": 102.5175, "en": "Trat"},
    "ตาก": {"lat": 16.8831, "lon": 99.1235, "en": "Tak"},
    "นครนายก": {"lat": 14.2069, "lon": 101.2131, "en": "Nakhon Nayok"},
    "นครปฐม": {"lat": 13.8140, "lon": 100.0373, "en": "Nakhon Pathom"},
    "นครพนม": {"lat": 17.3998, "lon": 104.7695, "en": "Nakhon Phanom"},
    "นครราชสีมา": {"lat": 14.9738, "lon": 102.0836, "en": "Nakhon Ratchasima"},
    "นครศรีธรรมราช": {"lat": 8.4325, "lon": 99.9631, "en": "Nakhon Si Thammarat"},
    "นครสวรรค์": {"lat": 15.7025, "lon": 100.1372, "en": "Nakhon Sawan"},
    "นนทบุรี": {"lat": 13.8591, "lon": 100.4923, "en": "Nonthaburi"},
    "นราธิวาส": {"lat": 6.4255, "lon": 101.8234, "en": "Narathiwat"},
    "น่าน": {"lat": 18.7834, "lon": 100.7711, "en": "Nan"},
    "บึงกาฬ": {"lat": 18.3570, "lon": 103.6552, "en": "Bueng Kan"},
    "บุรีรัมย์": {"lat": 14.9951, "lon": 103.1021, "en": "Buriram"},
    "ปทุมธานี": {"lat": 14.0208, "lon": 100.5250, "en": "Pathum Thani"},
    "ประจวบคีรีขันธ์": {"lat": 11.8124, "lon": 99.7972, "en": "Prachuap Khiri Khan"},
    "ปราจีนบุรี": {"lat": 14.0489, "lon": 101.3726, "en": "Prachin Buri"},
    "ปัตตานี": {"lat": 6.8704, "lon": 101.2486, "en": "Pattani"},
    "พระนครศรีอยุธยา": {"lat": 14.3532, "lon": 100.5693, "en": "Phra Nakhon Si Ayutthaya"},
    "พะเยา": {"lat": 19.1658, "lon": 99.9031, "en": "Phayao"},
    "พังงา": {"lat": 8.4501, "lon": 98.5255, "en": "Phang Nga"},
    "พัทลุง": {"lat": 7.6167, "lon": 100.0740, "en": "Phatthalung"},
    "พิจิตร": {"lat": 16.4406, "lon": 100.3488, "en": "Phichit"},
    "พิษณุโลก": {"lat": 16.8211, "lon": 100.2659, "en": "Phitsanulok"},
    "เพชรบุรี": {"lat": 13.1118, "lon": 99.9442, "en": "Phetchaburi"},
    "เพชรบูรณ์": {"lat": 16.4194, "lon": 101.1557, "en": "Phetchabun"},
    "แพร่": {"lat": 18.1446, "lon": 100.1412, "en": "Phrae"},
    "ภูเก็ต": {"lat": 7.8804, "lon": 98.3923, "en": "Phuket"},
    "มหาสารคาม": {"lat": 16.1850, "lon": 103.3005, "en": "Maha Sarakham"},
    "มุกดาหาร": {"lat": 16.5436, "lon": 104.7245, "en": "Mukdahan"},
    "แม่ฮ่องสอน": {"lat": 19.3000, "lon": 97.9683, "en": "Mae Hong Son"},
    "ยโสธร": {"lat": 15.7930, "lon": 104.1453, "en": "Yasothon"},
    "ยะลา": {"lat": 6.5399, "lon": 101.2813, "en": "Yala"},
    "ร้อยเอ็ด": {"lat": 16.0538, "lon": 103.6520, "en": "Roi Et"},
    "ระนอง": {"lat": 9.9529, "lon": 98.6300, "en": "Ranong"},
    "ระยอง": {"lat": 12.6831, "lon": 101.2816, "en": "Rayong"},
    "ราชบุรี": {"lat": 13.5365, "lon": 99.8144, "en": "Ratchaburi"},
    "ลพบุรี": {"lat": 14.7995, "lon": 100.6534, "en": "Lop Buri"},
    "ลำปาง": {"lat": 18.2893, "lon": 99.4933, "en": "Lampang"},
    "ลำพูน": {"lat": 18.5772, "lon": 98.9912, "en": "Lamphun"},
    "เลย": {"lat": 17.4860, "lon": 101.7223, "en": "Loei"},
    "ศรีสะเกษ": {"lat": 15.1152, "lon": 104.3217, "en": "Sisaket"},
    "สกลนคร": {"lat": 17.1557, "lon": 104.1486, "en": "Sakon Nakhon"},
    "สงขลา": {"lat": 7.1898, "lon": 100.5954, "en": "Songkhla"},
    "สตูล": {"lat": 6.6114, "lon": 100.0631, "en": "Satun"},
    "สมุทรปราการ": {"lat": 13.5991, "lon": 100.5968, "en": "Samut Prakan"},
    "สมุทรสงคราม": {"lat": 13.4098, "lon": 100.0023, "en": "Samut Songkhram"},
    "สมุทรสาคร": {"lat": 13.5475, "lon": 100.2744, "en": "Samut Sakhon"},
    "สระแก้ว": {"lat": 13.8240, "lon": 102.0646, "en": "Sa Kaeo"},
    "สระบุรี": {"lat": 14.5289, "lon": 100.9123, "en": "Saraburi"},
    "สิงห์บุรี": {"lat": 14.8936, "lon": 100.3967, "en": "Sing Buri"},
    "สุพรรณบุรี": {"lat": 14.4746, "lon": 100.1222, "en": "Suphan Buri"},
    "สุราษฎร์ธานี": {"lat": 9.1396, "lon": 99.3215, "en": "Surat Thani"},
    "สุรินทร์": {"lat": 14.8814, "lon": 103.4937, "en": "Surin"},
    "หนองคาย": {"lat": 17.8782, "lon": 102.7413, "en": "Nong Khai"},
    "หนองบัวลำภู": {"lat": 17.2025, "lon": 102.4385, "en": "Nong Bua Lamphu"},
    "อ่างทอง": {"lat": 14.5896, "lon": 100.4551, "en": "Ang Thong"},
    "อำนาจเจริญ": {"lat": 15.8606, "lon": 104.6258, "en": "Amnat Charoen"},
    "อุดรธานี": {"lat": 17.4150, "lon": 102.7859, "en": "Udon Thani"},
    "อุตรดิตถ์": {"lat": 17.6201, "lon": 100.0957, "en": "Uttaradit"},
    "อุทัยธานี": {"lat": 15.3835, "lon": 100.0247, "en": "Uthai Thani"},
    "อุบลราชธานี": {"lat": 15.2287, "lon": 104.8564, "en": "Ubon Ratchathani"},
}


def get_coords(city: str) -> tuple[float, float] | None:
    info = CITIES.get(city)
    if not info:
        return None
    return info["lat"], info["lon"]


def get_weather_query(city: str) -> str:
    info = CITIES.get(city)
    if not info:
        return city
    return info["en"]
