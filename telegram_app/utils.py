import json
from django.db import transaction
from .models import BotUser, RidePost, Road, RoadTranslation, TelegramGroup
from .credentials import BOT_TOKEN
import requests
from .translation import get_translation
import re


class BotService:
    def __init__(self, update):
        self.update = update
        self.message = update.get('message', {})
        self.callback_query = update.get('callback_query', {})
        self.user_id = self.get_user_id()
        self.message_id = self.get_message_id()
        self.chat = self.message.get('chat', {})
        self.chat_type = self.chat.get('type', '')
        self.chat_id = str(self.chat.get('id', ''))
        self.user_obj = None

    def get_user_id(self):
        if self.callback_query:
            return self.callback_query.get('from', {}).get('id')
        return self.message.get('from', {}).get('id')

    def get_message_id(self):
        if self.callback_query:
            return self.callback_query.get('message', {}).get('message_id')
        return self.message.get('message_id')

    def send_message(self, chat_id, text, parse_mode='Markdown', reply_markup=None, remove_keyboard=False):
        payload = {
            'chat_id': chat_id,
            'text': get_translation(text),
            'parse_mode': parse_mode
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup

        return self.make_telegram_request('sendMessage', payload)

    def make_telegram_request(self, method, payload):
        token = BOT_TOKEN
        url = f"https://api.telegram.org/bot{token}/{method}"
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    def delete_message(self, chat_id, message_id):
        payload = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        return self.make_telegram_request('deleteMessage', payload)

    def post_to_group(self, ride_description: str, road_id: int) -> dict:
        if self.user_obj.phone_number:
            try:
                selected_road = Road.objects.get(id=road_id)
                post = RidePost.objects.create(
                    ordered_by=self.user_obj,
                    description=ride_description,
                    posted_on_group=selected_road.group
                )

                text = f"<b>Yangi zakaz:</b> #RideID_{post.id},\n<b>Qo'shimcha ma'lumot: </b>{post.description},\nQabul qilganizdan so'ng klient ni telefon raqamini ko'rishingiz mumkun."
                keyboard = [
                    [{"text": get_translation("Accept the ride", lang=self.user_obj.lang),
                        "callback_data": f"accept_ride_post_{post.id}"}],
                ]
                reply_markup = json.dumps({"inline_keyboard": keyboard})

                return self.send_message(chat_id=selected_road.group.chat_id,
                                         text=text, parse_mode='HTML', reply_markup=reply_markup)
            except:
                return False

        self.user_obj.state = "awaiting_phone_number"
        self.user_obj.save()
        self.prompt_for_phone_number(self.user_obj)
        return False

    def accept_ride_post(self, ride_id: int, completed=False) -> dict:
        try:
            if completed:
                ride = RidePost.objects.get(id=ride_id)
                ride.is_active = False
                ride.accepted_by = self.user_obj
                ride.save()
                updated_text = f"<b>Zakaz Nomer:</b> #RideID_{ride.id}, \n<b>Zakaz qilingan:</b> {ride.ordered_by},\n<b>Qabul qilindi (Haydovchi):</b> {self.user_obj.phone_number}!"
                self.edit_message_text(chat_id=self.user_id,
                                       message_id=self.message_id, text=updated_text, parse_mode="HTML")
                return True, "The ride is completed!", ride

            ride = RidePost.objects.get(id=ride_id)
            ride.accepted_by = self.user_obj
            ride.group_message_id = self.message_id
            ride.save()
            updated_text = f"<b>Zakaz Nomer:</b> #RideID_{ride.id}, \n<b>Zakaz qilingan:</b> {ride.ordered_by},\n<b>Qabul qilish jarayonida (Haydovchi):</b> {self.user_obj.phone_number}!"
            text = f"<b>Yangi zakaz:</b> #RideID_{ride.id}\n<b>Telefon raqam:</b> {ride.ordered_by.phone_number},\n<b>Qo'shimcha ma'lumot: </b>{ride.description}"

            keyboard = [
                [
                    {"text": get_translation("Accept the ride", lang=self.user_obj.lang),
                        "callback_data": f"accepted_ride_post_{ride.id}"},
                    {"text": get_translation("Cancel the ride", lang=self.user_obj.lang),
                        "callback_data": f"cancel_ride_post_{ride.id}"}
                ],
            ]
            reply_markup = json.dumps({"inline_keyboard": keyboard})

            self.send_message(chat_id=self.user_id,
                              text=text, parse_mode='HTML', reply_markup=reply_markup)
            return self.edit_message_text(chat_id=ride.posted_on_group.chat_id, message_id=self.message_id, text=updated_text, parse_mode="HTML")

        except:
            return False, "Ride not found!"

    def cancel_ride_post(self, ride_id: int) -> dict:
        try:
            ride = RidePost.objects.get(id=ride_id)

            if ride.is_active:
                ride.is_active = True
                ride.accepted_by = None
                ride.save()
                text = get_translation(
                    "ride_canceled_reason", lang=self.user_obj.lang)
                cancel_text = f"{text} {ride.description}"
                self.edit_message_text(
                    ride.posted_on_group.chat_id, ride.group_message_id, cancel_text)

                self.edit_message_text(
                    self.user_id, self.message_id, cancel_text)
                return self.post_to_group(ride.description, ride.posted_on_group.id)
            else:
                cancel_text = get_translation(
                    "ride_canceled_reason", lang=self.user_obj.lang)
                self.edit_message_text(
                    ride.posted_on_group.chat_id, ride.message_id, cancel_text)

                return {
                    'success': True,
                    'message': 'Ride post cancelled and re-posted to the group!'
                }
        except RidePost.DoesNotExist:
            return {
                'success': False,
                'message': 'Ride post not found!'
            }

    def edit_message_text(self, chat_id, message_id, text, parse_mode="Markdown"):
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': parse_mode,
        }
        return self.make_telegram_request('editMessageText', payload)

    def get_or_register_group(self):
        if self.chat_type in ['group', 'supergroup']:
            telegram_group, created = TelegramGroup.objects.get_or_create(
                chat_id=self.chat_id,
                defaults={'title': self.chat.get('title', '')}
            )
            return telegram_group
        return None

    def process_telegram_update(self):

        if self.chat_type in ['group', 'supergroup']:
            self.get_or_register_group()
            self.handle_group_message()
            return True, "Group interaction processed."

        user, created = BotUser.objects.get_or_create(
            user_id=str(self.user_id)
        )
        if created:
            user.state = "new"
            user.save()
        self.user_obj = user
        text = get_translation(self.message.get(
            "text", None), lang=self.user_obj.lang)
        if self.callback_query:
            data = self.callback_query.get('data')
            self.handle_callback_query(user, data)
        elif text == get_translation("change_language", lang=user.lang):
            self.ask_for_language(user, is_new=False)
        elif text == get_translation('/start') or user.state == 'awaiting_user_language' or user.state == 'only_change_language' or user.state == "new":
            self.ask_for_language(user)
        elif user.state == 'awaiting_driver_status':
            self.handle_driver_status(user)
        elif user.state == 'awaiting_phone_number':
            self.handle_phone_number(user)
        elif user.state and "awaiting_for_desc" in user.state:
            self.handle_passanger_order(user)
        elif text == get_translation("order_new_ride", lang=user.lang):
            self.display_available_rides()
        else:
            self.handle_default()

        return True, "Processed"

    def handle_group_message(self):
        text = self.message.get("text", None)
        caption = self.message.get("caption", None)
        user = BotUser.objects.filter(user_id=self.user_id).first()
        print(user, self.user_id)
        if user:
            is_admin = user.is_admin
        else:
            is_admin = False
        if caption and not is_admin:
            if caption and (self.contains_link(caption) or self.contains_phone_number(caption)):
                self.delete_message(self.chat_id, self.message_id)
                return
        if text and not is_admin:
            if self.contains_link(text) or self.contains_phone_number(text):
                self.delete_message(self.chat_id, self.message_id)

    def contains_link(self, text):
        # Regular expression to match a URL
        url_pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        return bool(re.search(url_pattern, text))

    def contains_phone_number(self, text):
        # Regular expression to match a phone number in various formats
        phone_pattern = r"\b(?:\+\d{1,3}\s*)?\d{3,5}\s*\d{2,4}\s*\d{2,4}\s*\d{2,4}\b"
        return bool(re.search(phone_pattern, text))

    def send_photo(self, payload):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # This will raise an error for HTTP error responses
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Failed to send photo: {str(e)}'
            }

    def handle_callback_query(self, user, data):
        if data == "order_new_ride":
            return self.handle_default()

        if data == 'set_driver_yes':
            user.is_driver = True
            user.state = 'awaiting_phone_number'
            user.save()
            self.delete_message(self.user_id, self.message_id)
            self.prompt_for_phone_number(user)
        elif data == 'set_driver_no':
            user.is_driver = False
            user.state = 'awaiting_phone_number'
            user.save()
            self.delete_message(self.user_id, self.message_id)
            self.prompt_for_phone_number(user)
        elif "accept_ride_post" in data:
            if self.user_obj.is_driver:
                ride_id = data.split("_")[-1]
                self.accept_ride_post(ride_id)
                print("on root", self.message_id)
            else:
                self.send_message(
                    self.user_id, get_translation('be_driver', lang=self.user_obj.lang))
                self.handle_driver_status(user)
        elif "accepted_ride_post" in data:
            ride_id = data.split("_")[-1]
            success, _, ride = self.accept_ride_post(ride_id, completed=True)
            updated_text = f"<b>Zakaz Nomer:</b> #RideID_{ride.id}, \n<b>Zakaz qilganasdf:</b> {ride.ordered_by},\n<b>Qabul qilindi (Haydovchi):</b> {self.user_obj.phone_number}!"
            return self.edit_message_text(chat_id=ride.posted_on_group.chat_id, message_id=ride.group_message_id, text=updated_text, parse_mode="HTML")

        elif "cancel_ride_post" in data:
            ride_id = data.split("_")[-1]
            self.cancel_ride_post(ride_id)
        elif "order" in data:
            user.state = f'awaiting_for_desc_for_{data}'
            user.save()
            self.delete_message(self.user_id, self.message_id)
            self.prompt_for_order_desc(user)
        elif "set_lang" in data:
            user.lang = data.split("_")[-1]
            if user.state == "only_change_language":
                user.state = ""
                user.save()
                self.delete_message(self.user_id, self.message_id)
                return self.handle_default()
            else:
                user.state = 'awaiting_driver_status'
            user.save()
            self.delete_message(self.user_id, self.message_id)
            return self.handle_driver_status(user)
        else:
            return False, "Invalid callback data."

        return True, "Driver status set and asking for phone number."

    def handle_driver_status(self, user):
        user.state = 'awaiting_driver_status'
        user.save()
        keyboard = [
            [{"text": get_translation(
                "yes_driver", lang=user.lang), "callback_data": "set_driver_yes"}],
            [{"text": get_translation(
                "no_driver", lang=user.lang), "callback_data": "set_driver_no"}]
        ]
        reply_markup = json.dumps({"inline_keyboard": keyboard})
        self.send_message(self.user_id, get_translation(
            "driver_question", lang=user.lang),
            reply_markup=reply_markup)

    def ask_for_language(self, user, is_new=True):
        if is_new:
            user.state = 'awaiting_user_language'
        else:
            user.state = 'only_change_language'
        user.save()

        keyboard = [
            [{"text": "🇺🇿 O'zbekcha", "callback_data": "set_lang_uz"}],
            [{"text": "🇷🇺 Русский", "callback_data": "set_lang_ru"}]
        ]

        reply_markup = json.dumps({"inline_keyboard": keyboard})
        self.send_message(self.user_id, "Tilni tanlang / Выберите язык:",
                          reply_markup=reply_markup, remove_keyboard=True)

    def prompt_for_phone_number(self, user):
        self.send_message(self.user_id, get_translation(
            "ask_phone_number_text", lang=user.lang))

    def prompt_for_order_desc(self, user):
        self.send_message(
            self.user_id, get_translation("order_desc_text", lang=user.lang))

    def handle_default(self):
        if not self.user_obj.state:
            return self.home_keywoards()

        return self.send_message(
            self.user_id, get_translation("welcome_text", lang=self.user_obj.lang))

    def home_keywoards(self):
        reply_keyboard = {
            "keyboard": [
                [
                    {"text": get_translation(
                        "order_new_ride", lang=self.user_obj.lang)},
                    {"text": get_translation(
                        "change_language", lang=self.user_obj.lang)}
                ]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        reply_markup_reply = json.dumps(reply_keyboard)

        self.send_message(
            self.user_id, get_translation("homepage_text", lang=self.user_obj.lang), reply_markup=reply_markup_reply)

    def get_translated_roads(self, lang='uz'):
        translations = RoadTranslation.objects.filter(
            language=lang).values_list('road_id', 'translated_name')
        translation_map = {
            road_id: translated_name for road_id, translated_name in translations}

        roads = Road.objects.all()
        translated_roads = {road.id: translation_map.get(
            road.id, road.road_name) for road in roads}
        return translated_roads

    def display_available_rides(self):
        translated_roads = self.get_translated_roads(lang=self.user_obj.lang)
        inline_keyboard = self.change_obj_to_dynamic_key(
            translated_roads, "order")
        reply_markup = json.dumps({"inline_keyboard": inline_keyboard})
        self.send_message(
            self.user_id, get_translation("order_available_text", lang=self.user_obj.lang), reply_markup=reply_markup)

    def change_obj_to_dynamic_key(self, obj, key):
        items = [
            {'text': v, 'callback_data': f"{key}_{k}"}
            for k, v in obj.items()
        ]
        return [items[i:i + 2] for i in range(0, len(items), 2)]

    def handle_phone_number(self, user):
        phone_number = self.message.get('text').strip()
        if self.validate_phone_number(phone_number):
            user.phone_number = phone_number
            user.state = ''
            user.save()

            return self.handle_default()
        else:
            return self.send_message(
                self.user_id, get_translation("invalid_phone_number_text", lang=user.lang))

    def handle_passanger_order(self, user):
        description = self.message.get('text').strip()
        road_id = user.state.split("_")[-1]
        if self.post_to_group(description, road_id):
            user.state = ''
            user.save()
            self.send_message(
                self.user_id, get_translation("order_recieved_message", lang=user.lang))
            return True, "Posted to group"
        return False, "Something went wrong!"

    def validate_phone_number(self, phone_number):
        if phone_number.startswith("+998") and len(phone_number) == 13:
            return phone_number[4:].isdigit()
        return False
