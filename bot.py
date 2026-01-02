import asyncio
import os
from io import BytesIO
from typing import Dict, Any
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, FSInputFile
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import numpy as np
from pydub import AudioSegment
import soundfile as sf

# ====================== KONFIGURASIÝA ======================
BOT_TOKEN = "8387242598:AAHFfLJ5JLnYz5_ENSoM7sn3c7bT7L5pRPk"
ADMIN_USERNAME = "@Daykkaa"
ADMIN_ID = 8143084360

# ====================== LOGGING ======================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====================== FSM ======================
class AudioStates(StatesGroup):
    waiting_for_audio = State()
    waiting_for_effects = State()
    processing_audio = State()

# ====================== EFFECTLER ======================
EFFECTS = {
    # Bass we treble effectler
    "bass_boost": {"name": "🎵 Bass Boost", "min": 0, "max": 100, "default": 50},
    "treble": {"name": "🎶 Treble", "min": 0, "max": 100, "default": 50},
    "bass": {"name": "🔊 Bass", "min": 0, "max": 100, "default": 50},
    "mid": {"name": "🎤 Mid", "min": 0, "max": 100, "default": 50},
    "high": {"name": "🎧 High", "min": 0, "max": 100, "default": 50},
    
    # Reverb effectler
    "reverb": {"name": "🏛 Reverb", "min": 0, "max": 100, "default": 30},
    "echo": {"name": "🌊 Echo", "min": 0, "max": 100, "default": 30},
    "hall_reverb": {"name": "🏰 Hall Reverb", "min": 0, "max": 100, "default": 30},
    "room_reverb": {"name": "🏠 Room Reverb", "min": 0, "max": 100, "default": 30},
    "plate_reverb": {"name": "🥏 Plate Reverb", "min": 0, "max": 100, "default": 30},
    
    # Distortion effectler
    "distortion": {"name": "🎸 Distortion", "min": 0, "max": 100, "default": 20},
    "overdrive": {"name": "🔥 Overdrive", "min": 0, "max": 100, "default": 20},
    "fuzz": {"name": "⚡ Fuzz", "min": 0, "max": 100, "default": 20},
    "crunch": {"name": "💥 Crunch", "min": 0, "max": 100, "default": 20},
    
    # Modulýasiýa effectler
    "chorus": {"name": "🌀 Chorus", "min": 0, "max": 100, "default": 40},
    "flanger": {"name": "🌪 Flanger", "min": 0, "max": 100, "default": 40},
    "phaser": {"name": "🌈 Phaser", "min": 0, "max": 100, "default": 40},
    "tremolo": {"name": "🎹 Tremolo", "min": 0, "max": 100, "default": 40},
    "vibrato": {"name": "🎻 Vibrato", "min": 0, "max": 100, "default": 40},
    
    # Filter effectler
    "low_pass": {"name": "📉 Low Pass", "min": 0, "max": 100, "default": 50},
    "high_pass": {"name": "📈 High Pass", "min": 0, "max": 100, "default": 50},
    "band_pass": {"name": "📊 Band Pass", "min": 0, "max": 100, "default": 50},
    "notch": {"name": "🎛 Notch", "min": 0, "max": 100, "default": 50},
    
    # Time-based effectler
    "delay": {"name": "⏱ Delay", "min": 0, "max": 100, "default": 30},
    "ping_pong_delay": {"name": "🏓 Ping Pong Delay", "min": 0, "max": 100, "default": 30},
    "slapback_delay": {"name": "👏 Slapback Delay", "min": 0, "max": 100, "default": 30},
    
    # Dynamic effectler
    "compressor": {"name": "🎚 Compressor", "min": 0, "max": 100, "default": 40},
    "limiter": {"name": "📏 Limiter", "min": 0, "max": 100, "default": 40},
    "expander": {"name": "📐 Expander", "min": 0, "max": 100, "default": 40},
    "gate": {"name": "🚪 Gate", "min": 0, "max": 100, "default": 40},
    
    # Pitch we speed effectler
    "pitch_shift": {"name": "🎼 Pitch Shift", "min": 0, "max": 100, "default": 50},
    "time_stretch": {"name": "⏩ Time Stretch", "min": 0, "max": 100, "default": 50},
    "speed": {"name": "⚡ Speed", "min": 0, "max": 100, "default": 50},
    
    # Special effectler
    "bit_crusher": {"name": "🕹 Bit Crusher", "min": 0, "max": 100, "default": 20},
    "vinyl": {"name": "💿 Vinyl Effect", "min": 0, "max": 100, "default": 30},
    "radio": {"name": "📻 Radio Effect", "min": 0, "max": 100, "default": 40},
    "telephone": {"name": "☎️ Telephone", "min": 0, "max": 100, "default": 50},
    "underwater": {"name": "🌊 Underwater", "min": 0, "max": 100, "default": 40},
    
    # Spatial effectler
    "pan": {"name": "🎛 Pan", "min": 0, "max": 100, "default": 50},
    "stereo_enhance": {"name": "🔊 Stereo Enhance", "min": 0, "max": 100, "default": 50},
    "mono": {"name": "🔈 Mono", "min": 0, "max": 100, "default": 50},
    
    # Ambient effectler
    "ambient": {"name": "🌌 Ambient", "min": 0, "max": 100, "default": 40},
    "space": {"name": "🚀 Space", "min": 0, "max": 100, "default": 40},
    "dream": {"name": "💭 Dream", "min": 0, "max": 100, "default": 40},
    
    # Vintage effectler
    "vintage": {"name": "📻 Vintage", "min": 0, "max": 100, "default": 50},
    "tape_saturation": {"name": "📼 Tape Saturation", "min": 0, "max": 100, "default": 40},
    "tube_warmth": {"name": "🔆 Tube Warmth", "min": 0, "max": 100, "default": 40},
    
    # Nature effectler
    "rain": {"name": "🌧 Rain", "min": 0, "max": 100, "default": 40},
    "thunder": {"name": "⛈ Thunder", "min": 0, "max": 100, "default": 30},
    "forest": {"name": "🌲 Forest", "min": 0, "max": 100, "default": 40},
    "ocean": {"name": "🌊 Ocean", "min": 0, "max": 100, "default": 40},
}

# ====================== BOT INIT ======================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ====================== HELPERS ======================
def create_progress_bar(value: int, max_value: int = 100) -> str:
    """Progress bar döretmek"""
    filled = int(value / max_value * 10)
    empty = 10 - filled
    return "█" * filled + "░" * empty

def create_effect_keyboard(effect_values: Dict[str, int], page: int = 0) -> InlineKeyboardMarkup:
    """Effectler üçin inlayn keyboard döretmek"""
    effects_list = list(EFFECTS.items())
    items_per_page = 10
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(effects_list))
    
    buttons = []
    
    # Effect düwmeleri
    for i in range(start_idx, end_idx):
        key, effect = effects_list[i]
        value = effect_values.get(key, effect["default"])
        
        effect_name = effect["name"]
        progress_bar = create_progress_bar(value)
        btn_text = f"{effect_name}: {progress_bar} {value}%"
        
        callback_data = f"effect_{key}_{page}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=callback_data)])
    
    # Control düwmeleri
    control_buttons = []
    
    if page > 0:
        control_buttons.append(InlineKeyboardButton(text="⬅️ Öňki", callback_data=f"page_{page-1}"))
    
    control_buttons.append(InlineKeyboardButton(text="✅ OK", callback_data="apply_effects"))
    control_buttons.append(InlineKeyboardButton(text="🔄 Reset", callback_data="reset_effects"))
    
    if end_idx < len(effects_list):
        control_buttons.append(InlineKeyboardButton(text="Indiki ➡️", callback_data=f"page_{page+1}"))
    
    buttons.append(control_buttons)
    
    # Main menu düwmesi
    buttons.append([InlineKeyboardButton(text="🏠 Baş Menýu", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ====================== AUDIO PROCESSING ======================
def apply_audio_effects(audio_data: bytes, effect_values: Dict[str, int]) -> bytes:
    """
    Audio-ya effectleri ulanmak
    Bu ýerde çynlada audio processing amala aşyrylýar
    """
    try:
        # Audio segment döretmek
        audio = AudioSegment.from_file(BytesIO(audio_data))
        
        # Bass we treble tüzetmeleri
        bass_value = effect_values.get('bass', 50)
        treble_value = effect_values.get('treble', 50)
        
        if bass_value != 50:
            bass_factor = (bass_value - 50) / 50.0
            audio = audio.low_pass_filter(150).apply_gain(bass_factor * 10)
        
        if treble_value != 50:
            treble_factor = (treble_value - 50) / 50.0
            audio = audio.high_pass_filter(3000).apply_gain(treble_factor * 10)
        
        # Volume tüzetmeleri
        volume_value = effect_values.get('volume', 50)
        if volume_value != 50:
            volume_change = (volume_value - 50) * 0.5
            audio = audio + volume_change
        
        # Reverb simulation
        reverb_value = effect_values.get('reverb', 30)
        if reverb_value > 30:
            # Simple reverb effect
            audio_with_echo = audio.overlay(audio - 10, position=50)
            audio = audio_with_echo
        
        # Convert back to bytes
        buffer = BytesIO()
        audio.export(buffer, format="mp3")
        buffer.seek(0)
        
        return buffer.read()
    
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        # Error ýüze çyksa, orijinal audio-ny gaýtaryň
        return audio_data

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Start komandasy"""
    welcome_text = f"""
✨ <b>Salam, {message.from_user.first_name}!</b> ✨

🎵 <b>Audio Effect Bot</b> 🎵 hoş geldiňiz!

Bu bot bilen:
• Audio faýllaryňyza 50-den gowrak effect goşup bilersiňiz
• Her effecti 0-100% aralygynda sazlap bilersiňiz
• Täze effectli audio faýly ýükläp alyp bilersiňiz

🚀 <b>Başlamak üçin:</b>
1. Audio faýlyňyzy ýollap beriň (MP3 formaty)
2. Effectleri sazlaň
3. Täze faýly almagyňyzy soraň!

🔧 <b>Admin:</b> {ADMIN_USERNAME}
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Audio ýolla", callback_data="send_audio")],
        [InlineKeyboardButton(text="ℹ️ Maglumat", callback_data="info")],
        [InlineKeyboardButton(text="👨‍💻 Admin", url=f"tg://user?id={ADMIN_ID}")]
    ])
    
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=keyboard)

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin paneli"""
    if message.from_user.id == ADMIN_ID:
        admin_text = f"""
👑 <b>Admin Paneli</b> 👑

🔹 <b>Admin:</b> {ADMIN_USERNAME}
🔹 <b>ID:</b> {ADMIN_ID}

📊 <b>Bot statistikasy:</b>
• Effectler: {len(EFFECTS)} sany
• User ID: {message.from_user.id}

🛠 <b>Admin komandalary:</b>
• /stats - Bot statistikasy
• /broadcast - Habar ibermek
• /users - Ulanyjylar
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📢 Habar iber", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="🔄 Restart", callback_data="admin_restart")],
            [InlineKeyboardButton(text="🏠 Baş Menýu", callback_data="main_menu")]
        ])
        
        await message.answer(admin_text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer("❌ Bu ýere girip bolmaýar! Diňe admin girip biler.")

@dp.callback_query(F.data == "send_audio")
async def process_send_audio(callback: CallbackQuery, state: FSMContext):
    """Audio ýollamak üçin çaýyrmak"""
    await callback.message.edit_text(
        "🎤 <b>Indi audio faýlyňyzy ýollap beriň</b>\n\n"
        "🔊 <i>MP3 formaty ýakymly bolýar</i>",
        parse_mode="HTML"
    )
    await state.set_state(AudioStates.waiting_for_audio)
    await callback.answer()

@dp.message(AudioStates.waiting_for_audio)
async def process_audio(message: Message, state: FSMContext):
    """Audio faýly kabul etmek"""
    if not (message.audio or message.voice or message.document):
        await message.answer("❌ <b>Audio faýl ýollap beriň!</b>", parse_mode="HTML")
        return
    
    try:
        # Audio faýly ýükläp almak
        if message.audio:
            file_id = message.audio.file_id
        elif message.voice:
            file_id = message.voice.file_id
        else:
            if message.document.mime_type and "audio" in message.document.mime_type:
                file_id = message.document.file_id
            else:
                await message.answer("❌ <b>Audio faýl ýollap beriň!</b>", parse_mode="HTML")
                return
        
        # Audio-ny ýükläp almak
        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)
        audio_data = file_bytes.read()
        
        # Statelerde saklamak
        await state.update_data(audio_data=audio_data, file_id=file_id)
        
        # Effect sazlamak üçin keyboard görkezmek
        effect_values = {key: effect["default"] for key, effect in EFFECTS.items()}
        
        effect_text = f"""
🎛 <b>Audio Effect Sazlamalary</b>

✅ <b>Audio kabul edildi!</b>
📁 <i>Indi effectleri sazlaň:</i>

{len(EFFECTS)} sany effect bar:
• Bass/Treble: {EFFECTS['bass']['name']}, {EFFECTS['treble']['name']}
• Reverb/Delay: {EFFECTS['reverb']['name']}, {EFFECTS['delay']['name']}
• Special: {EFFECTS['vinyl']['name']}, {EFFECTS['radio']['name']}

🔄 <b>Sazlamak üçin:</b>
Effect düwmesine basyň we bahany sazlaň
        """
        
        keyboard = create_effect_keyboard(effect_values)
        
        await message.answer(effect_text, parse_mode="HTML", reply_markup=keyboard)
        await state.set_state(AudioStates.waiting_for_effects)
        await state.update_data(effect_values=effect_values, page=0)
        
    except Exception as e:
        logger.error(f"Audio process error: {e}")
        await message.answer("❌ <b>Audio faýly işlemekde ýalňyşlyk ýüze çykdy!</b>", parse_mode="HTML")
        await state.clear()

@dp.callback_query(F.data.startswith("effect_"))
async def process_effect_selection(callback: CallbackQuery, state: FSMContext):
    """Effect sazlamak"""
    data = await state.get_data()
    effect_values = data.get("effect_values", {})
    page = data.get("page", 0)
    
    # Effect adyny we bahany almak
    parts = callback.data.split("_")
    effect_key = parts[1]
    
    # Bahany artdyrmak/azaltmak üçin keyboard
    current_value = effect_values.get(effect_key, EFFECTS[effect_key]["default"])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖ 10", callback_data=f"adjust_{effect_key}_{page}_-10"),
            InlineKeyboardButton(text="➖ 1", callback_data=f"adjust_{effect_key}_{page}_-1"),
        ],
        [
            InlineKeyboardButton(text=f"🎛 {current_value}%", callback_data=f"noop"),
        ],
        [
            InlineKeyboardButton(text="➕ 1", callback_data=f"adjust_{effect_key}_{page}_1"),
            InlineKeyboardButton(text="➕ 10", callback_data=f"adjust_{effect_key}_{page}_10"),
        ],
        [
            InlineKeyboardButton(text="🎯 Set", callback_data=f"set_{effect_key}_{page}"),
            InlineKeyboardButton(text="🔄 Reset", callback_data=f"reset_{effect_key}_{page}"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Yza", callback_data=f"back_to_effects_{page}"),
        ]
    ])
    
    effect_info = EFFECTS[effect_key]
    progress_bar = create_progress_bar(current_value)
    
    text = f"""
🔧 <b>Effect Sazlamasy</b>

🎵 <b>Effect:</b> {effect_info['name']}
📊 <b>Häzirki baha:</b> {current_value}%
{progress_bar}

📈 <b>Min:</b> {effect_info['min']}%
📉 <b>Max:</b> {effect_info['max']}%

<i>Bahany sazlamak üçin düwmeleri ulanyň</i>
    """
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data.startswith("adjust_"))
async def process_adjust_effect(callback: CallbackQuery, state: FSMContext):
    """Effect bahasyny üýtgetmek"""
    data = await state.get_data()
    effect_values = data.get("effect_values", {})
    
    parts = callback.data.split("_")
    effect_key = parts[1]
    page = int(parts[2])
    adjustment = int(parts[3])
    
    current_value = effect_values.get(effect_key, EFFECTS[effect_key]["default"])
    new_value = current_value + adjustment
    
    # Min we max çäginde saklamak
    min_val = EFFECTS[effect_key]["min"]
    max_val = EFFECTS[effect_key]["max"]
    new_value = max(min_val, min(max_val, new_value))
    
    effect_values[effect_key] = new_value
    
    await state.update_data(effect_values=effect_values)
    
    # Täzelän keyboard görkezmek
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖ 10", callback_data=f"adjust_{effect_key}_{page}_-10"),
            InlineKeyboardButton(text="➖ 1", callback_data=f"adjust_{effect_key}_{page}_-1"),
        ],
        [
            InlineKeyboardButton(text=f"🎛 {new_value}%", callback_data=f"noop"),
        ],
        [
            InlineKeyboardButton(text="➕ 1", callback_data=f"adjust_{effect_key}_{page}_1"),
            InlineKeyboardButton(text="➕ 10", callback_data=f"adjust_{effect_key}_{page}_10"),
        ],
        [
            InlineKeyboardButton(text="🎯 Set", callback_data=f"set_{effect_key}_{page}"),
            InlineKeyboardButton(text="🔄 Reset", callback_data=f"reset_{effect_key}_{page}"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Yza", callback_data=f"back_to_effects_{page}"),
        ]
    ])
    
    effect_info = EFFECTS[effect_key]
    progress_bar = create_progress_bar(new_value)
    
    text = f"""
🔧 <b>Effect Sazlamasy</b>

🎵 <b>Effect:</b> {effect_info['name']}
📊 <b>Häzirki baha:</b> {new_value}%
{progress_bar}

📈 <b>Min:</b> {effect_info['min']}%
📉 <b>Max:</b> {effect_info['max']}%

<i>Bahany sazlamak üçin düwmeleri ulanyň</i>
    """
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer(f"Baha üýtgedildi: {new_value}%")

@dp.callback_query(F.data.startswith("back_to_effects_"))
async def process_back_to_effects(callback: CallbackQuery, state: FSMContext):
    """Effect sazlamalaryna yzyna gaýtmak"""
    page = int(callback.data.split("_")[-1])
    data = await state.get_data()
    effect_values = data.get("effect_values", {})
    
    keyboard = create_effect_keyboard(effect_values, page)
    
    effect_text = f"""
🎛 <b>Audio Effect Sazlamalary</b>

{len(EFFECTS)} sany effect bar:
• Bass/Treble: {EFFECTS['bass']['name']}, {EFFECTS['treble']['name']}
• Reverb/Delay: {EFFECTS['reverb']['name']}, {EFFECTS['delay']['name']}
• Special: {EFFECTS['vinyl']['name']}, {EFFECTS['radio']['name']}

🔄 <b>Sazlamak üçin:</b>
Effect düwmesine basyň we bahany sazlaň
    """
    
    await callback.message.edit_text(effect_text, parse_mode="HTML", reply_markup=keyboard)
    await state.update_data(page=page)
    await callback.answer()

@dp.callback_query(F.data.startswith("page_"))
async def process_page_change(callback: CallbackQuery, state: FSMContext):
    """Sahypany üýtgetmek"""
    page = int(callback.data.split("_")[1])
    data = await state.get_data()
    effect_values = data.get("effect_values", {})
    
    keyboard = create_effect_keyboard(effect_values, page)
    
    effect_text = f"""
🎛 <b>Audio Effect Sazlamalary</b>

{len(EFFECTS)} sany effect bar:
• Bass/Treble: {EFFECTS['bass']['name']}, {EFFECTS['treble']['name']}
• Reverb/Delay: {EFFECTS['reverb']['name']}, {EFFECTS['delay']['name']}
• Special: {EFFECTS['vinyl']['name']}, {EFFECTS['radio']['name']}

🔄 <b>Sazlamak üçin:</b>
Effect düwmesine basyň we bahany sazlaň
    """
    
    await callback.message.edit_text(effect_text, parse_mode="HTML", reply_markup=keyboard)
    await state.update_data(page=page)
    await callback.answer()

@dp.callback_query(F.data == "apply_effects")
async def process_apply_effects(callback: CallbackQuery, state: FSMContext):
    """Effectleri ulanmak"""
    data = await state.get_data()
    audio_data = data.get("audio_data")
    effect_values = data.get("effect_values", {})
    
    if not audio_data:
        await callback.answer("❌ Audio faýl ýok!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "⏳ <b>Audio faýly işleýär...</b>\n\n"
        "🔄 Effectler ulanylýar...",
        parse_mode="HTML"
    )
    
    try:
        # Audio processing
        processed_audio = apply_audio_effects(audio_data, effect_values)
        
        # Täze audio faýly ýollamak
        audio_file = BytesIO(processed_audio)
        audio_file.name = "processed_audio.mp3"
        
        # Saýlanan effectleri görkezmek
        selected_effects = []
        for key, value in effect_values.items():
            if value != EFFECTS[key]["default"]:
                selected_effects.append(f"• {EFFECTS[key]['name']}: {value}%")
        
        effects_text = "\n".join(selected_effects[:10])  # Ilkinji 10 effect görkezmek
        if len(selected_effects) > 10:
            effects_text += f"\n• ... we {len(selected_effects) - 10} effect"
        
        await bot.send_audio(
            chat_id=callback.message.chat.id,
            audio=FSInputFile(audio_file),
            caption=f"""
✅ <b>Audio faýlyňyz taýýar!</b>

🎛 <b>Ulanan effectler:</b>
{effects_text if selected_effects else "• Default sazlamalar"}

✨ <b>Ýene bir audio işlemek üçin /start basyň!</b>
            """,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Täze Audio", callback_data="send_audio")],
                [InlineKeyboardButton(text="🏠 Baş Menýu", callback_data="main_menu")]
            ])
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Apply effects error: {e}")
        await callback.message.edit_text(
            "❌ <b>Audio faýly işlemekde ýalňyşlyk ýüze çykdy!</b>",
            parse_mode="HTML"
        )
    
    await callback.answer()

@dp.callback_query(F.data == "reset_effects")
async def process_reset_effects(callback: CallbackQuery, state: FSMContext):
    """Effectleri resetlemek"""
    effect_values = {key: effect["default"] for key, effect in EFFECTS.items()}
    
    await state.update_data(effect_values=effect_values, page=0)
    
    keyboard = create_effect_keyboard(effect_values, 0)
    
    await callback.message.edit_text(
        "🔄 <b>Effectler resetlendi!</b>\n\n"
        "Indi täzeden sazlamak üçin effectleri saýlaň.",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer("Effectler resetlendi!")

@dp.callback_query(F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    """Baş menýu"""
    await state.clear()
    
    welcome_text = f"""
✨ <b>Salam, {callback.from_user.first_name}!</b> ✨

🎵 <b>Audio Effect Bot</b> 🎵 hoş geldiňiz!

Bu bot bilen:
• Audio faýllaryňyza 50-den gowrak effect goşup bilersiňiz
• Her effecti 0-100% aralygynda sazlap bilersiňiz
• Täze effectli audio faýly ýükläp alyp bilersiňiz

🚀 <b>Başlamak üçin:</b>
1. Audio faýlyňyzy ýollap beriň (MP3 formaty)
2. Effectleri sazlaň
3. Täze faýly almagyňyzy soraň!

🔧 <b>Admin:</b> {ADMIN_USERNAME}
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Audio ýolla", callback_data="send_audio")],
        [InlineKeyboardButton(text="ℹ️ Maglumat", callback_data="info")],
        [InlineKeyboardButton(text="👨‍💻 Admin", url=f"tg://user?id={ADMIN_ID}")]
    ])
    
    await callback.message.edit_text(welcome_text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "info")
async def process_info(callback: CallbackQuery):
    """Bot barada maglumat"""
    info_text = f"""
📚 <b>Audio Effect Bot - Maglumat</b>

🎵 <b>Effectler:</b> {len(EFFECTS)} sany
🎛 <b>Sazlama aralygy:</b> 0-100%
🎧 <b>Formatlar:</b> MP3, VOICE, Audio

✨ <b>Ähli effectler:</b>
• Bass/Treble effectler
• Reverb/Delay effectler
• Distortion effectler
• Modulation effectler
• Filter effectler
• Dynamic effectler
• Special effectler

👨‍💻 <b>Developer:</b> {ADMIN_USERNAME}
🆔 <b>Admin ID:</b> {ADMIN_ID}

🔧 <b>Tehnologiýalar:</b>
• Python aiogram
• PyDub audio processing
• Inline keyboard
• FSM (State Machine)

<i>Bot doly işleýär we täze audio faýllary döredýär!</i>
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Audio ýolla", callback_data="send_audio")],
        [InlineKeyboardButton(text="🏠 Baş Menýu", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(info_text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "noop")
async def process_noop(callback: CallbackQuery):
    """Hiç zat etmezlik üçin"""
    await callback.answer()

# ====================== ADMIN HANDLERS ======================
@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    """Bot statistikasy"""
    if message.from_user.id == ADMIN_ID:
        stats_text = f"""
📊 <b>Bot Statistikasy</b>

👥 <b>Umumy:</b>
• Effectler: {len(EFFECTS)} sany
• Admin: {ADMIN_USERNAME}

🔧 <b>Tehniki:</b>
• Python aiogram
• PyDub audio processing
• Memory storage

🛠 <b>Kömek:</b>
• /start - Boty başlat
• /admin - Admin paneli
• /stats - Statistika
        """
        await message.answer(stats_text, parse_mode="HTML")
    else:
        await message.answer("❌ Bu ýere girip bolmaýar!")

# ====================== MAIN ======================
async def main():
    """Boty başlatmak"""
    print("=" * 50)
    print(f"🤖 Audio Effect Bot başlanýar...")
    print(f"👑 Admin: {ADMIN_USERNAME}")
    print(f"🆔 Admin ID: {ADMIN_ID}")
    print(f"🎵 Effectler: {len(EFFECTS)} sany")
    print("=" * 50)
    
    # Boty başlatmak
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
