"""
Discord Bot: Server Name Changer based on Voice Channel Activity
================================================================
บอทจะเปลี่ยนชื่อเซิร์ฟเวอร์โดยอัตโนมัติ:
  - มีคนอยู่ใน Voice Channel → ชื่อเซิร์ฟเวอร์ = "o_o"
  - ไม่มีคนอยู่ใน Voice Channel → ชื่อเซิร์ฟเวอร์ = "-_-"

Permission ที่บอทต้องการ:
  - Manage Server (เพื่อเปลี่ยนชื่อเซิร์ฟเวอร์)
  - View Channels (เพื่ออ่านสถานะ Voice Channel)

วิธีติดตั้ง:
  pip install discord.py

วิธีรัน:
  python discord_bot.py
"""

import os
import discord
from discord.ext import commands

from myserver import server_on
# ─────────────────────────────────────────────
#  ตั้งค่าหลัก — แก้ไขตรงนี้ก่อนรันบอท
# ─────────────────────────────────────────────


NAME_EMPTY  = "-_-"   # ชื่อเซิร์ฟเวอร์เมื่อไม่มีคนอยู่ใน Voice
NAME_ACTIVE = "•_•"   # ชื่อเซิร์ฟเวอร์เมื่อมีคนอยู่ใน Voice
# ─────────────────────────────────────────────


# กำหนด Intents ที่บอทต้องการ
intents = discord.Intents.default()
intents.voice_states = True   # ต้องการ Intent นี้เพื่อรับ Event voice_state_update
intents.guilds = True         # ต้องการ Intent นี้เพื่อเข้าถึงข้อมูล Guild/Server

bot = commands.Bot(command_prefix="!", intents=intents)


def count_voice_members(guild: discord.Guild) -> int:
    """
    นับจำนวนสมาชิกทั้งหมดที่อยู่ใน Voice Channel ของ Guild นี้
    (ไม่นับบอทตัวอื่น เพื่อให้ผลลัพธ์แม่นยำขึ้น)
    """
    total = 0
    for voice_channel in guild.voice_channels:
        for member in voice_channel.members:
            if not member.bot:   # ข้ามบอท
                total += 1
    return total


@bot.event
async def on_ready():
    """เรียกเมื่อบอทเชื่อมต่อกับ Discord สำเร็จ"""
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("─" * 40)


@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState
):
    """
    Event นี้จะถูกเรียกทุกครั้งที่สถานะ Voice ของสมาชิกเปลี่ยนแปลง เช่น
      - เข้า / ออก Voice Channel
      - ย้ายห้อง
      - Mute / Unmute / Deafen
    """
    guild = member.guild

    # นับจำนวนคนที่อยู่ใน Voice Channel ขณะนี้
    voice_member_count = count_voice_members(guild)

    # ตัดสินใจว่าควรเปลี่ยนชื่อเป็นอะไร
    desired_name = NAME_ACTIVE if voice_member_count > 0 else NAME_EMPTY

    # ป้องกันการเปลี่ยนชื่อซ้ำโดยไม่จำเป็น
    if guild.name == desired_name:
        return

    # เปลี่ยนชื่อเซิร์ฟเวอร์
    try:
        await guild.edit(name=desired_name)
        status = "🔊 มีคนอยู่" if voice_member_count > 0 else "🔇 ไม่มีคนอยู่"
        print(
            f"[{guild.name}] {status} ({voice_member_count} คน) "
            f"→ เปลี่ยนชื่อเป็น '{desired_name}'"
        )
    except discord.Forbidden:
        print("❌ Error: บอทไม่มีสิทธิ์ 'Manage Server' — กรุณาตรวจสอบสิทธิ์บอทในเซิร์ฟเวอร์")
    except discord.HTTPException as e:
        print(f"❌ HTTP Error ขณะเปลี่ยนชื่อเซิร์ฟเวอร์: {e}")


# รันบอท
bot.run(os.getenv('TOKEN'))