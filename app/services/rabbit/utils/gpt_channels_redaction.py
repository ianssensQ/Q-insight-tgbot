from openai import OpenAI
from decouple import config

GPT_API_TOKEN = config('GPT_API_TOKEN')
client = OpenAI(api_key=GPT_API_TOKEN)


def gpt_redaction(texts):
    if texts:
        prompt = (
            "Below are summaries of various posts from different channels. "
            "Please review these summaries, remove any repetitions, and organize the information logically:\n\n"

        )
        for text in texts:
            prompt += text

        completion = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system",
                 "content": "You are a bot assistant that helps the user summarize information about posts from "
                            "Telegram"},
                {'role': 'user', 'content': f'{prompt}'}
            ],
            temperature=0.5
        )

        organized_summary = completion.choices[0].message.content
        # organized_summary = completion.choices[0].message['content'].strip()
        return organized_summary
    else:
        return 'No data'


if __name__ == '__main__':
    print(gpt_redaction(['Екатерина Мизулина осудила Асхаба Тамаева! ',
                         'На этот раз в руки главы «Лиги Безопасного Интернета» попала история о том,',
                         'как Тамаев слил в сеть личные данные своего разоблачителя и в итоге заставил ',
                         'того извиняться. Екатерина выпустила большую серию постов в своем тг-канале, ',
                         'она заявила, что Асхаб не уважает ислам, а также несколько раз назвала блогера ',
                         '«скамером». Разборки дошли до того, что Мизулиной стали присылать угрозы в личные ',
                         'сообщения…']))
"""
"Ниже приведены краткие описания различных сообщений из телеграм каналов "
"Пожалуйста, просмотри эти резюме, удали все повторения и логически организуй информацию:"
"\n\n"
"Важно чтобы результат был в формате HTML "
"""
