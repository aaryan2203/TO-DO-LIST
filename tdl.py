import discord
from discord.ext import commands
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='-',intents=intents, help_command=None)

# File to store to-do lists
TODO_FILE = 'todo_data.json'

# Load or initialize data
def load_data():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(TODO_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Initialize data storage
todo_data = load_data()

# Helper function to get user's to-do list
def get_user_todos(user_id):
    user_id = str(user_id)
    if user_id not in todo_data:
        todo_data[user_id] = []
    return todo_data[user_id]

# Emoji checkboxes
UNCHECKED = "☐"
CHECKED = "☑"

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    await bot.change_presence(activity=discord.Game(name="-help for commands"))

@bot.command(name='help')
async def help_command(ctx):
    """Display help information"""
    embed = discord.Embed(
        title="📝 To-Do List Bot Commands",
        description="Manage your personal to-do list with ease!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="-add <task>",
        value="Add a new task to your to-do list\nExample: `-add Buy groceries`",
        inline=False
    )
    
    embed.add_field(
        name="-list",
        value="View all your tasks with checkboxes",
        inline=False
    )
    
    embed.add_field(
        name="-check <number>",
        value="Mark a task as completed\nExample: `-check 1`",
        inline=False
    )
    
    embed.add_field(
        name="-uncheck <number>",
        value="Mark a task as incomplete\nExample: `-uncheck 1`",
        inline=False
    )
    
    embed.add_field(
        name="-remove <number>",
        value="Delete a task from your list\nExample: `-remove 1`",
        inline=False
    )
    
    embed.add_field(
        name="-clear",
        value="Remove all tasks from your list",
        inline=False
    )
    
    embed.add_field(
        name="-clearCompleted",
        value="Remove all completed tasks",
        inline=False
    )
    
    embed.add_field(
        name="-stats",
        value="View statistics about your tasks",
        inline=False
    )
    
    embed.set_footer(text="Prefix: -")
    
    await ctx.send(embed=embed)

@bot.command(name='add')
async def add_task(ctx, *, task: str):
    """Add a new task to your to-do list"""
    user_id = str(ctx.author.id)
    todos = get_user_todos(user_id)
    
    new_task = {
        "task": task,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    
    todos.append(new_task)
    save_data(todo_data)
    
    embed = discord.Embed(
        title="✅ Task Added",
        description=f"{UNCHECKED} {task}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Task #{len(todos)}")
    
    await ctx.send(embed=embed)

@bot.command(name='list')
async def list_tasks(ctx):
    """Display all tasks"""
    user_id = str(ctx.author.id)
    todos = get_user_todos(user_id)
    
    if not todos:
        embed = discord.Embed(
            title="📝 Your To-Do List",
            description="Your list is empty! Use `-add <task>` to add tasks.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"📝 {ctx.author.name}'s To-Do List",
        color=discord.Color.blue()
    )
    
    task_list = []
    for idx, todo in enumerate(todos, 1):
        checkbox = CHECKED if todo['completed'] else UNCHECKED
        task_text = todo['task']
        if todo['completed']:
            task_text = f"~~{task_text}~~"
        task_list.append(f"**{idx}.** {checkbox} {task_text}")
    
    embed.description = "\n".join(task_list)
    
    completed = sum(1 for t in todos if t['completed'])
    embed.set_footer(text=f"{completed}/{len(todos)} tasks completed")
    
    await ctx.send(embed=embed)

@bot.command(name='check')
async def check_task(ctx, task_number: int):
    """Mark a task as completed"""
    user_id = str(ctx.author.id)
    todos = get_user_todos(user_id)
    
    if not todos:
        await ctx.send("❌ Your to-do list is empty!")
        return
    
    if task_number < 1 or task_number > len(todos):
        await ctx.send(f"❌ Invalid task number! Please use a number between 1 and {len(todos)}.")
        return
    
    task = todos[task_number - 1]
    
    if task['completed']:
        await ctx.send(f"ℹ️ Task #{task_number} is already completed!")
        return
    
    task['completed'] = True
    save_data(todo_data)
    
    embed = discord.Embed(
        title="✅ Task Completed!",
        description=f"{CHECKED} ~~{task['task']}~~",
        color=discord.Color.green()
    )
    
    await ctx.send(embed=embed)

@bot.command(name='uncheck')
async def uncheck_task(ctx, task_number: int):
    """Mark a task as incomplete"""
    user_id = str(ctx.author.id)
    todos = get_user_todos(user_id)
    
    if not todos:
        await ctx.send("❌ Your to-do list is empty!")
        return
    
    if task_number < 1 or task_number > len(todos):
        await ctx.send(f"❌ Invalid task number! Please use a number between 1 and {len(todos)}.")
        return
    
    task = todos[task_number - 1]
    
    if not task['completed']:
        await ctx.send(f"ℹ️ Task #{task_number} is already incomplete!")
        return
    
    task['completed'] = False
    save_data(todo_data)
    
    embed = discord.Embed(
        title="↩️ Task Marked Incomplete",
        description=f"{UNCHECKED} {task['task']}",
        color=discord.Color.orange()
    )
    
    await ctx.send(embed=embed)

@bot.command(name='remove')
async def remove_task(ctx, task_number: int):
    """Remove a task from your list"""
    user_id = str(ctx.author.id)
    todos = get_user_todos(user_id)
    
    if not todos:
        await ctx.send("❌ Your to-do list is empty!")
        return
    
    if task_number < 1 or task_number > len(todos):
        await ctx.send(f"❌ Invalid task number! Please use a number between 1 and {len(todos)}.")
        return
    
    removed_task = todos.pop(task_number - 1)
    save_data(todo_data)
    
    embed = discord.Embed(
        title="🗑️ Task Removed",
        description=f"Removed: {removed_task['task']}",
        color=discord.Color.red()
    )
    
    await ctx.send(embed=embed)

@bot.command(name='clear')
async def clear_all(ctx):
    """Clear all tasks from your list"""
    user_id = str(ctx.author.id)
    todos = get_user_todos(user_id)
    
    if not todos:
        await ctx.send("❌ Your to-do list is already empty!")
        return
    
    count = len(todos)
    todo_data[user_id] = []
    save_data(todo_data)
    
    embed = discord.Embed(
        title="🗑️ List Cleared",
        description=f"Removed all {count} task(s) from your list.",
        color=discord.Color.red()
    )
    
    await ctx.send(embed=embed)

@bot.command(name='clearCompleted')
async def clear_completed(ctx):
    """Remove all completed tasks"""
    user_id = str(ctx.author.id)
    todos = get_user_todos(user_id)
    
    if not todos:
        await ctx.send("❌ Your to-do list is empty!")
        return
    
    initial_count = len(todos)
    todos_filtered = [t for t in todos if not t['completed']]
    removed_count = initial_count - len(todos_filtered)
    
    if removed_count == 0:
        await ctx.send("ℹ️ No completed tasks to remove!")
        return
    
    todo_data[user_id] = todos_filtered
    save_data(todo_data)
    
    embed = discord.Embed(
        title="🗑️ Completed Tasks Cleared",
        description=f"Removed {removed_count} completed task(s).",
        color=discord.Color.green()
    )
    
    await ctx.send(embed=embed)

@bot.command(name='stats')
async def show_stats(ctx):
    """Display statistics about your tasks"""
    user_id = str(ctx.author.id)
    todos = get_user_todos(user_id)
    
    if not todos:
        await ctx.send("❌ Your to-do list is empty! No statistics to show.")
        return
    
    total = len(todos)
    completed = sum(1 for t in todos if t['completed'])
    incomplete = total - completed
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    embed = discord.Embed(
        title="📊 Your To-Do Statistics",
        color=discord.Color.purple()
    )
    
    embed.add_field(name="Total Tasks", value=f"📝 {total}", inline=True)
    embed.add_field(name="Completed", value=f"✅ {completed}", inline=True)
    embed.add_field(name="Incomplete", value=f"⏳ {incomplete}", inline=True)
    embed.add_field(name="Completion Rate", value=f"📈 {completion_rate:.1f}%", inline=False)
    
    # Progress bar
    bar_length = 20
    filled = int(bar_length * completion_rate / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    embed.add_field(name="Progress", value=f"`{bar}`", inline=False)
    
    await ctx.send(embed=embed)

# Error handling
@add_task.error
async def add_task_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please provide a task! Example: `-add Buy groceries`")

@check_task.error
@uncheck_task.error
@remove_task.error
async def task_number_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please provide a task number! Example: `-check 1`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please provide a valid number!")

# Run the bot
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if not TOKEN:
        print("=" * 50)
        print("⚠️  ERROR: DISCORD_TOKEN not found!")
        print("=" * 50)
        print("\nPlease create a .env file with your bot token:")
        print("DISCORD_TOKEN=your_bot_token_here")
        print("\nOr set the environment variable:")
        print("export DISCORD_TOKEN=your_bot_token_here")
        print("=" * 50)
    else:
        print("=" * 50)
        print("Discord To-Do List Bot")
        print("=" * 50)
        print("\nStarting bot...")
        
        try:
            bot.run(TOKEN)
        except discord.LoginFailure:
            print("\n❌ Invalid bot token! Please check your token and try again.")
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")

#----------------------------------------------------------------------------------------------------------------------------

DISCORD_TOKEN="your discord bot token"
