"""
Discordボットからのコマンドを処理するモジュール
"""
import os
import sys
import logging
import asyncio
import discord
from discord.ext import commands

# 親ディレクトリをインポートパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger('youtube-shorts-bot.discord_bot')

class ShortsBot(commands.Bot):
    """YouTubeショート動画生成ボット"""
    
    def __init__(self, command_prefix='!', intents=None, channel_id=None, callback=None):
        """初期化"""
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
        
        super().__init__(command_prefix=command_prefix, intents=intents)
        
        self.channel_id = channel_id or config.DISCORD_CHANNEL_ID
        self.callback = callback
        
        # コマンド登録
        self.add_commands()
    
    async def on_ready(self):
        """ボット起動時の処理"""
        logger.info(f'{self.user.name} としてログインしました')
        if self.channel_id:
            channel = self.get_channel(int(self.channel_id))
            if channel:
                await channel.send('YouTube Shorts ボットが起動しました！ `!shorts テーマ` でショート動画を生成できます。')
    
    async def on_message(self, message):
        """メッセージ受信時の処理"""
        # 自分自身のメッセージを無視
        if message.author == self.user:
            return
        
        # 指定チャンネル以外を無視（設定されている場合）
        if self.channel_id and str(message.channel.id) != self.channel_id:
            return
        
        # コマンド処理
        await self.process_commands(message)
    
    def add_commands(self):
        """コマンドを追加"""
        
        @self.command(name='shorts', help='指定したテーマでショート動画を生成します')
        async def create_shorts(ctx, *, theme):
            """ショート動画を生成するコマンド"""
            if not theme:
                await ctx.send('テーマを指定してください。例: `!shorts 猫`')
                return
            
            # 処理開始メッセージ
            await ctx.send(f'「{theme}」についてのショート動画生成を開始します...')
            
            # バックグラウンドでコールバック実行
            if self.callback:
                # 非同期で動画生成処理を実行
                asyncio.create_task(self.run_callback(ctx, theme))
            else:
                await ctx.send('コールバック関数が設定されていません')
        
        @self.command(name='help_shorts', help='ボットの使い方を表示します')
        async def help_shorts(ctx):
            """ヘルプコマンド"""
            help_text = """
**YouTube Shorts 自動生成ボットの使い方**

`!shorts テーマ` - 指定したテーマでショート動画を生成します
`!help_shorts` - このヘルプを表示します

**例**
`!shorts 猫` - 猫についてのショート動画を生成します
"""
            await ctx.send(help_text)
    
    async def run_callback(self, ctx, theme):
        """
        コールバック関数を実行
        
        Args:
            ctx: コマンドコンテキスト
            theme (str): 動画のテーマ
        """
        try:
            # コールバック実行
            result = await self.callback(theme)
            
            if result.get('success'):
                video_id = result.get('video_id')
                video_url = f"https://youtu.be/{video_id}" if video_id else "不明"
                await ctx.send(f'動画の生成とアップロードが完了しました！\n{video_url}')
            else:
                error = result.get('error', '不明なエラー')
                await ctx.send(f'動画の生成に失敗しました。エラー: {error}')
        
        except Exception as e:
            logger.error(f'コールバック実行中にエラーが発生: {str(e)}')
            await ctx.send(f'エラーが発生しました: {str(e)}')


class DiscordBot:
    """Discord連携クラス"""
    
    def __init__(self, token=None, channel_id=None, command_prefix='!'):
        """初期化"""
        self.token = token or config.DISCORD_TOKEN
        if not self.token:
            # ファイルから読み込み
            token_file = config.DISCORD_TOKEN_FILE
            if os.path.exists(token_file):
                with open(token_file, 'r') as f:
                    self.token = f.read().strip()
        
        if not self.token:
            raise ValueError("Discord Tokenが設定されていません")
        
        self.channel_id = channel_id or config.DISCORD_CHANNEL_ID
        self.command_prefix = command_prefix
        self.bot = None
        self.callback = None
    
    def set_callback(self, callback):
        """
        コールバック関数を設定
        
        Args:
            callback: 非同期コールバック関数 async def callback(theme) -> dict
        """
        self.callback = callback
    
    def run(self):
        """Discordボットを起動"""
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.bot = ShortsBot(
            command_prefix=self.command_prefix,
            intents=intents,
            channel_id=self.channel_id,
            callback=self.callback
        )
        
        logger.info("Discordボットを起動中...")
        self.bot.run(self.token)


if __name__ == "__main__":
    # テスト用コード
    async def test_callback(theme):
        """テスト用のコールバック関数"""
        print(f"テーマ「{theme}」についての処理を実行します")
        # 実際の処理は行わずに成功を返す
        return {
            'success': True,
            'video_id': 'dQw4w9WgXcQ'  # サンプルID
        }
    
    # ボット初期化
    bot = DiscordBot()
    bot.set_callback(test_callback)
    
    # 起動
    bot.run()
