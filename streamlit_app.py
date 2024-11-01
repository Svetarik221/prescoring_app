import os
import openai
import streamlit as st
from parse_hh import get_candidate_info, get_job_description

# Использование API-ключа из переменных сред

# Получение API-ключа из файла secrets.toml
openai.api_key = st.secrets["OPENAI_API_KEY"]


SYSTEM_PROMPT = """
Проскорь кандидата, насколько он подходит для данной вакансии.

Сначала напиши короткий анализ, который будет пояснять оценку.
Отдельно оцени качество заполнения резюме (понятно ли, с какими задачами сталкивался кандидат и каким образом их решал?). Эта оценка должна учитываться при выставлении финальной оценки - нам важно нанимать таких кандидатов, которые могут рассказать про свою работу.
Потом представь результат в виде оценки от 1 до 10.
""".strip()


# Функция для запроса к GPT
def request_gpt(system_prompt, user_prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
            temperature=0,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"Ошибка при обращении к API: {e}")
        return None


# Интерфейс Streamlit
st.title("Приложение для прескоринга кандидатов")

# Подсказка для URL или текста
st.write("Введите URL страницы или текст описания для вакансии и резюме.")

# Ввод URL или текста для описания вакансии и резюме
job_description_url = st.text_area("Введите ссылку или текст описания вакансии")
cv_url = st.text_area("Введите ссылку или текст резюме кандидата")

# Кнопка для запуска оценки
# Кнопка для запуска оценки
# Кнопка для запуска оценки
if st.button("Оценить резюме"):
    with st.spinner("Оцениваем резюме..."):
        # Получение описания вакансии и резюме
        if job_description_url.startswith("http"):
            job_description = get_job_description(job_description_url)
        else:
            job_description = job_description_url  # Если введен текст, используем его напрямую

        if cv_url.startswith("http"):
            cv = get_candidate_info(cv_url)
        else:
            cv = cv_url  # Если введен текст, используем его напрямую

        # Проверка полученных данных
        if not job_description or not cv:
            st.error("Не удалось получить данные по одному из URL.")
        else:
            # Формирование запроса к GPT
            user_prompt = f"# ВАКАНСИЯ\n{job_description}\n\n# РЕЗЮМЕ\n{cv}"
            response = request_gpt(SYSTEM_PROMPT, user_prompt)

            # Вывод результата с выделенными заголовками
            if response:
                # Проверка наличия "Итоговая оценка:"
                if "Итоговая оценка:" in response:
                    analysis, final_score = response.split("Итоговая оценка:", 1)

                    # Вывод вакансии и резюме
                    st.write("### Описание вакансии")
                    st.write(job_description)
                    st.write("### Резюме кандидата")
                    st.write(cv)

                    # Вывод анализа
                    st.write("### Анализ кандидата")
                    st.write(analysis.strip())

                    # Вывод итоговой оценки
                    st.markdown(f"**Итоговая оценка: {final_score.strip()}**")
                else:
                    # Если "Итоговая оценка:" не найдена, выводим весь ответ целиком
                    st.write("### Анализ кандидата")
                    st.write(response)
            else:
                st.error("Не удалось получить ответ от GPT.")
