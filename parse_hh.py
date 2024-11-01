import requests
from bs4 import BeautifulSoup

import urllib.parse
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def get_html(url: str):
    try:
        # Кодируем URL для безопасной передачи
        encoded_url = urllib.parse.quote(url, safe=':/?=&')

        # Настройка повторных попыток на случай нестабильных подключений
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))

        response = session.get(
            encoded_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
                "Accept-Charset": "utf-8"
            },
        )
        response.raise_for_status()  # Проверяем, не возникли ли ошибки
        response.encoding = 'utf-8'  # Устанавливаем корректную кодировку для ответа
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении страницы: {e}")
        return None


def extract_vacancy_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # Извлечение заголовка вакансии
    title_tag = soup.find("h1", {"data-qa": "vacancy-title"})
    title = title_tag.text.strip() if title_tag else "Название вакансии не указано"

    # Извлечение зарплаты
    salary_tag = soup.find("span", {"data-qa": "vacancy-salary-compensation-type-net"})
    salary = salary_tag.text.strip() if salary_tag else "Зарплата не указана"

    # Извлечение опыта работы
    experience_tag = soup.find("span", {"data-qa": "vacancy-experience"})
    experience = experience_tag.text.strip() if experience_tag else "Опыт работы не указан"

    # Извлечение типа занятости и режима работы
    employment_mode_tag = soup.find("p", {"data-qa": "vacancy-view-employment-mode"})
    employment_mode = employment_mode_tag.text.strip() if employment_mode_tag else "Тип занятости не указан"

    # Извлечение компании
    company_tag = soup.find("a", {"data-qa": "vacancy-company-name"})
    company = company_tag.text.strip() if company_tag else "Компания не указана"

    # Извлечение местоположения
    location_tag = soup.find("p", {"data-qa": "vacancy-view-location"})
    location = location_tag.text.strip() if location_tag else "Местоположение не указано"

    # Извлечение описания вакансии
    description_tag = soup.find("div", {"data-qa": "vacancy-description"})
    description = description_tag.text.strip() if description_tag else "Описание вакансии отсутствует"

    # Извлечение ключевых навыков
    skills_tags = soup.find_all("div", {"class": "magritte-tag__label___YHV-o_3-0-3"})
    skills = [skill.text.strip() for skill in skills_tags] if skills_tags else ["Навыки не указаны"]

    # Формирование строки в формате Markdown без f-строк
    markdown = """
# {}

**Компания:** {}
**Зарплата:** {}
**Опыт работы:** {}
**Тип занятости и режим работы:** {}
**Местоположение:** {}

## Описание вакансии
{}

## Ключевые навыки
- {}
""".format(
        title,
        company,
        salary,
        experience,
        employment_mode,
        location,
        description,
        '\n- '.join(skills)
    )

    return markdown.strip()

def extract_candidate_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Извлечение основных данных кандидата
    name_tag = soup.find('h2', {'data-qa': 'bloko-header-1'})
    name = name_tag.text.strip() if name_tag else "Имя кандидата не указано"

    gender_age_tag = soup.find('p')
    gender_age = gender_age_tag.text.strip() if gender_age_tag else "Пол и возраст не указаны"

    location_tag = soup.find('span', {'data-qa': 'resume-personal-address'})
    location = location_tag.text.strip() if location_tag else "Местоположение не указано"

    job_title_tag = soup.find('span', {'data-qa': 'resume-block-title-position'})
    job_title = job_title_tag.text.strip() if job_title_tag else "Должность не указана"

    job_status_tag = soup.find('span', {'data-qa': 'job-search-status'})
    job_status = job_status_tag.text.strip() if job_status_tag else "Статус не указан"

    # Извлечение опыта работы
    experience_section = soup.find('div', {'data-qa': 'resume-block-experience'})
    experiences = []
    if experience_section:
        experience_items = experience_section.find_all('div', class_='resume-block-item-gap')
        for item in experience_items:
            period_tag = item.find('div', class_='bloko-column_s-2')
            period = period_tag.text.strip() if period_tag else "Период работы не указан"

            duration_tag = item.find('div', class_='bloko-text')
            duration = duration_tag.text.strip() if duration_tag else ""

            period = f"{period} ({duration})" if duration else period

            company_tag = item.find('div', class_='bloko-text_strong')
            company = company_tag.text.strip() if company_tag else "Компания не указана"

            position_tag = item.find('div', {'data-qa': 'resume-block-experience-position'})
            position = position_tag.text.strip() if position_tag else "Должность не указана"

            description_tag = item.find('div', {'data-qa': 'resume-block-experience-description'})
            description = description_tag.text.strip() if description_tag else "Описание работы отсутствует"

            experiences.append(f"**{period}**\n\n*{company}*\n\n**{position}**\n\n{description}\n")

    # Извлечение ключевых навыков
    skills_section = soup.find('div', {'data-qa': 'skills-table'})
    skills = [skill.text.strip() for skill in skills_section.find_all('span', {'data-qa': 'bloko-tag__text'})] if skills_section else ["Навыки не указаны"]

    # Формирование строки в формате Markdown
    markdown = "# {}\n\n".format(name)
    markdown += "**{}**\n\n".format(gender_age)
    markdown += "**Местоположение:** {}\n\n".format(location)
    markdown += "**Должность:** {}\n\n".format(job_title)
    markdown += "**Статус:** {}\n\n".format(job_status)
    markdown += "## Опыт работы\n\n"
    for exp in experiences:
        markdown += exp + "\n"
    markdown += "## Ключевые навыки\n\n"
    markdown += ', '.join(skills) + "\n"

    return markdown

def get_candidate_info(url: str):
    response = get_html(url)
    if response:
        return extract_candidate_data(response.text)
    return "Не удалось получить данные резюме."

def get_job_description(url: str):
    response = get_html(url)
    if response:
        return extract_vacancy_data(response.text)
    return "Не удалось получить данные вакансии."
