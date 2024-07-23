from openai import OpenAI
from decouple import config

GPT_API_TOKEN = config('GPT_API_TOKEN')
client = OpenAI(api_key=GPT_API_TOKEN)


def gpt(text):
    prompt = (
        "Summarize the following Telegram post if it needed, "
        "keeping only the most important information. "
        "Make the summary very concise and to the point:\n\n"
        "breaking the post into main SUBTOPICS, if it needed."
        "Действуй по шаблону: \n\n"
        "**Название поста**: \n\n"
        "Основная информация: (по пунктам)"
        "Выделяй важные слова в тексте"

    )

    full_text = text + prompt
    completion = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {"role": "system",
             "content": " You are a bot assistant that helps the user summarize information about posts from Telegram"},
            {'role': 'user', 'content': f'{full_text}'}
        ],
        temperature=0.5
    )

    text = completion.choices[0].message.content

    return text


if __name__ == '__main__':
    print(gpt('Екатерина Мизулина осудила Асхаба Тамаева! '
              'На этот раз в руки главы «Лиги Безопасного Интернета» попала история о том,'
              'как Тамаев слил в сеть личные данные своего разоблачителя и в итоге заставил '
              'того извиняться. Екатерина выпустила большую серию постов в своем тг-канале, '
              'она заявила, что Асхаб не уважает ислам, а также несколько раз назвала блогера '
              '«скамером». Разборки дошли до того, что Мизулиной стали присылать угрозы в личные '
              'сообщения…'))
