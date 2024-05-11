translations = {
    'uz': {
        "order_available_text": "Yo'lni tanlang! Siz qaysi shahardan qaysi shaharga sayohat qilmoqchisiz? Bizning xizmatimiz sizga kerakli joyga tez, qulay va xavfsiz yetkazib berishni ta'minlaydi. 🚖",
        "order_new_ride": "🚗 Buyurtma qilish",
        "change_language": "🌐 Tilni o'zgartirish",
        "be_driver": "Bu buyurtmani qabul qilish uchun siz haydovchi bo'lishingiz kerak!",
        "ride_canceled_reason": "Buyurtma bekor qilindi. Qayta mavjud. 🔄\n\nTavsif:",
        "Qabul qildim": "Qabul qilish",
        "order_recieved_message": "Rahmat, buyurtma qabul qilindi, haydovchilar tez orada siz bilan bog'lanishadi. Agar yangi buyurtma berishni xohlaysiz, iltimos, /yangi yozing.",
        "invalid_phone_number_text": "Noto'g'ri telefon raqami, qaytadan urinib ko'ring. Misol: +9989XXXXXXXXX",
        "homepage_text": "Assalomu alaykum! 🌟 Bizning xizmatimizga xush kelibsiz. Buyurtma berish uchun kerakli variantni tanlang yoki tilni o'zgartirish uchun tugmani bosing. 🚗🔄",
        "welcome_text": "Bizni xizmatimizga xush kelibsiz! 🌟",
        "order_desc_text": "Zakaz uchun tavsifni kiriting: 📝",
        "ask_phone_number_text": "Iltimos, telefon raqamingizni kiriting. Misol uchun: +9989XXXXXXXXX 📞",
        "driver_question": "Siz haydovchimisiz? 🚗",
        "yes_driver": "Ha, men haydovchiman!",
        "no_driver": "Yo'q, men yo'lovchiman!",
        "Accept the ride": "Qabul qilish ✅",
        "Cancel the ride": "Bekor qilish ❌",
    },
    'ru': {

        "order_available_text": "Выберите маршрут! Из какого города в какой город вы хотите путешествовать? Наш сервис обеспечит вас быстрой, удобной и безопасной доставкой в нужное вам место. 🚖",
        "order_new_ride": "🚗 Заказать новую поездку",
        "change_language": "🌐 Изменить язык",
        "be_driver": "Вы должны быть водителем, чтобы принять этот заказ!",
        "ride_canceled_reason": "Buyurtma bekor qilindi. Qayta mavjud. 🔄\n\nTavsif:",
        "Qabul qildim": "Qabul qilish",
        "order_recieved_message": "Спасибо, заказ сохранен, водители скоро свяжутся с вами. Если вы хотите сделать еще один заказ, введите /новый.",
        "invalid_phone_number_text": "Неверный номер телефона, попробуйте снова. Пример: +9989XXXXXXXXX",
        "homepage_text": "Добро пожаловать! 🌟 Добро пожаловать в наш сервис. Выберите нужный вариант для заказа или нажмите кнопку для изменения языка. 🚗🔄",
        "welcome_text": "Добро пожаловать в наше обслуживание! 🌟",
        "order_desc_text": "Введите описание заказа, пожалуйста: 📝",
        "ask_phone_number_text": "Пожалуйста, введите свой номер телефона. Например: +9989XXXXXXXXX 📞",
        "driver_question": "Вы водитель? 🚗",
        "no_driver": "Нет, я пассажир!",
        "yes_driver": "Да, я водитель!",
        "Accept the ride": "Принять поездку ✅",
        "Cancel the ride": "Отменить поездку ❌",
    }
}


def get_translation(text: str, lang: str = None) -> str:
    if lang and lang in translations.keys():
        return translations[lang].get(text, text)
    return text
