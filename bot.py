import os
import discord
from discord.ext import commands

# --- Cấu hình các thiết lập cơ bản cho bot ---
intents = discord.Intents.default()
intents.members = True          # Bật intent để nhận sự kiện thành viên tham gia/rời đi
intents.message_content = True  # Bật intent đọc nội dung tin nhắn

bot = commands.Bot(command_prefix="!", intents=intents)

# Sự kiện khi bot khởi động thành công
@bot.event
async def on_ready():
    print(f"Bot đã đăng nhập thành công với tên: {bot.user}")

# --- SỰ KIỆN THÀNH VIÊN MỚI THAM GIA (WELCOME + AUTOROLE) ---
@bot.event
async def on_member_join(member):
    # 1. Tự động gán role 'Member'
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        try:
            await member.add_roles(role)
            print(f"Đã gán vai trò {role.name} cho {member.name}")
        except Exception as e:
            print(f"Lỗi khi gán vai trò: {e}")

    # 2. Gửi tin nhắn Chào mừng
    channel = discord.utils.get(member.guild.text_channels, name="chào-mừng") 
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
    channel = discord.utils.get(member.guild.text_channels, name="tạm-biệt")
    if channel:
        embed = discord.Embed(
            title="👋 Thành viên rời đi",
            description=f"Tạm biệt **{member.name}**, chúc bạn luôn may mắn!",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Số lượng thành viên còn lại:", value=f"{member.guild.member_count} người", inline=False)
        
        await channel.send(embed=embed)

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

# -------------------------------------------------------------
# KHỞI ĐỘNG BOT
# -------------------------------------------------------------
TOKEN = "DÁN_TOKEN_THẬT_CỦA_BẠN_VÀO_ĐÂY"

if __name__ == "__main__":
    bot.run(TOKEN)
