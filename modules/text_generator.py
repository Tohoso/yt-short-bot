"""
AIを使用してテーマに基づいたテキストを生成するモジュール
"""
import logging
import anthropic
from slugify import slugify
import random
import os
import sys

# 親ディレクトリをインポートパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger('youtube-shorts-bot.text_generator')

class TextGenerator:
    """AIテキスト生成クラス"""
    
    def __init__(self, api_key=None):
        """初期化"""
        # APIキーの設定
        self.api_key = api_key or config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic APIキーが設定されていません")
        
        # Anthropic APIクライアントの初期化
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # テキスト生成のプロンプトテンプレート
        self.prompt_templates = [
            """# 自己啓発ショート動画用インパクト名言生成システム\nあなたは視聴者の心を揺さぶる強力な自己啓発名言を生み出すエキスパートです。与えられたテーマとペルソナに基づき、ショート動画（15-60秒）で使用する10個の心を突き動かす名言を作成してください。
## 入力情報
- **メインテーマ**: {theme}
- **ターゲットペルソナ**: [詳細なペルソナ情報を記入]
- **望まれる感情変化**: [視聴後に期待する感情や行動の変化]
- **キーワード（任意）**: [含めたい特定のキーワード]

## ショート動画名言の特性

### 形式要件
- **文字数制限**: 各名言は厳密に20文字以内
- **名言数**: 正確に10個の名言を生成
- **表示形式**: 箇条書き（番号付き）で表示

### 内容構成（内部指針）
1. **覚醒名言**（視聴者に衝撃を与える）
2. **現状打破名言**（不満や停滞感への共感）
3. **行動喚起名言**（即時行動を促す）
4. **勇気づけ名言**（「勇気」の概念を含む）
5. **時間価値名言**（「今」の重要性を強調）
6. **決断名言**（選択と決断の重要性）
7. **習慣力名言**（小さな習慣の積み重ねの価値）
8. **障害克服名言**（困難への対処）
9. **未来構築名言**（理想の未来へのビジョン）
10. **総括名言**（全体を締めくくる力強いメッセージ）

## 名言作成の詳細指示

### 言語パターンの特徴
- **命令形の活用**: 「行動せよ」「始めろ」など
- **断定的表現**: 「〜だ」「〜である」の文末
- **対比構造**: 「昨日と今日」「凡人と天才」など
- **数字の効果的使用**: 「1日1歩」「7割の勇気」など
- **省略の技法**: 主語や接続詞を省略して簡潔に
- **破調のリズム**: 5-7-5のリズムを意図的に崩す

### 心理的効果を高める技法
- **痛点への直接訴求**: ペルソナの不安や焦りに響く
- **二項対立の提示**: 「行動か後悔か」など選択を迫る
- **希少性の強調**: 「今しかない」「一度きり」など
- **確信の伝達**: 断言による自信の表明
- **感情喚起**: 「恐怖」「歓喚」「感動」などの感情語
- **達成感の予告**: 行動後の満足感を先取りさせる

### 10文字以内で表現するコツ
- 無駄な修飾語を全て排除する
- 主語を省略して述部から始める
- 一般的な表現より強いインパクトのある語彙を選ぶ
- 一文一義の原則を守る（一つの名言に一つのメッセージ）
- 熟語や慣用句を活用して意味を凝縮する
- 「、」や「。」などの句読点もカウントするため最小限に

## 表現技法の詳細（内部用）

### 力強さの表現（70%）
- **音の強さ**: 「ダ・ザ・ガ・バ」などの濁音を効果的に使用
- **切迫感**: 「今」「すぐ」「迷うな」などの緊急性
- **断定**: 「必ず」「絶対」「断言する」などの確信
- **対決姿勢**: 「立ち向かえ」「打ち破れ」などの闘争表現
- **強調語**: 「極限」「最高」「究極」などの限界表現

### 共感と寄り添い（30%）
- **包含表現**: 「共に」「一緒に」などの連帯感
- **励まし**: 「大丈夫」「信じろ」などの肯定
- **理解の表明**: 「わかるさ」「当然だ」などの共感
- **希望**: 「光」「夢」「未来」などの前向きイメージ
- **親近感**: 「君なら」「我々は」などの距離を縮める表現

## 各名言のポジショニング（内部用）

1. **覚醒名言**: 視聴者を「眠り」から叩き起こす衝撃的表現
2. **現状打破名言**: 現状への不満を代弁し、共感を示す
3. **行動喚起名言**: 「今すぐ」行動することの価値を強調
4. **勇気づけ名言**: 「勇気」という言葉を直接使用
5. **時間価値名言**: 「今日」「今」の重要性と「明日」の危険性
6. **決断名言**: 「選べ」「決めろ」など決断を促す
7. **習慣力名言**: 小さな習慣の積み重ねの効果を強調
8. **障害克服名言**: 困難や挫折への対応方法
9. **未来構築名言**: 行動によって生まれる理想の未来
10. **総括名言**: 全体を強く締めくくるパワフルなメッセージ

## 名言間の流れ設計
- 10個の名言全体で「問題提起→共感→解決策→行動喚起→未来展望」のストーリー構造を形成
- 名言間に緩急をつけ、強い表現と柔らかい表現を交互に配置
- 前半で課題を提示し、中盤で解決法を示し、後半で具体的行動と未来像を描く
- 最初と最後の名言は特に印象的なものにする（初頭効果と新近効果）

## ショート動画向け特別考慮事項
- 一瞬で視聴者の注目を引く衝撃的な第一名言
- 音読したときのリズム感と抑揚を考慮
- テロップ表示を前提とした読みやすさと視認性
- スクロールしながら読む体験を想定した構成
- 台詞として発声しやすい音の組み合わせ

## 最終チェックリスト
- [ ] 全ての名言が20文字以内に収まっているか
- [ ] 10個の名言で一貫したストーリー性があるか
- [ ] テーマに沿った内容になっているか
- [ ] 指定されたキーワードが適切に組み込まれているか
- [ ] 力強さと共感のバランスは70:30になっているか
- [ ] ターゲットペルソナの心理に響く内容になっているか
- [ ] 視覚的にインパクトがある表現になっているか
- [ ] 音読したときのリズム感は良いか
- [ ] 意味が明確で誤解を招かない表現か
- [ ] 最初と最後の名言は特に印象的か

このプロンプトに従って、指定されたテーマに関する10個の力強い自己啓発名言（各20文字以内）を作成してください。"""
        ]
    
    def generate_text(self, theme, max_length=100):
        """
        テーマに基づいてテキストを生成する
        
        Args:
            theme (str): テキスト生成のテーマ
            max_length (int): 生成するテキストの最大文字数
        
        Returns:
            str: 生成されたテキスト
            str: 生成されたテキストのslug形式（ファイル名用）
        """
        try:
            # プロンプトテンプレートからランダムに選択
            prompt_template = random.choice(self.prompt_templates)
            prompt = prompt_template.format(theme=theme)
            
            logger.info(f"「{theme}」のテキスト生成を開始")
            
            # Anthropic Claude APIを使用してテキスト生成
            system_prompt = """# 自己啓発ショート動画用インパクト名言生成システム

あなたは視聴者の心を揺さぶる強力な自己啓発名言を生み出すエキスパートです。与えられたテーマとペルソナに基づき、ショート動画（15-60秒）で使用する10個の心を突き動かす名言を作成してください。

## 入力情報
- **メインテーマ**: [動画の中心テーマを記入]
- **ターゲットペルソナ**: [詳細なペルソナ情報を記入]
- **望まれる感情変化**: [視聴後に期待する感情や行動の変化]
- **キーワード（任意）**: [含めたい特定のキーワード]

## ショート動画名言の特性

### 形式要件
- **文字数制限**: 各名言は厳密に20文字以内
- **名言数**: 正確に10個の名言を生成
- **表示形式**: 箇条書き（番号付き）で表示

### 内容構成（内部指針）
1. **覚醒名言**（視聴者に衝撃を与える）
2. **現状打破名言**（不満や停滞感への共感）
3. **行動喚起名言**（即時行動を促す）
4. **勇気づけ名言**（「勇気」の概念を含む）
5. **時間価値名言**（「今」の重要性を強調）
6. **決断名言**（選択と決断の重要性）
7. **習慣力名言**（小さな習慣の積み重ねの価値）
8. **障害克服名言**（困難への対処）
9. **未来構築名言**（理想の未来へのビジョン）
10. **総括名言**（全体を締めくくる力強いメッセージ）

## 名言作成の詳細指示

### 言語パターンの特徴
- **命令形の活用**: 「行動せよ」「始めろ」など
- **断定的表現**: 「〜だ」「〜である」の文末
- **対比構造**: 「昨日と今日」「凡人と天才」など
- **数字の効果的使用**: 「1日1歩」「7割の勇気」など
- **省略の技法**: 主語や接続詞を省略して簡潔に
- **破調のリズム**: 5-7-5のリズムを意図的に崩す

### 心理的効果を高める技法
- **痛点への直接訴求**: ペルソナの不安や焦りに響く
- **二項対立の提示**: 「行動か後悔か」など選択を迫る
- **希少性の強調**: 「今しかない」「一度きり」など
- **確信の伝達**: 断言による自信の表明
- **感情喚起**: 「恐怖」「歓喚」「感動」などの感情語
- **達成感の予告**: 行動後の満足感を先取りさせる

### 10文字以内で表現するコツ
- 無駄な修飾語を全て排除する
- 主語を省略して述部から始める
- 一般的な表現より強いインパクトのある語彙を選ぶ
- 一文一義の原則を守る（一つの名言に一つのメッセージ）
- 熟語や慣用句を活用して意味を凝縮する
- 「、」や「。」などの句読点もカウントするため最小限に

## 表現技法の詳細（内部用）

### 力強さの表現（70%）
- **音の強さ**: 「ダ・ザ・ガ・バ」などの濁音を効果的に使用
- **切迫感**: 「今」「すぐ」「迷うな」などの緊急性
- **断定**: 「必ず」「絶対」「断言する」などの確信
- **対決姿勢**: 「立ち向かえ」「打ち破れ」などの闘争表現
- **強調語**: 「極限」「最高」「究極」などの限界表現

### 共感と寄り添い（30%）
- **包含表現**: 「共に」「一緒に」などの連帯感
- **励まし**: 「大丈夫」「信じろ」などの肯定
- **理解の表明**: 「わかるさ」「当然だ」などの共感
- **希望**: 「光」「夢」「未来」などの前向きイメージ
- **親近感**: 「君なら」「我々は」などの距離を縮める表現

## 各名言のポジショニング（内部用）

1. **覚醒名言**: 視聴者を「眠り」から叩き起こす衝撃的表現
2. **現状打破名言**: 現状への不満を代弁し、共感を示す
3. **行動喚起名言**: 「今すぐ」行動することの価値を強調
4. **勇気づけ名言**: 「勇気」という言葉を直接使用
5. **時間価値名言**: 「今日」「今」の重要性と「明日」の危険性
6. **決断名言**: 「選べ」「決めろ」など決断を促す
7. **習慣力名言**: 小さな習慣の積み重ねの効果を強調
8. **障害克服名言**: 困難や挫折への対応方法
9. **未来構築名言**: 行動によって生まれる理想の未来
10. **総括名言**: 全体を強く締めくくるパワフルなメッセージ

## 名言間の流れ設計
- 10個の名言全体で「問題提起→共感→解決策→行動喚起→未来展望」のストーリー構造を形成
- 名言間に緩急をつけ、強い表現と柔らかい表現を交互に配置
- 前半で課題を提示し、中盤で解決法を示し、後半で具体的行動と未来像を描く
- 最初と最後の名言は特に印象的なものにする（初頭効果と新近効果）

## ショート動画向け特別考慮事項
- 一瞬で視聴者の注目を引く衝撃的な第一名言
- 音読したときのリズム感と抑揚を考慮
- テロップ表示を前提とした読みやすさと視認性
- スクロールしながら読む体験を想定した構成
- 台詞として発声しやすい音の組み合わせ

## 最終チェックリスト
- [ ] 全ての名言が20文字以内に収まっているか
- [ ] 10個の名言で一貫したストーリー性があるか
- [ ] テーマに沿った内容になっているか
- [ ] 指定されたキーワードが適切に組み込まれているか
- [ ] 力強さと共感のバランスは70:30になっているか
- [ ] ターゲットペルソナの心理に響く内容になっているか
- [ ] 視覚的にインパクトがある表現になっているか
- [ ] 音読したときのリズム感は良いか
- [ ] 意味が明確で誤解を招かない表現か
- [ ] 最初と最後の名言は特に印象的か

このプロンプトに従って、指定されたテーマに関する10個の力強い自己啓発名言（各20文字以内）を作成してください。
必ず日本語で応答してください。"""
            
            # Anthropicの正しいAPI呼び出し方法に修正
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",  # 正しいモデル名を使用
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000
            )
            # 生成されたテキストを取得
            raw_text = response.content[0].text.strip()
            
            # 生成されたテキストを行ごとに分割してから処理
            lines = raw_text.split('\n')
            
            # 最初の行がメインテーマや説明文なら除外
            if lines and ('メインテーマ' in lines[0] or '生成します' in lines[0] or 'テーマに関する' in lines[0]):
                lines = lines[1:]
            
            # 箇条書きの行を抽出する
            formatted_lines = []
            for line in lines:
                # 数字や箇条書き記号を取り除く
                clean_line = line.strip()
                # 説明文や見出し、プロンプトが含まれている行をスキップ
                if clean_line and not clean_line.startswith('#') and not clean_line.startswith('[') \
                   and not 'メインテーマ' in clean_line \
                   and not '生成します' in clean_line \
                   and not 'ここでは' in clean_line:
                    # 先頭の番号や記号を削除
                    clean_line = clean_line.lstrip('0123456789.-*• \t')
                    clean_line = clean_line.strip()
                    if clean_line and len(clean_line) <= 30:  # 短い名言のみを抽出
                        formatted_lines.append(clean_line)
            
            # 最大　10個の名言を取得
            formatted_lines = formatted_lines[:10]
            
            # 名言が一つも取得できなかった場合は一行のテキストを使用
            if not formatted_lines:
                if len(raw_text) > max_length:
                    generated_text = raw_text[:max_length] + "..."
                else:
                    generated_text = raw_text
            else:
                # 箇条書きで結合
                generated_text = "\n".join(formatted_lines)
            
            logger.info(f"テキスト生成完了: {generated_text}")
            
            # slugを生成（ファイル名用）
            text_slug = slugify(theme)
            
            return generated_text, text_slug
            
        except Exception as e:
            logger.error(f"テキスト生成中にエラーが発生: {str(e)}")
            # エラーの場合はデフォルトテキストとslugを返す
            return f"{theme}についての動画です", slugify(theme)
    
    def generate_multiple_variations(self, theme, count=3, max_length=100):
        """
        複数のバリエーションを生成する
        
        Args:
            theme (str): テーマ
            count (int): 生成するバリエーション数
            max_length (int): 各テキストの最大長
            
        Returns:
            list: 生成されたテキストのリスト
        """
        variations = []
        for _ in range(count):
            text, _ = self.generate_text(theme, max_length)
            variations.append(text)
        return variations


if __name__ == "__main__":
    # テスト用コード
    import sys
    if len(sys.argv) > 1:
        theme = sys.argv[1]
    else:
        theme = "猫"
    
    generator = TextGenerator()
    text, slug = generator.generate_text(theme)
    
    print(f"テーマ: {theme}")
    print(f"生成テキスト: {text}")
    print(f"Slug: {slug}")
