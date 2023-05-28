from bs4 import BeautifulSoup

def get_profile_from_html(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')

    """
        SUMMARY SECTION
    """
    summary_box = soup.find("section", class_="top-card-layout")
    name = summary_box.find("h1").get_text(strip=True)
    description = summary_box.find("h2").get_text(strip=True)

    """
        ABOUT SECTION
    """
    about = soup.find('section', attrs={"data-section":"summary"}).find("p").get_text(strip=True)

    """
        EXPERIENCE SECTION
    """
    experience = []
    experience_blocks = soup.find_all('li', class_='experience-item')
    for block in experience_blocks:
        exp = {}

        exp['title'] = block.find('h3').get_text(strip=True)

        # location
        exp['location'] = block.find('h4').get_text(strip=True)

        # description
        description_element = block.find('p', class_='show-more-less-text__text--more') or block.find('p', class_='show-more-less-text__text--less')
        exp['description'] = description_element.get_text(strip=True) if description_element else ''

        # time range
        exp['time_range'] = block.find('span', class_='date-range').get_text(strip=True)


        experience.append(exp)

    """
        EDUCATION SECTION
    """
    education = []
    education_blocks = soup.find_all('li', class_='education__list-item')
    for block in education_blocks:
        edu = {}
        # organisation
        edu['school'] = block.find('h3').get_text(strip=True)

        # degree
        edu['degree'] = block.find('h4').get_text(strip=True)

        # description
        description_element = block.find('div', attrs={"data-section":"educations"}) if block.find('div', attrs={"data-section":"educations"}) else None
        edu['description'] = description_element.get_text(strip=True) if description_element else ''

        # time range
        exp['time_range'] = block.find('span', class_='date-range').get_text(strip=True)

        education.append(edu)

    """
        CERTIFICATION SECTION
    """
    certification = []
    certification_list = soup.find('ul', class_='certifications__list') if soup.find('ul', class_='certifications__list') else None
    if certification_list:
        certification_blocks = certification_list.find_all('li')
        for block in certification_blocks:
            cert = {}
            # cert name
            cert['certification'] = block.find('h3').get_text(strip=True)
            
            # organization
            cert['organization'] = block.find('h4').get_text(strip=True)

            # time range
            cert['time_range'] = block.find('div', class_='certifications__date-range').get_text(strip=True)

            certification.append(cert)

    # Create the 'item' dictionary
    item = {
        'name': name,
        'description': description,
        'about': about,
        'experience': experience,
        'education': education,
        'certification': certification
    }

    return item