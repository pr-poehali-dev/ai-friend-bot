import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import Icon from '@/components/ui/icon';

const Index = () => {
  const [botToken, setBotToken] = useState('');
  const [webhookSet, setWebhookSet] = useState(false);

  const botUrl = 'https://functions.poehali.dev/8ab85d66-dcad-4893-86ab-5136ac8b5d49';

  const setWebhook = async () => {
    if (!botToken) {
      alert('Введи токен бота!');
      return;
    }

    try {
      const response = await fetch(
        `https://api.telegram.org/bot${botToken}/setWebhook?url=${botUrl}`,
        { method: 'POST' }
      );
      const data = await response.json();
      
      if (data.ok) {
        setWebhookSet(true);
        alert('✅ Webhook установлен! Бот готов к работе!');
      } else {
        alert('❌ Ошибка: ' + data.description);
      }
    } catch (error) {
      alert('❌ Не удалось подключиться к Telegram API');
    }
  };

  return (
    <div className="min-h-screen gradient-primary">
      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-5xl font-bold text-white mb-4">
            AI Подруга 💕
          </h1>
          <p className="text-xl text-white/80">
            Telegram бот с искусственным интеллектом и генерацией фото
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 mb-8">
          <Card className="glass border-white/20 p-6 animate-scale-in">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 gradient-primary rounded-full flex items-center justify-center">
                <Icon name="MessageCircle" size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Умный чат</h3>
            </div>
            <p className="text-white/80 text-sm">
              AI подруга общается как реальная девушка. Запоминает контекст разговора и меняет стиль общения.
            </p>
          </Card>

          <Card className="glass border-white/20 p-6 animate-scale-in">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 gradient-primary rounded-full flex items-center justify-center">
                <Icon name="Camera" size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Генерация фото</h3>
            </div>
            <p className="text-white/80 text-sm">
              Получай фото одной и той же девушки в разных нарядах и позах. От обычных до откровенных.
            </p>
          </Card>

          <Card className="glass border-white/20 p-6 animate-scale-in">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 gradient-primary rounded-full flex items-center justify-center">
                <Icon name="Settings" size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Настройки характера</h3>
            </div>
            <p className="text-white/80 text-sm">
              4 режима: Дружелюбная, Кокетливая, Игривая, Пошлая. Настраивай уровень откровенности.
            </p>
          </Card>

          <Card className="glass border-white/20 p-6 animate-scale-in">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 gradient-primary rounded-full flex items-center justify-center">
                <Icon name="Crown" size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold text-white">Premium функции</h3>
            </div>
            <p className="text-white/80 text-sm">
              Безлимитные сообщения, все режимы, 18+ контент, настройка откровенности.
            </p>
          </Card>
        </div>

        <Card className="glass border-white/20 p-8 mb-8 animate-fade-in">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">
            🤖 Настройка бота
          </h2>

          <div className="space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center text-white font-bold">
                  1
                </div>
                <h3 className="text-lg font-semibold text-white">
                  Создай бота в Telegram
                </h3>
              </div>
              <p className="text-white/80 text-sm ml-10">
                Открой <a href="https://t.me/BotFather" target="_blank" rel="noopener noreferrer" className="text-secondary underline">@BotFather</a> → отправь <code className="bg-white/10 px-2 py-1 rounded">/newbot</code> → получи токен
              </p>
            </div>

            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center text-white font-bold">
                  2
                </div>
                <h3 className="text-lg font-semibold text-white">
                  Добавь токен в секреты
                </h3>
              </div>
              <p className="text-white/80 text-sm ml-10 mb-3">
                Вставь токен в поле "TELEGRAM_BOT_TOKEN" выше ☝️
              </p>
            </div>

            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center text-white font-bold">
                  3
                </div>
                <h3 className="text-lg font-semibold text-white">
                  Подключи webhook
                </h3>
              </div>
              <div className="ml-10 space-y-3">
                <Input
                  type="text"
                  value={botToken}
                  onChange={(e) => setBotToken(e.target.value)}
                  placeholder="Вставь сюда токен бота"
                  className="glass text-white border-white/20"
                />
                <Button
                  onClick={setWebhook}
                  className="w-full gradient-primary hover:opacity-90"
                  disabled={webhookSet}
                >
                  {webhookSet ? (
                    <>
                      <Icon name="Check" size={18} className="mr-2" />
                      Webhook установлен
                    </>
                  ) : (
                    <>
                      <Icon name="Zap" size={18} className="mr-2" />
                      Установить webhook
                    </>
                  )}
                </Button>
              </div>
            </div>

            {webhookSet && (
              <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-4 ml-10 animate-fade-in">
                <p className="text-white font-semibold flex items-center gap-2">
                  <Icon name="CheckCircle" size={20} className="text-green-400" />
                  Готово! Открой своего бота в Telegram и напиши /start
                </p>
              </div>
            )}
          </div>
        </Card>

        <Card className="glass border-white/20 p-6 animate-fade-in">
          <h3 className="text-xl font-bold text-white mb-4">📋 Команды бота</h3>
          <div className="space-y-2 text-white/80 text-sm">
            <div className="flex items-start gap-3">
              <code className="bg-white/10 px-2 py-1 rounded text-white">/start</code>
              <span>Начать общение с ботом</span>
            </div>
            <div className="flex items-start gap-3">
              <code className="bg-white/10 px-2 py-1 rounded text-white">/photo</code>
              <span>Получить фото от AI подруги</span>
            </div>
            <div className="flex items-start gap-3">
              <code className="bg-white/10 px-2 py-1 rounded text-white">/settings</code>
              <span>Настройки режима и 18+ контента</span>
            </div>
            <div className="flex items-start gap-3">
              <code className="bg-white/10 px-2 py-1 rounded text-white">/mode friendly</code>
              <span>Сменить режим (friendly/flirty/playful/spicy)</span>
            </div>
            <div className="flex items-start gap-3">
              <code className="bg-white/10 px-2 py-1 rounded text-white">/nsfw on</code>
              <span>Включить 18+ режим (Premium)</span>
            </div>
            <div className="flex items-start gap-3">
              <code className="bg-white/10 px-2 py-1 rounded text-white">/profile</code>
              <span>Твой профиль и статистика</span>
            </div>
            <div className="flex items-start gap-3">
              <code className="bg-white/10 px-2 py-1 rounded text-white">/premium</code>
              <span>Информация о Premium подписке</span>
            </div>
          </div>
        </Card>

        <div className="mt-8 text-center">
          <Badge className="glass text-white border-white/30 px-4 py-2">
            <Icon name="Database" size={16} className="mr-2" />
            База данных настроена
          </Badge>
          <Badge className="glass text-white border-white/30 px-4 py-2 ml-2">
            <Icon name="Server" size={16} className="mr-2" />
            Backend развёрнут
          </Badge>
        </div>
      </div>
    </div>
  );
};

export default Index;
