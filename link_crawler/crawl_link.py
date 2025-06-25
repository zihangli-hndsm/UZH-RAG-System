import os
from bs4 import BeautifulSoup
import time
import random
import texthtml
import undetected_chromedriver as uc


class Node:
    def __init__(self, node_url, lang: str, tier=0, children: list = None, no_children=False, father=None):
        self.url = node_url
        self.tier = tier
        self.father = father
        self.lang = lang
        self.no_children = no_children
        if children is None and not no_children:
            self.children = get_children_and_crawl(self)
        else:  # 如果给了children，就等于进入手动添加father的模式
            self.children = children

    def continue_progress(self):
        if self.children:
            for child in self.children:
                child.father = self
                child.continue_progress()
        elif not self.no_children:
            self.children = get_children_and_crawl(self)


def get_children_and_crawl(n: Node):
    # request and parse html
    global progress
    result = []
    driver.get(n.url)
    time.sleep(5)
    response = driver.page_source
    soup = BeautifulSoup(response, 'html.parser')

    # crawling
    results, save_name = texthtml.extract_content(soup, log, n.url)
    if save_name == 'untitled':
        save_name = f"untitled_{n.url.split('/')[-1]}_{'_'.join(n.url.split('/')[4:])}"
        log_and_print(f"Warning: Untitled page: {n.url}")
    save_name = f"{n.lang}_{replace_special_chars(save_name)[-80:]}_{'_'.join(n.url.split('/')[4:])[-80:]}.md"
    if results:
        texthtml.save_into_file(results, './results/' + save_name)
        log_and_print(f"Saved: {save_name}")
        print('*Progress saved, you can interrupt the process now.*')
    else:
        log_and_print(f"Warning: No content found for: {n.url}. So skipped.")
    progress = update_progress(progress, n)
    # Extra sleep!
    time.sleep(random.randint(15, 22))
    print("!!!A new crawl is starting. Don't interrupt the process now!!!")
    time.sleep(2)

    # get children
    list_children = soup.find('ul', {'class': 'Breadcrumb--flyout--list'})
    if list_children and driver.current_url not in visited_links:
        visited_links.add(driver.current_url)
        log_and_print(f"Found children for: {n.url}. (DO NOT END THE PROCESS NOW!)")
        children_a = list_children.find_all('a')
        for a in children_a:
            link = a.get('href')
            if link.startswith('/'):
                link = n.url.split('uzh.ch')[0] + 'uzh.ch' + link
            progress = add_progress(progress, n, link)
        for a in children_a:
            link = a.get('href')
            if link.startswith('/'):
                link = n.url.split('uzh.ch')[0] + 'uzh.ch' + link
            child_node = Node(link, n.lang, n.tier + 1, father=n)
            result.append(child_node)
        write_visited_links(visited_links_path)
    else:
        if driver.current_url in visited_links:
            log_and_print(f"Warning: Already visited: {n.url}")
        else:
            log_and_print('No children found for: ' + n.url)
        n.no_children = True
        progress = complete_progress(progress, n)
        # Check if father tier is complete
        progress = check_complete(progress, n)
        save_progress(progress, progress_path)
    return result


def output_links(top_node, output_file_obj):
    if top_node.url is not None:
        if top_node.url in written_links:
            log_and_print('Link already visited: ' + top_node.url)
            return
        else:
            output_file_obj.write(top_node.url + '\n')
            written_links.add(top_node.url)
        if top_node.children:
            for child in top_node.children:
                output_links(child, output_file_obj)
    else:
        log_and_print('Error: node.url is None')


def log_and_print(msg):
    global log
    log.write(msg + '\n')
    print(msg)


# 每完成一个节点就更新一次进度
def add_progress(progress_list, father_n: Node, link):
    if len(progress_list) == father_n.tier + 1:
        progress_list.append({link: 'False'})
    progress_list[father_n.tier + 1][link] = 'False'
    save_progress(progress_list, progress_path)
    return progress_list


def update_progress(progress_list, n: Node):
    if len(progress_list) == n.tier:
        progress_list.append({})
    progress_list[n.tier][n.url] = 'wip'
    save_progress(progress_list, progress_path)
    return progress_list


def complete_progress(progress_list, n: Node):
    if len(progress_list) == n.tier:
        raise ValueError('Progress list is not long enough for this node')
    progress_list[n.tier][n.url] = 'True'
    save_progress(progress_list, progress_path)
    return progress_list


def check_complete(progress_list, n: Node):
    if len(progress_list) != n.tier + 1:
        raise ValueError('Progress list is not long enough for this node')
    for v in progress_list[-1].values():
        if v != 'True':
            return progress_list
    if n.tier == 0:
        if progress_list[0][n.url] == 'wip':
            progress_list[0][n.url] = 'True'
            log_and_print('野生（没爹）节点完成')
            return progress_list
        else:
            raise ValueError('Working on non-wip root node?!?!')
    print(f"节点{n.url}完成，父节点{n.father.url}完成")
    progress_list[n.tier-1][n.father.url] = 'True'
    progress_list = check_complete(progress_list[:-1], n.father)
    return progress_list


def save_progress(progress_list, path):
    with open(path, 'w', encoding='utf-8') as f_p:
        for i, d in enumerate(progress_list):
            for k, v in d.items():
                f_p.write(f"{i}\t{k}\t{v}\n")


def load_progress(path):
    loaded_progress = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f_p:
            for line in f_p.readlines():
                tier, link, is_complete = line.strip().split('\t')
                if len(loaded_progress) == int(tier):
                    loaded_progress.append({})
                loaded_progress[int(tier)][link] = is_complete
        return loaded_progress
    else:
        log_and_print('Warning: progress.txt not found')
        return []


def get_language_from_url(u):
    if u.find('/en/') != -1:
        return 'en'
    elif u.find('/de/') != -1:
        return 'de'
    else:
        log_and_print('Warning: language not specified for: ' + u)
        return 'de'


def load_nodes_from_progress(progress_list):
    if not progress_list:
        return []
    tier_nodes = [[] for _ in range(len(progress_list))]
    for i in range(len(progress_list)-1, -1, -1):
        new_node = None
        for link, is_complete in progress_list[i].items():
            if is_complete == 'True':
                new_node = Node(link, get_language_from_url(link), i, no_children=True)
            elif is_complete == 'False':
                new_node = Node(link, get_language_from_url(link), i, children=[], no_children=False)
            elif is_complete == 'wip':
                if i == len(progress_list) - 1:
                    new_node = Node(link, get_language_from_url(link), i, children=[], no_children=False)
                else:
                    new_node = Node(link, get_language_from_url(link), i, children=tier_nodes[i+1], no_children=False)
                    for child in tier_nodes[i+1]:
                        child.father = new_node
            if new_node is None:
                raise ValueError('Invalid progress value: ' + link)
            tier_nodes[i].append(new_node)
    return tier_nodes


def load_visited_links(path):
    if os.path.exists(path):
        vl = set()
        with open(path, 'r', encoding='utf-8') as f_v:
            for line in f_v.readlines():
                vl.add(line.strip())
        return vl
    else:
        log_and_print('Warning: visited_links.txt not found')
        return set()


def write_visited_links(path):
    with open(path, 'w', encoding='utf-8') as f_v:
        for link in visited_links:
            f_v.write(link + '\n')


def replace_special_chars(s):
    return s.replace('/', '_').replace(':', '_').replace('?', '').replace('=', '_').replace('&', '_').replace(' ', '_').replace('"', '').replace('*', '').replace('|', '').replace('\n', '')


# initialize driver
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
driver = uc.Chrome(options=options)
time_now = '_'.join([str(i) for i in time.localtime()[1:6]])
log = open(f"./logs/log_{time_now}.txt", 'w', encoding='utf-8')

written_links = set()
visited_links_path = 'visited_links.txt'
progress_path = 'progress.tsv'
visited_links = load_visited_links(visited_links_path)
progress = load_progress(progress_path)  # progress是一个列表，里面每个元素是一个字典，字典的键是节点的url，值是字符串，表示完成状态。
nodes = load_nodes_from_progress(progress)
if nodes:
    log.write('Start crawling...\n')
    for node in nodes[0]:
        if not node.no_children:
            node.continue_progress()  # 继续爬取未完成的节点
else:
    urls = open('urls.txt', 'r', encoding='utf-8').readlines()
    nodes = [[]] * len(urls)
    progress.append({})
    for url in urls:
        progress[0][url.strip()] = 'False'
    for url in urls:
        nodes[0].append(Node(url.strip(), get_language_from_url(url.strip())))
output_file = open('crawled_links.txt', 'w', encoding='utf-8')
for node in nodes:
    output_links(node[0], output_file)
output_file.close()
driver.quit()
