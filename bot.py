import os
import discord
from discord.ext import commands

# --- Cấu hình các thiết lập cơ bản cho bot ---
intents = discord.Intents.default()
intents.members = True          # Bật intent để bot nhận sự kiện thành viên mới
intents.message_content = True  # Bật intent đọc nội dung tin nhắn

bot = commands.Bot(command_prefix="!", intents=intents)

# Sự kiện khi bot khởi động thành công
@bot.event
async def on_ready():
    print(f"Bot đã đăng nhập thành công với tên: {bot.user}")

# Sự kiện tự động gán role 'Member' khi có thành viên mới vào server
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        try:
            await member.add_roles(role)
            print(f"Đã gán vai trò {role.name} cho {member.name}")
        except Exception as e:
            print(f"Lỗi khi gán vai trò: {e}")

# Các lệnh quản lý cơ bản
@bot.command()
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Đã xóa {amount} tin nhắn.", delete_after=3)

@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"Đã kick thành công {member.mention}")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"Đã ban thành công {member.mention}")

# -------------------------------------------------------------
# BƯỚC 3: Lấy Token bảo mật từ biến môi trường trên Render
# -------------------------------------------------------------
TOKEN = os.getenv("MTU2MTQzNTgzMjgzNjAzMDQ5Ng.GqUyF5.Ub2AdQQmf8_4DAqebLOH2LbYvTnkPwACiXIy_c")
if TOKEN is None:
    print("Lỗi: Không tìm thấy biến môi trường DISCORD_TOKEN!")
else:
    bot.run(TOKEN)
