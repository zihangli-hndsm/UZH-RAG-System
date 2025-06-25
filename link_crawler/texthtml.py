import requests
from bs4 import BeautifulSoup
import time
import random

unused_format_tags = ['small', 'sub', 'sup', 'ins', 'del', 'code', 'pre', 'kbd', 'var', 'cite', 'dfn', 'abbr',
                      'address', 'samp', 'blockquote', 'bdo', 'h5', 'h6']


# get html from url
def get_html(link):
    response = requests.get(link)
    response.encoding = 'utf-8'
    return BeautifulSoup(response.text, 'html.parser')
    # 这里返回一个叫soup的东西，混杂了网页上所有的大标题小标题设置总图案之类的乱七八糟的玩意


# get main body content from html，本来应该分开做的但是现在看起来也没用到
def get_content(html_soup):
    return html_soup.find('main', id='main-content')
    # 这里返回了所有叫main-content的东西，下文称之为main_content


# get h1 from main soup, 但看起来好像没用到
def get_title(main_soup):
    intro_section = main_soup.find('section', class_='Intro')
    if intro_section:
        h1 = intro_section.find('h1')
        if h1:
            return h1


# soup 处理函数，处理各种html的有关文本风格的标签
def convert_format_text(ele):
    result = ''
    for elem in ele.children:
        if isinstance(elem, str):
            result += elem
        else:
            match elem.name:
                case 'a':
                    if elem.has_attr('href'):
                        result += f"[{elem.get_text(strip=True)}]({elem['href']})"
                case 'strong':
                    result += f"**{elem.get_text(strip=True)}**"
                case 'b':
                    result += f"**{elem.get_text(strip=True)}**"
                case 'i':
                    result += f"*{elem.get_text(strip=True)}*"
                case 'em':
                    result += f"*{elem.get_text(strip=True)}*"
            # 可拓展处理其他内联标签如 <strong>, <em> 等
    return result


# get other main content from main soup
def extract_content(main_content, logger, link):
    result_content = []
    content_area = main_content.find('section', class_='ContentArea')
    if not content_area:
        return [], 'untitled'
    nav_nodes = main_content.find_all('li', class_='Breadcrumb--list--item')
    intro_section = main_content.find('section', class_='Intro')
    news_intro = main_content.find('header', class_='NewsArticleIntro')
    title = ''
    if intro_section:
        h1 = intro_section.find('h1')
        if h1:
            result_content.append(f"# {h1.text}\n")  # h1的部分反正不见了，看起来是直接从main函数里打了一大锅soup直接做的那么我也直接在这里做了
            title = h1.text
    elif news_intro:
        h1 = intro_section.find('h1')
        if h1:
            result_content.append(f"# {h1.text}\n")
            title = h1.text
    else:
        title = 'untitled'
    if nav_nodes:
        nav_node_names = []
        for node in nav_nodes:
            for ele in node.contents:
                match ele.name:
                    case 'a':
                        nav_node_names.append(ele.get_text(strip=True))
                    case 'button':
                        nav_node_names.append(ele.get_text(strip=True).split('Unterseiten anzeigen')[0])
        result_content.append('**Navigation: ' + '/'.join(nav_node_names) + '**\n')
    if content_area:
        # 每个 TextImage 组件
        for textimage in content_area.find_all('div', class_='TextImage'):
            for ele in textimage.descendants:
                match ele.name:
                    case 'h2':
                        result_content.append(f"## {ele.get_text(strip=True)}\n")
                    case 'h3':
                        result_content.append(f"### {ele.get_text(strip=True)}\n")
                    case 'h4':
                        result_content.append(f"#### {ele.get_text(strip=True)}\n")
                    # p 段落内容
                    case 'p':
                        # Process each element within the paragraph
                        result_content.append(convert_format_text(ele) + '\n')
                    # ul 列表项内容
                    # uls = textimage.find_all('ul', class_='type1')
                    case 'ul':
                        lis = ele.find_all('li')
                        for li in lis:
                            result_content.append(f"- {convert_format_text(li)}\n")
                    case 'a':
                        if ele.has_attr('href'):
                            result_content.append(f"[{ele.get_text(strip=True)}]({ele['href']})\n")
                    # 表格table, 只处理了tbodys
                    case 'table':
                        thead = ele.find('thead')
                        tbody = ele.find('tbody')
                        if thead:  # thead目前还没遇到过
                            t_len = 0
                            for tr in thead.find_all('tr'):
                                table_ele = [th.text for th in tr.find_all('th')]
                                t_len = len(table_ele)
                                result_content.append('|' + '| '.join(table_ele) + '|\n')
                            if tbody:
                                result_content.append('|----' * t_len + '|\n')
                        if tbody:
                            if tbody.find('th'):
                                t_len = len(tbody.find('tr').find_all('th'))
                                logger.write(f"Warning: table with th in tbody found at {link}!\n")
                            elif tbody.find('tr'):
                                t_len = len(tbody.find('tr').find_all('td'))
                            else:
                                logger.write(f"Warning: table with empty tbody found at {link}!\n")
                                continue
                            if not thead:
                                result_content.append('|table_col' * t_len + '|\n')
                                result_content.append('|----' * t_len + '|\n')
                            for tr in tbody.find_all('tr'):
                                table_ele = [td.text for td in tr.find_all('td')]
                                result_content.append('|' + '| '.join(table_ele) + '|\n')
                        logger.write(f"Table warning! {link}!\n")
                    case _:
                        if ele.name in unused_format_tags:
                            logger.write(f"Warning: unused format tag {ele.name} found at {link}!\n")
    return result_content, title


def save_into_file(text_list, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(line for line in text_list)


def get_info(link):
    soup = get_html(link)
    return extract_content(soup, log, link)


def read_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls


if __name__ == '__main__':
    log = open('log.txt', 'w', encoding='utf-8')
    # url = input("请输入要爬取的网页URL：").strip() 一个网页的单独爬取现在变成废案力
    urls = read_html('urls.txt')  # 记得把要爬的html放在这个文件里哈
    for i, url in enumerate(urls):
        results, savename = get_info(url)
        if savename == 'untitled':
            savename = f"untitled_{i}.md"
        save_into_file(results, savename)
        print(f"Saved: {savename}")
        time.sleep(random.uniform(0, 1))  # 嘿哈！全能的timesleep！
    print('done!')
