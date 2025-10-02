import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.all()
kodsplit = commands.Bot("!", intents=intents)

roles = {
    "🟥": 1420697438716428428,
    "🟩": 1420697534447357993,
}

CARGOS_FILE = "cargos.json"

def carregar_roles():
    with open("cargos.json", "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_message_id(message_id: int):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump({"message_id": message_id}, f)

def carregar_message_id():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("message_id")
    except (FileNotFoundError, json.JSONDecodeError):
        return None

MESSAGE_ID = 1420698186476949599

@kodsplit.event
async def on_ready():
    global MESSAGE_ID
    MESSAGE_ID = carregar_message_id()
    print("on run")

@kodsplit.event
async def on_raw_reaction_add(payload:discord.RawReactionActionEvent):
    if payload.message_id != MESSAGE_ID:
        return
    
    guild = kodsplit.get_guild(payload.guild_id)
    if guild is None:
        return
    
    role_id = roles.get(str(payload.emoji))
    if role_id is None:
        return
    
    role = guild.get_role(role_id)
    if role is None:
        return
    
    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return
    
    await member.add_roles(role, reason="Reaction role")
    print(f"Adicionado {role.name} para {member.name}")

@kodsplit.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.message_id != MESSAGE_ID:
        return
    
    guild = kodsplit.get_guild(payload.guild_id)
    if guild is None:
        return
    
    role_id = roles.get(str(payload.emoji))
    if role_id is None:
        return
    
    role = guild.get_role(role_id)
    if role is None:
        return
    
    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return
    
    await member.remove_roles(role, reason="Reaction role removido")
    print(f"Removido {role.name} de {member.name}")


@kodsplit.command()
async def meeting(context: commands.Context):
    await context.send(f"olá, meu nome é {kodsplit.user.name}")
              
@kodsplit.command()
@commands.bot_has_permissions(kick_members=True)
async def expulsar(context: commands.Context, *, player:discord.Member ,reason=None):
        try:
            await player.kick(reason=reason)
            await context.send(f"o membro {player.mention} foi expulso.")
        except discord.Forbidden:
            await context.send("Sem nível de permissão suficiente")
        except discord.HTTPException:
            await context.send("Erro de conexão")
            

#-------------------------------------------------------------------------------
@kodsplit.command()
@commands.has_permissions(administrator=True)
async def add_cargo(context: commands.Context, icon:str, cargo:int):

    if not os.path.exists(CARGOS_FILE):
        with open(CARGOS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

  
    try:
        with open(CARGOS_FILE, "r", encoding="utf-8") as f:
            roles = json.load(f)
    except json.JSONDecodeError:
        roles = {}  

    roles = carregar_roles()
    roles[icon]= cargo
    with open ("cargos.json", 'w', encoding='utf-8') as f:
        json.dump(roles, f, indent=4, ensure_ascii=False)
    await context.reply("Novo cargo adicionado")
#-------------------------------------------------------------------------------
@kodsplit.command()
@commands.has_permissions(administrator=True)
async def cargosys(context:commands.Context):
    global MESSAGE_ID
    await context.channel.purge()

    roles = carregar_roles()

    if MESSAGE_ID:
        try:
            oldMsg = await context.channel.fetch_message(MESSAGE_ID)
            await oldMsg.delete()
        except discord.NotFound:
            pass 
        except discord.Forbidden:
            await context.send("Não tenho permissão para apagar a mensagem antiga.")
        except discord.HTTPException:
            await context.send("Erro ao tentar apagar a mensagem antiga.")
    
    descricao = "Escolha um cargo reagindo abaixo:\n\n"
    for emoji, roleId in roles.items():
        role = context.guild.get_role(roleId)
        descricao += f"{emoji} → {role.name}\n"


    msg = await context.send(embed=discord.Embed(
        title="Sistema de Cargos",
        description=descricao,
        color=discord.Color.blue()
    ))


    for emoji in roles.keys():
        await msg.add_reaction(emoji)


    MESSAGE_ID = msg.id
    salvar_message_id(MESSAGE_ID)

@kodsplit.command(name='Delete')
@commands.has_permissions(manage_messages=True)
async def deletarMsg(context:commands.Context, num:int):
    if num < 1:
        context.send("Para apagar as mensagens, precisa informar o número de mensagens")
        return
    
    sms = await context.channel.purge(limit=num+1)
    await context.send(f'{len(sms)-1} apagadas', delete_after=5)

kodsplit.run('MTQyMDA0MzU2MzQ4MzQwMjI2MA.G-nCUm.KMFqxIICDQQBFlNsJXS57WbUhCHPeL2CDpcjc4')
