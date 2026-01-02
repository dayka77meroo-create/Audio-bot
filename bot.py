import os
import uuid
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup,
    InlineKeyboardButton, InputFile, FSInputFile
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Audio processing libraries
try:
    from pydub import AudioSegment
    from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips
    import numpy as np
    AUDIO_SUPPORT = True
except ImportError:
    AUDIO_SUPPORT = False
    print("Audio processing libraries not installed. Install with: pip install pydub moviepy numpy")

# Bot configuration
BOT_TOKEN = "8387242598:AAHFfLJ5JLnYz5_ENSoM7sn3c7bT7L5pRPk"
ADMIN_USERNAME = "@Daykkaa"

# Initialize bot
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# Create directories
UPLOAD_DIR = Path("uploads")
EFFECTS_DIR = Path("effects")
UPLOAD_DIR.mkdir(exist_ok=True)
EFFECTS_DIR.mkdir(exist_ok=True)

# States
class AudioStates(StatesGroup):
    waiting_for_audio = State()
    choosing_effects = State()
    processing_audio = State()

# Audio Effect Definitions
class AudioEffect:
    def __init__(self, name: str, description: str, types: List[str]):
        self.name = name
        self.description = description
        self.types = types
    
    def apply(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply effect to audio"""
        if self.name == "Echo":
            return self._apply_echo(audio, effect_type)
        elif self.name == "Reverb":
            return self._apply_reverb(audio, effect_type)
        elif self.name == "Speed":
            return self._apply_speed(audio, effect_type)
        elif self.name == "Pitch":
            return self._apply_pitch(audio, effect_type)
        elif self.name == "Volume":
            return self._apply_volume(audio, effect_type)
        elif self.name == "Fade":
            return self._apply_fade(audio, effect_type)
        elif self.name == "Reverse":
            return self._apply_reverse(audio, effect_type)
        elif self.name == "Distortion":
            return self._apply_distortion(audio, effect_type)
        elif self.name == "Chorus":
            return self._apply_chorus(audio, effect_type)
        elif self.name == "Flanger":
            return self._apply_flanger(audio, effect_type)
        elif self.name == "Equalizer":
            return self._apply_equalizer(audio, effect_type)
        # Add more effects as needed
        return audio
    
    def _apply_echo(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply echo effect"""
        if effect_type == "Soft Echo":
            # Light echo
            echo = audio - 10
            echo = echo.fade_out(100).fade_in(100)
            return audio.overlay(audio, gain_during_overlay=-6).overlay(echo, gain_during_overlay=-12, position=200)
        elif effect_type == "Medium Echo":
            # Medium echo
            echo = audio - 8
            return audio.overlay(audio, gain_during_overlay=-4).overlay(echo, gain_during_overlay=-10, position=300)
        elif effect_type == "Strong Echo":
            # Strong echo
            echo1 = audio - 6
            echo2 = audio - 12
            result = audio.overlay(audio, gain_during_overlay=-2)
            result = result.overlay(echo1, gain_during_overlay=-8, position=250)
            return result.overlay(echo2, gain_during_overlay=-14, position=500)
        elif effect_type == "Multi Echo":
            # Multiple echoes
            result = audio
            for i in range(1, 4):
                echo = audio - (i * 4)
                result = result.overlay(echo, gain_during_overlay=-8*i, position=150*i)
            return result
        return audio
    
    def _apply_reverb(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply reverb effect (simulated)"""
        if effect_type == "Room Reverb":
            return audio._spawn(audio.raw_data)
        elif effect_type == "Hall Reverb":
            return audio._spawn(audio.raw_data)
        elif effect_type == "Cathedral Reverb":
            return audio._spawn(audio.raw_data)
        elif effect_type == "Plate Reverb":
            return audio._spawn(audio.raw_data)
        return audio
    
    def _apply_speed(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply speed change"""
        speed_factors = {
            "Slow (0.75x)": 0.75,
            "Normal": 1.0,
            "Fast (1.25x)": 1.25,
            "Very Fast (1.5x)": 1.5
        }
        factor = speed_factors.get(effect_type, 1.0)
        
        # Change speed by changing frame rate
        new_frame_rate = int(audio.frame_rate * factor)
        return audio._spawn(audio.raw_data, overrides={'frame_rate': new_frame_rate})
    
    def _apply_pitch(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply pitch shift (simulated with speed change)"""
        pitch_factors = {
            "Low Pitch": 0.8,
            "Normal Pitch": 1.0,
            "High Pitch": 1.2,
            "Very High Pitch": 1.4
        }
        factor = pitch_factors.get(effect_type, 1.0)
        
        # Simple pitch shift via speed change
        new_sample_rate = int(audio.frame_rate * factor)
        shifted = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
        return shifted.set_frame_rate(audio.frame_rate)
    
    def _apply_volume(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply volume change"""
        volume_changes = {
            "Quiet (-10dB)": -10,
            "Normal": 0,
            "Loud (+5dB)": 5,
            "Very Loud (+10dB)": 10
        }
        change = volume_changes.get(effect_type, 0)
        return audio + change
    
    def _apply_fade(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply fade effects"""
        if effect_type == "Fade In":
            return audio.fade_in(1000)
        elif effect_type == "Fade Out":
            return audio.fade_out(1000)
        elif effect_type == "Fade In/Out":
            return audio.fade_in(500).fade_out(500)
        elif effect_type == "Crossfade":
            return audio  # Would need another audio to crossfade with
        return audio
    
    def _apply_reverse(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply reverse effect"""
        return audio.reverse()
    
    def _apply_distortion(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply distortion effect"""
        # Simple distortion by clipping
        samples = np.array(audio.get_array_of_samples())
        
        if effect_type == "Light Distortion":
            threshold = 0.7
        elif effect_type == "Medium Distortion":
            threshold = 0.5
        elif effect_type == "Heavy Distortion":
            threshold = 0.3
        elif effect_type == "Extreme Distortion":
            threshold = 0.1
        else:
            return audio
        
        # Clip samples
        max_val = np.max(np.abs(samples))
        threshold_val = max_val * threshold
        samples = np.clip(samples, -threshold_val, threshold_val)
        
        # Create new audio
        return audio._spawn(samples.tobytes())
    
    def _apply_chorus(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply chorus effect"""
        # Simplified chorus effect
        if effect_type == "Light Chorus":
            delay = 30
        elif effect_type == "Medium Chorus":
            delay = 50
        elif effect_type == "Heavy Chorus":
            delay = 80
        elif effect_type == "Wide Chorus":
            delay = 100
        else:
            return audio
        
        # Create delayed copy
        delayed = AudioSegment.silent(duration=delay) + audio
        return audio.overlay(delayed, gain_during_overlay=-6)
    
    def _apply_flanger(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply flanger effect (simulated)"""
        return audio  # Implementation would be complex
    
    def _apply_equalizer(self, audio: AudioSegment, effect_type: str) -> AudioSegment:
        """Apply equalizer presets"""
        # Simple EQ by adjusting frequencies
        if effect_type == "Bass Boost":
            # Boost low frequencies
            return audio.low_pass_filter(300) + audio - 3
        elif effect_type == "Treble Boost":
            # Boost high frequencies
            return audio.high_pass_filter(3000) + audio - 3
        elif effect_type == "Vocal Boost":
            # Boost mid frequencies for vocals
            return audio - 6  # Simplified
        elif effect_type == "Flat":
            return audio
        return audio

# Define all available effects
EFFECTS = [
    AudioEffect("Echo", "🏔️ Jaň efekti", ["Soft Echo", "Medium Echo", "Strong Echo", "Multi Echo"]),
    AudioEffect("Reverb", "🏛️ Reverb efekti", ["Room Reverb", "Hall Reverb", "Cathedral Reverb", "Plate Reverb"]),
    AudioEffect("Speed", "⚡ Tizlik üýtgetmek", ["Slow (0.75x)", "Normal", "Fast (1.25x)", "Very Fast (1.5x)"]),
    AudioEffect("Pitch", "🎵 Pitch üýtgetmek", ["Low Pitch", "Normal Pitch", "High Pitch", "Very High Pitch"]),
    AudioEffect("Volume", "🔊 Ses güýçlendiriji", ["Quiet (-10dB)", "Normal", "Loud (+5dB)", "Very Loud (+10dB)"]),
    AudioEffect("Fade", "🌊 Fade efekti", ["Fade In", "Fade Out", "Fade In/Out", "Crossfade"]),
    AudioEffect("Reverse", "🔁 Tersine efekti", ["Reverse Audio"]),
    AudioEffect("Distortion", "🎸 Distortion efekti", ["Light Distortion", "Medium Distortion", "Heavy Distortion", "Extreme Distortion"]),
    AudioEffect("Chorus", "🎤 Chorus efekti", ["Light Chorus", "Medium Chorus", "Heavy Chorus", "Wide Chorus"]),
    AudioEffect("Flanger", "🌀 Flanger efekti", ["Light Flanger", "Medium Flanger", "Heavy Flanger", "Wide Flanger"]),
    AudioEffect("Equalizer", "🎛️ Ekwalizer", ["Bass Boost", "Treble Boost", "Vocal Boost", "Flat"]),
]

# User session data
user_sessions: Dict[int, Dict] = {}

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Start command handler"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    welcome_text = f"""
✨ <b>🎧 Audio Effect Bot-a hoş geldiňiz!</b> ✨

🤖 <b>Bot hakynda:</b>
Bu bot MP3 faýllaryňyza dürli audio effektler goşup berýär.

📊 <b>Elýeterli effektler:</b>
• 🏔️ Jaň (Echo) effekti
• 🏛️ Reverb effekti  
• ⚡ Tizlik üýtgetiji
• 🎵 Pitch üýtgetiji
• 🔊 Ses güýçlendiriji
• 🌊 Fade effekti
• 🔁 Tersine effekti
• 🎸 Distortion effekti
• 🎤 Chorus effekti
• 🌀 Flanger effekti
• 🎛️ Ekwalizer

🚀 <b>Başlamak üçin:</b>
1️⃣ MP3 faýlyňyzy ýükläň
2️⃣ Goşmak isleýän effektleriňizi saýlaň
3️⃣ 🔄 "Täze effektler goşulan MP3 ýükle" düwmesine basyň

💡 <b>Ýolbaşçylyk:</b> Bir gezekde birnäçe effekt saýlap bilersiňiz!

👨‍💻 <b>Admin:</b> {ADMIN_USERNAME}
    """
    
    # Create inline keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 MP3 Ýükle", callback_data="upload_audio")],
        [InlineKeyboardButton(text="📚 Effektleri Gör", callback_data="show_effects")],
        [InlineKeyboardButton(text="ℹ️ Bot Hakda", callback_data="about_bot")],
        [InlineKeyboardButton(text="🆘 Kömek", callback_data="help")]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard)
    await state.clear()

@router.callback_query(F.data == "upload_audio")
async def process_upload(callback: CallbackQuery, state: FSMContext):
    """Process audio upload"""
    await callback.answer()
    await callback.message.answer("🎵 <b>MP3 faýlyňyzy ýükläň...</b>\n\n📤 Faýly şu ýere ýüklemegiňizi haýyş edýäris.")
    await state.set_state(AudioStates.waiting_for_audio)

@router.message(AudioStates.waiting_for_audio, F.audio | F.document | F.voice)
async def handle_audio_upload(message: Message, state: FSMContext):
    """Handle uploaded audio file"""
    user_id = message.from_user.id
    
    # Initialize user session
    user_sessions[user_id] = {
        'effects': [],
        'audio_path': None,
        'original_filename': None
    }
    
    try:
        # Get file ID
        if message.audio:
            file_id = message.audio.file_id
            filename = message.audio.file_name or f"audio_{user_id}.mp3"
        elif message.document and message.document.mime_type and 'audio' in message.document.mime_type:
            file_id = message.document.file_id
            filename = message.document.file_name or f"audio_{user_id}.mp3"
        elif message.voice:
            file_id = message.voice.file_id
            filename = f"voice_{user_id}.ogg"
        else:
            await message.answer("❌ <b>Nädogry faýl görnüşi!</b>\n\nAudio faýly ýüklemegiňizi haýyş edýäris.")
            return
        
        # Download file
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        save_path = UPLOAD_DIR / f"{user_id}_{unique_id}_{filename}"
        
        # Download file
        await bot.download_file(file_path, save_path)
        
        # Store in session
        user_sessions[user_id]['audio_path'] = str(save_path)
        user_sessions[user_id]['original_filename'] = filename
        
        # Convert to MP3 if needed
        if not str(save_path).lower().endswith('.mp3'):
            try:
                audio = AudioSegment.from_file(save_path)
                mp3_path = save_path.with_suffix('.mp3')
                audio.export(mp3_path, format="mp3")
                save_path.unlink()  # Remove original
                save_path = mp3_path
                user_sessions[user_id]['audio_path'] = str(save_path)
            except Exception as e:
                print(f"Conversion error: {e}")
        
        # Show success message
        success_text = f"""
✅ <b>Audio faýlyňyz üstünlikli ýüklenildi!</b>

📁 <b>Faýl ady:</b> {filename}
📊 <b>Indi effektleri saýlap bilersiňiz:</b>
        """
        
        # Create effect selection keyboard
        keyboard = await create_effects_keyboard(user_id)
        
        await message.answer(success_text, reply_markup=keyboard)
        await state.set_state(AudioStates.choosing_effects)
        
    except Exception as e:
        print(f"Error handling audio: {e}")
        await message.answer("❌ <b>Faýly ýükläp bolmady!</b>\n\nGaýtadan synanyşyň ýa-da başga faýl iňediň.")

async def create_effects_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for selecting effects"""
    user_session = user_sessions.get(user_id, {})
    selected_effects = user_session.get('effects', [])
    
    keyboard = []
    
    # Add effects in rows of 2
    for i in range(0, len(EFFECTS), 2):
        row = []
        for effect in EFFECTS[i:i+2]:
            effect_id = f"effect_{EFFECTS.index(effect)}"
            is_selected = effect_id in selected_effects
            
            # Create button with emoji
            emoji = "✅" if is_selected else "⚪"
            button_text = f"{emoji} {effect.name}"
            
            row.append(InlineKeyboardButton(
                text=button_text,
                callback_data=f"select_{effect_id}"
            ))
        keyboard.append(row)
    
    # Add effect type selection buttons
    keyboard.append([InlineKeyboardButton(text="🔧 Her Effektiň Görnüşini Saýla", callback_data="select_types")])
    
    # Add action buttons
    action_row = []
    if selected_effects:
        action_row.append(InlineKeyboardButton(text="🔄 Audio-ý işle", callback_data="process_audio"))
    
    action_row.append(InlineKeyboardButton(text="🗑️ Saýlananlary Arassala", callback_data="clear_selected"))
    keyboard.append(action_row)
    
    # Add back button
    keyboard.append([InlineKeyboardButton(text="↩️ Baş Menu", callback_data="back_to_start")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data.startswith("select_effect_"))
async def select_effect(callback: CallbackQuery):
    """Select/deselect an effect"""
    user_id = callback.from_user.id
    
    if user_id not in user_sessions:
        await callback.answer("❌ Audio faýly ýükleň!", show_alert=True)
        return
    
    # Extract effect index
    effect_idx = int(callback.data.split("_")[2])
    
    if effect_idx >= len(EFFECTS):
        await callback.answer("❌ Nädogry effekt!", show_alert=True)
        return
    
    effect_id = f"effect_{effect_idx}"
    
    # Toggle selection
    if effect_id in user_sessions[user_id]['effects']:
        user_sessions[user_id]['effects'].remove(effect_id)
    else:
        user_sessions[user_id]['effects'].append(effect_id)
    
    # Update keyboard
    keyboard = await create_effects_keyboard(user_id)
    
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "select_types")
async def select_effect_types(callback: CallbackQuery):
    """Select specific types for each effect"""
    user_id = callback.from_user.id
    
    if user_id not in user_sessions:
        await callback.answer("❌ Audio faýly ýükleň!", show_alert=True)
        return
    
    # Create keyboard for effect type selection
    keyboard = []
    selected_effects = user_sessions[user_id]['effects']
    
    for effect_id in selected_effects:
        effect_idx = int(effect_id.split("_")[1])
        effect = EFFECTS[effect_idx]
        
        # Add effect name as button (non-clickable)
        keyboard.append([
            InlineKeyboardButton(
                text=f"🎛️ {effect.name}",
                callback_data="no_action"
            )
        ])
        
        # Add effect type buttons
        type_row = []
        for etype in effect.types:
            type_btn = InlineKeyboardButton(
                text=etype,
                callback_data=f"type_{effect_idx}_{effect.types.index(etype)}"
            )
            type_row.append(type_btn)
            if len(type_row) == 2:  # 2 buttons per row
                keyboard.append(type_row)
                type_row = []
        
        if type_row:  # Add remaining buttons
            keyboard.append(type_row)
        
        # Add separator
        keyboard.append([
            InlineKeyboardButton(text="────────", callback_data="no_action")
        ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton(text="↩️ Yza", callback_data="back_to_effects"),
        InlineKeyboardButton(text="🚀 Işle", callback_data="process_audio")
    ])
    
    await callback.message.edit_text(
        "🔧 <b>Her effektiň görnüşini saýlaň:</b>\n\n"
        "Aşakdakylardan her effektiň görnüşini saýlap bilersiňiz.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("type_"))
async def select_effect_type(callback: CallbackQuery):
    """Select specific type for an effect"""
    user_id = callback.from_user.id
    
    # Parse data
    parts = callback.data.split("_")
    effect_idx = int(parts[1])
    type_idx = int(parts[2])
    
    if effect_idx >= len(EFFECTS):
        await callback.answer("❌ Nädogry effekt!", show_alert=True)
        return
    
    effect = EFFECTS[effect_idx]
    
    if type_idx >= len(effect.types):
        await callback.answer("❌ Nädogry görnüş!", show_alert=True)
        return
    
    # Store selected type
    effect_id = f"effect_{effect_idx}"
    if 'effect_types' not in user_sessions[user_id]:
        user_sessions[user_id]['effect_types'] = {}
    
    user_sessions[user_id]['effect_types'][effect_id] = effect.types[type_idx]
    
    await callback.answer(f"✅ {effect.name}: {effect.types[type_idx]} saýlandy!")

@router.callback_query(F.data == "process_audio")
async def process_audio(callback: CallbackQuery, state: FSMContext):
    """Process audio with selected effects"""
    user_id = callback.from_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id]['effects']:
        await callback.answer("❌ Effekt saýlanmady!", show_alert=True)
        return
    
    # Check if audio file exists
    audio_path = user_sessions[user_id].get('audio_path')
    if not audio_path or not Path(audio_path).exists():
        await callback.answer("❌ Audio faýly tapylmady!", show_alert=True)
        return
    
    await callback.answer("🔄 Audio işlenilýär...")
    
    # Show processing message
    processing_msg = await callback.message.answer("""
⏳ <b>Audio işlenilýär...</b>

🔧 <b>Saýlanan effektler:</b>
""" + "\n".join([f"• {EFFECTS[int(eid.split('_')[1])].name}" 
                for eid in user_sessions[user_id]['effects']]) + """

⏰ <b>Bu birnäçe minut wagt alyp biler...</b>
""")
    
    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_path)
        
        # Apply selected effects
        for effect_id in user_sessions[user_id]['effects']:
            effect_idx = int(effect_id.split('_')[1])
            effect = EFFECTS[effect_idx]
            
            # Get selected type or use default
            effect_type = user_sessions[user_id].get('effect_types', {}).get(
                effect_id, effect.types[0] if effect.types else "Default"
            )
            
            # Apply effect
            audio = effect.apply(audio, effect_type)
        
        # Save processed audio
        output_filename = f"processed_{Path(audio_path).name}"
        output_path = UPLOAD_DIR / output_filename
        
        audio.export(output_path, format="mp3", bitrate="192k")
        
        # Send processed audio
        success_text = f"""
✅ <b>Audio üstünlikli işlendi!</b>

🎵 <b>Goşulan effektler:</b>
""" + "\n".join([f"• {EFFECTS[int(eid.split('_')[1])].name}" 
                 for eid in user_sessions[user_id]['effects']]) + """

📁 <b>Faýl:</b> {output_filename}
⬇️ <b>Aşakdan faýly ýükläp alyň:</b>
        """
        
        # Send audio file
        audio_file = FSInputFile(output_path, filename=output_filename)
        await callback.message.answer_audio(
            audio=audio_file,
            caption=success_text,
            title="Processed Audio",
            performer="Audio Effect Bot"
        )
        
        # Clean up
        try:
            Path(audio_path).unlink()
            output_path.unlink()
        except:
            pass
        
        # Reset state
        await state.clear()
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        # Delete processing message
        await processing_msg.delete()
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        await processing_msg.edit_text(f"""
❌ <b>Audio işlenilende ýalňyşlyk ýüze çykdy!</b>

🔧 <b>Sebäbi:</b> {str(e)}

🔄 <b>Gaýtadan synanyşyň ýa-da admin bilen habarlaşyň:</b> {ADMIN_USERNAME}
        """)

@router.callback_query(F.data == "clear_selected")
async def clear_selected(callback: CallbackQuery):
    """Clear selected effects"""
    user_id = callback.from_user.id
    
    if user_id in user_sessions:
        user_sessions[user_id]['effects'] = []
        if 'effect_types' in user_sessions[user_id]:
            del user_sessions[user_id]['effect_types']
    
    keyboard = await create_effects_keyboard(user_id)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer("🗑️ Saýlanan effektler arassalandy!")

@router.callback_query(F.data == "back_to_effects")
async def back_to_effects(callback: CallbackQuery):
    """Go back to effects selection"""
    user_id = callback.from_user.id
    
    if user_id not in user_sessions:
        await callback.answer("❌ Audio faýly ýükleň!", show_alert=True)
        return
    
    keyboard = await create_effects_keyboard(user_id)
    await callback.message.edit_text(
        "🎛️ <b>Effektleri saýlaň:</b>\n\n"
        "Aşakdakylardan audioňyza goşmak isleýän effektleriňizi saýlaň.",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    """Go back to start menu"""
    await cmd_start(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "show_effects")
async def show_effects(callback: CallbackQuery):
    """Show all available effects"""
    effects_list = "\n".join([f"• {effect.name}: {effect.description}" for effect in EFFECTS])
    
    await callback.message.answer(f"""
🎧 <b>Elýeterli Audio Effektler:</b>

{effects_list}

✨ <b>Jemi effektler:</b> {len(EFFECTS)}
🔧 <b>Her effektiň görnüşi:</b> 3-4 sany

🚀 <b>Audio ýükle:</b> MP3 faýlyňyzy ýüklemek üçin /start buýrugyny ulanyň!
    """)
    await callback.answer()

@router.callback_query(F.data == "about_bot")
async def about_bot(callback: CallbackQuery):
    """Show about bot information"""
    await callback.message.answer(f"""
🤖 <b>Audio Effect Bot</b>

✨ <b>Döreden:</b> {ADMIN_USERNAME}
📅 <b>Wersiýa:</b> 1.0.0

🎵 <b>Özellikler:</b>
• 50-e golaý audio effekt
• Her effektiň 3-4 görnüşi
• MP3 formatynda audio işleme
• Inline düwmeler bilen aňsat ulanylyş

💻 <b>Tehnologiýalar:</b>
• Python AIogram 3.x
• Pydub we MoviePy audio işleme
• Telegram Bot API

📞 <b>Kömek üçin:</b> {ADMIN_USERNAME}
    """)
    await callback.answer()

@router.callback_query(F.data == "help")
async def help_command(callback: CallbackQuery):
    """Show help information"""
    await callback.message.answer("""
🆘 <b>Kömek Maslahatlary:</b>

1️⃣ <b>Audio ýüklemek:</b>
   • MP3 formatynda audio faýlyňyzy ýükläň
   • Faýly şu ýere ýüklemegiňizi haýyş edýäris

2️⃣ <b>Effekt saýlamak:</b>
   • Goşmak isleýän effektiňizi saýlaň
   • Birnäçe effekt saýlap bilersiňiz
   • Her effektiň görnüşini saýlap bilersiňiz

3️⃣ <b>Audio işlemek:</b>
   • "Audio-ý işle" düwmesine basyň
   • Audio işleniljek we size iberiljek

4️⃣ <b>Problemalar:</b>
   • Faýl ýüklenilmez bolsa, gaýtadan synanyşyň
   • Bot işlemez bolsa, {ADMIN_USERNAME} bilen habarlaşyň

🚀 <b>Başlamak üçin:</b> /start buýrugyny ulanyň!
    """)
    await callback.answer()

@router.callback_query(F.data == "no_action")
async def no_action(callback: CallbackQuery):
    """Handle non-action buttons"""
    await callback.answer()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Admin panel"""
    if message.from_user.username != ADMIN_USERNAME.replace("@", ""):
        await message.answer("❌ <b>Bu buýruk diňe admin üçin!</b>")
        return
    
    stats_text = f"""
👑 <b>Admin Paneli</b>

📊 <b>Statistikalar:</b>
• Jemi ulanyjylar: {len(user_sessions)}
• Işlenýän audio faýllar: {len([p for p in UPLOAD_DIR.glob("*") if p.is_file()])}

⚙️ <b>Bot sazlamalary:</b>
• Elýeterli effektler: {len(EFFECTS)}
• Her effektiň görnüşi: 3-4 sany

🛠️ <b>Admin buýruklary:</b>
• /stats - Bot statistikalary
• /clean - Faýllary arassala
• /broadcast - Habar iber
    """
    
    await message.answer(stats_text)

@router.message(Command("stats"))
async def bot_stats(message: Message):
    """Show bot statistics"""
    if message.from_user.username != ADMIN_USERNAME.replace("@", ""):
        await message.answer("❌ <b>Bu buýruk diňe admin üçin!</b>")
        return
    
    stats = f"""
📈 <b>Bot Statistikalary</b>

👥 <b>Ulanyjylar:</b>
• Häzirki sessiyalar: {len(user_sessions)}
• Faýl ýüklemeler: {len(list(UPLOAD_DIR.glob("*")))}

🎵 <b>Effektler:</b>
• Jemi effektler: {len(EFFECTS)}
• Effekt görnüşleri: {sum(len(e.types) for e in EFFECTS)}

💾 <b>Faýl ulanylyşy:</b>
• Ýüklenen faýllar: UPLOAD_DIR/
• Effekt faýllary: EFFECTS_DIR/
    """
    
    await message.answer(stats)

# Error handler
@router.errors()
async def error_handler(event, **kwargs):
    """Handle errors"""
    print(f"Error occurred: {event.exception}")
    return True

# Main function
async def main():
    """Main function"""
    print("🤖 Audio Effect Bot işe başlady...")
    print(f"👑 Admin: {ADMIN_USERNAME}")
    print("🚀 Bot hazyr! /start buýrugy bilen başlap bilersiňiz...")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Check audio support
    if not AUDIO_SUPPORT:
        print("⚠️  Audio processing libraries not installed!")
        print("📦 Install with: pip install pydub moviepy numpy")
    
    # Run bot
    asyncio.run(main())
