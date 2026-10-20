import discord
from discord.ext import commands
from keep_alive import keep_alive

# Cấu hình Intents
intents = discord.Intents.default()
intents.members = True        # Bắt buộc để nhận member join/leave, kick, ban, gán role
intents.message_content = True  # Bắt buộc để đọc các lệnh

# Tiền tố lệnh là !
bot = commands.Bot(command_prefix='!', intents=intents)

# Xóa lệnh help mặc định của discord.py để tránh bị trùng lặp lỗi
bot.remove_command('help')

# Đặt tên Role tự động gán khi người mới vào (Đã đổi thành Member theo ý bạn)
AUTO_ROLE_NAME = "Member"

@bot.event
async def on_ready():
    print(f'Bot đã đăng nhập thành công với tên: {bot.user}')

# ==========================================
# 1. TỰ ĐỘNG GÁN ROLE & CHÀO MỪNG (CÓ AVATAR)
# ==========================================
@bot.event
async def on_member_join(member):
    # Tự động gán Role
    role = discord.utils.get(member.guild.roles, name=AUTO_ROLE_NAME)
    if role:
        try:
            await member.add_roles(role)
            print(f"Đã gán role '{AUTO_ROLE_NAME}' cho {member.name}")
        except discord.Forbidden:
            print("Lỗi: Bot không đủ quyền để gán role này. Hãy kéo role của Bot lên trên role Member!")

    # Gửi tin nhắn chào mừng vào kênh chung
    channel = discord.utils.get(member.guild.text_channels, name='chung')
    if channel:
        embed = discord.Embed(
            title="👋 Chào mừng bạn đến với Server!",
            description=f"Xin chào {member.mention}, bạn đã được nhận role **{AUTO_ROLE_NAME}**!\nChúc bạn có những phút giây vui vẻ tại **{member.guild.name}**!",
            color=discord.Color.green()
        )
        # Lấy avatar của thành viên mới
        avatar_url = member.display_avatar.url
        embed.set_thumbnail(url=avatar_url)  # Hiển thị avatar nhỏ ở góc phải
        
        await channel.send(embed=embed)

# ==========================================
# 2. TẠM BIỆT THÀNH VIÊN RỜI SERVER (CÓ AVATAR)
# ==========================================
@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name='chung')
    if channel:
        embed = discord.Embed(
            title="😢 Thành viên rời server",
            description=f"**{member.name}** đã rời khỏi server. Hẹn gặp lại!",
            color=discord.Color.red()
        )
        # Lấy avatar của thành viên rời server
        avatar_url = member.display_avatar.url
        embed.set_thumbnail(url=avatar_url)  # Hiển thị avatar nhỏ ở góc phải
        
        await channel.send(embed=embed)

# ==========================================
# 3. LỆNH XÓA TIN NHẮN (!clear <số lượng>)
# ==========================================
@bot.command(name='clear', help='Xóa tin nhắn (Ví dụ: !clear 10)')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount <= 0:
        await ctx.send("Vui lòng nhập số lượng lớn hơn 0!", delete_after=5)
        return
    
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Đã xóa thành công **{len(deleted) - 1}** tin nhắn.", delete_after=3)

# ==========================================
# 4. LỆNH ĐUỔI THÀNH VIÊN (!kick @user [lý do])
# ==========================================
@bot.command(name='kick', help='Đuổi thành viên khỏi server')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("❌ Bạn không thể tự kick chính mình!")
        return

    reason_str = reason if reason else "Không có lý do"
    await member.kick(reason=reason_str)

    embed = discord.Embed(
        title="👢 Đã đuổi thành viên (Kick)",
        description=f"**{member.name}** đã bị đuổi khỏi server.\n**Lý do:** {reason_str}",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

# ==========================================
# 5. LỆNH CẤM THÀNH VIÊN (!ban @user [lý do])
# ==========================================
@bot.command(name='ban', help='Cấm vĩnh viễn thành viên')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("❌ Bạn không thể tự ban chính mình!")
        return

    reason_str = reason if reason else "Không có lý do"
    await member.ban(reason=reason_str)

    embed = discord.Embed(
        title="🔨 Đã cấm thành viên (Ban)",
        description=f"**{member.name}** đã bị cấm khỏi server.\n**Lý do:** {reason_str}",
        color=discord.Color.dark_red()
    )
    await ctx.send(embed=embed)

# ==========================================
# 6. LỆNH HƯỚNG DẪN (!help)
# ==========================================
@bot.command(name='help', help='Hiển thị danh sách các lệnh của bot')
async def custom_help(ctx):
    embed = discord.Embed(
        title="🤖 Danh sách lệnh quản lý Bot",
        description="Dưới đây là các lệnh bạn có thể sử dụng:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🧹 `!clear <số lượng>`",
        value="Xóa nhanh số lượng tin nhắn chỉ định trong kênh.\n*(Yêu cầu quyền: Quản lý tin nhắn)*",
        inline=False
    )
    embed.add_field(
        name="👢 `!kick @user [lý do]`",
        value="Đuổi một thành viên khỏi server.\n*(Yêu cầu quyền: Đuổi thành viên)*",
        inline=False
    )
    embed.add_field(
        name="🔨 `!ban @user [lý do]`",
        value="Cấm vĩnh viễn một thành viên khỏi server.\n*(Yêu cầu quyền: Cấm thành viên)*",
        inline=False
    )
    
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

# ==========================================
# XỬ LÝ LỖI
# ==========================================
@clear.error
@kick.error
@ban.error
async def command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bạn không đủ quyền để sử dụng lệnh này!", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Bạn chưa nhập đủ thông tin. Ví dụ: `!kick @user Lý do` hoặc `!ban @user Lý do`", delete_after=5)
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Không tìm thấy thành viên này trong server!", delete_after=5)

# Khởi động web server giữ bot luôn hoạt động
keep_alive()

# Chạy bot bằng Token của bạn
bot.run('MTU2MTQzNTgzMjgzNjAzMDQ5Ng.GTkKa2.oAHgLe-1weB-QJMD4A7Gv-Xrkl_wVZ6-vIFhyE')
