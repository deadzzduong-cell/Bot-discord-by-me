import os
import random
import asyncio
import discord
from discord.ext import commands

# -------------------------------------------------------------
# CẤU HÌNH CÁC ID VÀ TOKEN (Thay đổi thông tin của bạn tại đây)
# -------------------------------------------------------------
WELCOME_CHANNEL_ID = 1476494395204435978  # ID kênh gửi thông báo Chào mừng / Tạm biệt
LEVEL_CHANNEL_ID = 1562086216000733296    # ID kênh gửi thông báo Lên Cấp (Level Up)
MEMBER_ROLE_NAME = "Human"                # Tên role muốn tự động cấp
TOKEN = "DÁN_TOKEN_THẬT_CỦA_BẠN_VÀO_ĐÂY"

# --- Cấu hình các thiết lập cơ bản cho bot ---
intents = discord.Intents.default()
intents.members = True          # Bật intent để nhận sự kiện thành viên tham gia/rời đi
intents.message_content = True  # Bật intent đọc nội dung tin nhắn

bot = commands.Bot(command_prefix="!", intents=intents)

# Bộ nhớ tạm để lưu hệ thống Level / XP của thành viên
user_xp = {}

# Sự kiện khi bot khởi động thành công
@bot.event
async def on_ready():
    print(f"Bot đã đăng nhập thành công với tên: {bot.user}")

# --- SỰ KIỆN THÀNH VIÊN MỚI THAM GIA (WELCOME + AUTOROLE) ---
@bot.event
async def on_member_join(member):
    # 1. Tự động gán role 'Human' (hoặc role bạn chọn)
    role = discord.utils.get(member.guild.roles, name=MEMBER_ROLE_NAME)
    if role:
        try:
            await member.add_roles(role)
            print(f"Đã gán vai trò {role.name} cho {member.name}")
        except Exception as e:
            print(f"Lỗi khi gán vai trò: {e}")

    # 2. Gửi tin nhắn Chào mừng qua ID Kênh
    channel = bot.get_channel(WELCOME_CHANNEL_ID) 
    if channel:
        embed = discord.Embed(
            title="🎉 Thành viên mới gia nhập!",
            description=f"Chào mừng {member.mention} đã đến với **{member.guild.name}**!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Số lượng thành viên:", value=f"{member.guild.member_count} người", inline=False)
        embed.set_footer(text="Chúc bạn có khoảng thời gian vui vẻ tại đây!")
        
        await channel.send(embed=embed)

# --- SỰ KIỆN THÀNH VIÊN RỜI SERVER (GOODBYE) ---
@bot.event
async def on_member_remove(member):
    # Gửi tin nhắn Tạm biệt qua ID Kênh
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="👋 Thành viên rời đi",
            description=f"Tạm biệt **{member.name}**, chúc bạn luôn may mắn!",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Số lượng thành viên còn lại:", value=f"{member.guild.member_count} người", inline=False)
        
        await channel.send(embed=embed)

# --- HỆ THỐNG XP & LEVEL KHI NHẮN TIN (GỬI QUA KÊNH LEVEL ID) ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    author_id = message.author.id
    # Khởi tạo dữ liệu nếu user chưa có trong hệ thống
    if author_id not in user_xp:
        user_xp[author_id] = {"xp": 0, "level": 1}

    # Cộng ngẫu nhiên từ 5 đến 15 XP mỗi tin nhắn
    user_xp[author_id]["xp"] += random.randint(5, 15)
    current_xp = user_xp[author_id]["xp"]
    current_level = user_xp[author_id]["level"]

    # Mức XP cần thiết để lên cấp tiếp theo (Level * 100)
    needed_xp = current_level * 100
    if current_xp >= needed_xp:
        user_xp[author_id]["level"] += 1
        user_xp[author_id]["xp"] = 0
        
        # Gửi thông báo Lên cấp sang kênh Level riêng biệt qua ID Kênh
        level_channel = bot.get_channel(LEVEL_CHANNEL_ID)
        if level_channel:
            await level_channel.send(f"🎉 Chúc mừng {message.author.mention} đã đạt **Level {current_level + 1}**! 🚀")
        else:
            # Nếu không tìm thấy kênh theo ID trên, gửi tạm vào kênh hiện tại
            await message.channel.send(f"🎉 Chúc mừng {message.author.mention} đã đạt **Level {current_level + 1}**! 🚀")

    # Bắt buộc phải có dòng này để bot tiếp tục nhận diện các lệnh dấu `!`
    await bot.process_commands(message)

# --- CÁC LỆNH QUẢN LÝ VÀ TIỆN ÍCH ---
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

@bot.command(name="avatar")
async def get_avatar(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
        
    embed = discord.Embed(
        title=f"🖼️ Avatar của {member.name}",
        color=discord.Color.blue()
    )
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# --- LỆNH TUNG ĐỒNG XU (COIN FLIP) ---
@bot.command(name="coinflip")
async def coin_flip(ctx):
    result = random.choice(["🪙 Mặt Ngửa (Heads)", "🪙 Mặt Sấp (Tails)"])
    embed = discord.Embed(
        title="🎲 Tung Đồng Xu",
        description=f"Kết quả tung đồng xu cho {ctx.author.mention}: **{result}**",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

# --- LỆNH XEM RANK / LEVEL ---
@bot.command(name="rank")
async def show_rank(ctx, member: discord.Member = None):
    target = member or ctx.author
    data = user_xp.get(target.id, {"xp": 0, "level": 1})
    
    embed = discord.Embed(
        title=f"📊 Cấp độ của {target.name}",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="Level", value=str(data["level"]), inline=True)
    embed.add_field(name="XP hiện tại", value=str(data["xp"]), inline=True)
    
    await ctx.send(embed=embed)

# --- LỆNH VÒNG QUAY MAY MẮN (WHEEL OF NAMES) ---
@bot.command(name="wheel")
async def wheel_of_names(ctx, *, names_str: str = None):
    if not names_str:
        await ctx.send("❌ **Cú pháp sai!** Vui lòng nhập danh sách các tên cách nhau bằng dấu phẩy.\n👉 *Ví dụ:* `!wheel An, Bình, Cường, Dũng, Giang`")
        return

    names = [name.strip() for name in names_str.split(",") if name.strip()]

    if len(names) < 2:
        await ctx.send("⚠️ Bạn cần nhập ít nhất **2 lựa chọn** cách nhau bằng dấu phẩy để quay!")
        return

    embed = discord.Embed(
        title="🎡 VÒNG QUAY MAY MẮN 🎡",
        description=f"📋 **Các lựa chọn:** {', '.join(names)}\n\n🌀 *Đang khởi động vòng quay...*",
        color=discord.Color.gold()
    )
    msg = await ctx.send(embed=embed)

    effects = ["🎰 **Đang xoay vòng quay...**", "🎲 **Đang xáo trộn các tên...**", "⚡ **Sắp tìm ra người may mắn...**"]
    for effect in effects:
        await asyncio.sleep(1.2)
        embed.description = f"📋 **Các lựa chọn:** {', '.join(names)}\n\n{effect}"
        await msg.edit(embed=embed)

    winner = random.choice(names)

    await asyncio.sleep(1)
    embed_winner = discord.Embed(
        title="🎉 KẾT QUẢ VÒNG QUAY 🎉",
        description=f"📋 **Danh sách tham gia:** {', '.join(names)}\n\n🏆 **Người trúng giải là:** **`{winner}`** 🥳✨",
        color=discord.Color.green()
    )
    embed_winner.set_footer(text=f"Được quay bởi {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

    await msg.edit(embed=embed_winner)
    await ctx.send(f"🎊 Chúc mừng **{winner}** đã trúng thưởng!")

# -------------------------------------------------------------
# KHỞI ĐỘNG BOT
# -------------------------------------------------------------
if __name__ == "__main__":
    bot.run(TOKEN)
