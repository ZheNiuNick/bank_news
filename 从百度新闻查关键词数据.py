# -*- coding: utf-8 -*-

import os
import re
import ssl
import time
import math
import warnings
import datetime
from urllib.parse import quote
from openpyxl import Workbook

import pandas as pd
import requests
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore")


def get_req(url, headers={}, params={}, data={}, json={}, cookies={}, encoding='utf-8', timeout=180, method='GET',
            return_type='text', files=[], proxies={}):
    if method.lower() == 'get':
        req = requests.get(url=url, headers=headers, params=params, cookies=cookies, timeout=timeout, verify=False,
                           proxies=proxies)
    else:
        req = requests.post(url=url, headers=headers, params=params, data=data, json=json, cookies=cookies,
                            timeout=timeout,
                            verify=False, files=files, proxies=proxies)

    if encoding != '':
        req.encoding = encoding
    if return_type == 'text':
        return req.text
    elif return_type == 'byte':
        return req.content
    elif return_type == 'json':
        return req.json()

    return None


def retry_get_req(url, headers={}, params={}, data={}, json={}, cookies={}, encoding='utf-8', timeout=180, method='GET',
                  return_type='text'):
    i = 0
    while i <= 3:
        try:
            html = get_req(url, headers=headers, params=params, data=data, json=json, cookies=cookies,
                           encoding=encoding, method=method,
                           return_type=return_type, timeout=timeout)
        except Exception as e:
            print('报错了呢', str(e), url, params, data, json)
            i += 1
            time.sleep(5)
        else:
            return html
    return None


def write_log(log_file, content, with_time=True, mode='a+', print_line=True):
    # 输出日志
    if print_line:
        print(content)
    file_path = get_file_path(log_file)
    if not os.path.exists(os.path.join(os.getcwd(), file_path)):
        os.makedirs(file_path)
    with open(log_file, mode, encoding='utf-8') as f:
        if with_time:
            f.write(f'输出时间：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {content}')
        else:
            f.write(content)

        f.close()


def check_file_content(file_path, string):
    if not os.path.exists(file_path):
        return False
    f = open(file_path, 'a+', encoding='utf8')
    f.seek(0)
    line = f.readline()
    while line:
        if string in line:
            return True

        line = f.readline()
    return False


def get_file_path(full_path):
    return full_path[0:full_path.rfind(os.path.sep) + 1]


def save_2_excel(df, file_path, check_keys=[], sheet_name='Sheet1'):
    if not os.path.exists(os.path.join(os.getcwd(), get_file_path(file_path))):
        os.makedirs(os.path.join(os.getcwd(), get_file_path(file_path)))
    if not os.path.exists(file_path):
        df.to_excel(file_path, index=False, sheet_name=sheet_name)
    else:
        row_df = pd.DataFrame(pd.read_excel(file_path))
        has_row_num = row_df.shape[0]
        row_num = has_row_num + df.shape[0]
        print('原有数据行数=', has_row_num, '添加后行数=', row_num)

        final_df = pd.concat([row_df, df], ignore_index=True)
        if len(check_keys) > 0:
            final_df.drop_duplicates(check_keys,
                                     keep='first',
                                     inplace=True)
        final_df.to_excel(file_path, index=False, sheet_name=sheet_name)


def get_str_from_json(params_data, with_mark=True):
    url_str = ''
    if with_mark:
        url_str = '?'
    nums = 0
    max_nums = len(params_data)
    for key in params_data:
        nums = nums + 1
        # 如果是最后一位就不要带上&
        # 拼为url字符串
        if nums == max_nums:
            url_str += str(key) + '=' + quote(str(params_data[key]))
        else:
            url_str += str(key) + '=' + quote(str(params_data[key])) + '&'
    return url_str


def get_content(page_url, sleep_time=5, headless=True):
    try:
        option = Options()
        option.add_argument("--incognito")  # 配置隐私模式
        if headless:
            option.add_argument('--headless')  # 配置无界面
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=option)
        # driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=option)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                           Object.defineProperty(navigator,'webdriver',{
                               get: () => undefined
                           })
                       """
        })
        driver.get(page_url)
        time.sleep(1)
        html = driver.page_source
        if '百度安全认证' in html or '百度安全验证' in html:
            headers = {
                'Cookie': 'BIDUPSID=55A07159F608934F4FF1692EAF72748B; PSTM=1687329289; BD_UPN=12314753; BDUSS=FR6YUp0RXpVMmRyNmpJdWNGcTZiRG9uUVJLWmhKRmFHQkVSNjBlQ0RPMURJOUprSVFBQUFBJCQAAAAAAAAAAAEAAADskvwAZHpsaXNoZW4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEOWqmRDlqpkc; BDUSS_BFESS=FR6YUp0RXpVMmRyNmpJdWNGcTZiRG9uUVJLWmhKRmFHQkVSNjBlQ0RPMURJOUprSVFBQUFBJCQAAAAAAAAAAAEAAADskvwAZHpsaXNoZW4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEOWqmRDlqpkc; BAIDUID=03061BB93570E6604D844E75125C6AB2:SL=0:NR=10:FG=1; H_WISE_SIDS=114550_216842_213349_214800_110085_243890_245598_257586_257015_253022_261706_236312_261869_259308_257289_256419_263898_265030_265054_261036_265302_265343_265643_265649_265778_265853_265881_265277_257261_266589_267067_265886_267099_267344_267066_267375_267424_267462_265615_267415_266188_264946_267788_267712_267899_267910_267926_265636_260335_265776_266421_265999_266713_265368_107314_268322_267031_268593_263619_268707_268633_266187_268875_268878_268849_269005_265986_234296_234208_267535_259642_266027_269388_264170_268831_259080_256154_269549_269160_268759_188333_269721_269731_269773_269775_269777_268237_268435_269904_269771_269969_270179_270084_264813_267658_256739_270336_267804; H_WISE_SIDS_BFESS=114550_216842_213349_214800_110085_243890_245598_257586_257015_253022_261706_236312_261869_259308_257289_256419_263898_265030_265054_261036_265302_265343_265643_265649_265778_265853_265881_265277_257261_266589_267067_265886_267099_267344_267066_267375_267424_267462_265615_267415_266188_264946_267788_267712_267899_267910_267926_265636_260335_265776_266421_265999_266713_265368_107314_268322_267031_268593_263619_268707_268633_266187_268875_268878_268849_269005_265986_234296_234208_267535_259642_266027_269388_264170_268831_259080_256154_269549_269160_268759_188333_269721_269731_269773_269775_269777_268237_268435_269904_269771_269969_270179_270084_264813_267658_256739_270336_267804; MCITY=-301%3A; BDSFRCVID=9o8OJexroG0f5RrfI9Ew8Ptpv2KK0gOTDYrEOwXPsp3LGJLVcAw0EG0PtEhTCoub_2AUogKK3gOTHxtF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tR-qVIK5tIK3ejrnhCTVMt_e2x7-2D62aKDs_U3IBhcqJ-ovQT3tjqDXb4u8W58OLTnjLDocWKJJ8UbeWJ5p0bLEhHrULnDJBNOp3hj5tp5nhMJmQt7xLP40-RPH3lQy523iob3vQpnWfhQ3DRoWXPIqbN7P-p5Z5mAqKl0MLPbtbb0xXj_0DjvBea_fJTLsKjAX3JjV5PK_Hn7zeTroeM4pbq7H2M-j5JTNQJQYfl5bbMJmKbDKyUnQbPnn0pcH3mOfhUJb-IOdspcs34bN5T8kQN3T-UQ3Qg7yLRo7tqjlDn3oyTbJXp0n2hOly5jtMgOBBJ0yQ4b4OR5JjxonDh83bG7MJUutfD7H3KCKtD-Kbf5; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BAIDUID_BFESS=03061BB93570E6604D844E75125C6AB2:SL=0:NR=10:FG=1; BDSFRCVID_BFESS=9o8OJexroG0f5RrfI9Ew8Ptpv2KK0gOTDYrEOwXPsp3LGJLVcAw0EG0PtEhTCoub_2AUogKK3gOTHxtF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF_BFESS=tR-qVIK5tIK3ejrnhCTVMt_e2x7-2D62aKDs_U3IBhcqJ-ovQT3tjqDXb4u8W58OLTnjLDocWKJJ8UbeWJ5p0bLEhHrULnDJBNOp3hj5tp5nhMJmQt7xLP40-RPH3lQy523iob3vQpnWfhQ3DRoWXPIqbN7P-p5Z5mAqKl0MLPbtbb0xXj_0DjvBea_fJTLsKjAX3JjV5PK_Hn7zeTroeM4pbq7H2M-j5JTNQJQYfl5bbMJmKbDKyUnQbPnn0pcH3mOfhUJb-IOdspcs34bN5T8kQN3T-UQ3Qg7yLRo7tqjlDn3oyTbJXp0n2hOly5jtMgOBBJ0yQ4b4OR5JjxonDh83bG7MJUutfD7H3KCKtD-Kbf5; delPer=0; BD_CK_SAM=1; PSINO=7; sug=3; sugstore=0; ORIGIN=0; bdime=0; BA_HECTOR=2400200004802k2h050h012c1ie6uq31p; ZFY=LuMjI0DN5dEh:AFx5TS:BcKW0S81Pym1OWypvzylibcxo:C; BD_HOME=1; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; COOKIE_SESSION=1_0_8_8_9_26_1_3_6_8_27_5_11321_0_32_0_1692613305_0_1692613273%7C9%2333482_68_1691411636%7C9; H_PS_645EC=2192h%2BT8pd%2FFo26QIiBB9x8DJMrxUY0BvyarwFlA1foZ4bS8Nh1bixdp2bhjYMenUawu; BDRCVFR[C0p6oIjvx-c]=mbxnW11j9Dfmh7GuZR8mvqV; H_PS_PSSID=36558_39226_39223_39193_39198_39138_39225_39137_39101; kleck=abb412b41a7039225c5360ef0a45df63; BDSVRTM=280; WWW_ST=1692630670208',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
            html = retry_get_req(page_url, headers=headers)
            # print(html)
            return html
        return driver.page_source
    except:
        return ''


def trans_date(publish_date):
    if publish_date == '':
        return ''
    date_now = datetime.datetime.now()
    one_day = datetime.timedelta(days=1)
    match = re.findall(r'(\d+)天前', publish_date)
    if len(match) > 0:
        publish_date = (date_now - one_day * int(match[0])).strftime('%Y年%m月%d日')

    if not '年' in publish_date and re.match('\d+月\d+日', publish_date):
        publish_date = datetime.datetime.now().strftime('%Y年') + publish_date

    if '分钟前' in publish_date or '小时前' in publish_date or '今天' in publish_date:
        publish_date = date_now.strftime('%Y年%m月%d日')

    if '昨天' in publish_date:
        publish_date = (date_now - one_day).strftime('%Y年%m月%d日')
    if '前天' in publish_date:
        publish_date = (date_now - one_day * 2).strftime('%Y年%m月%d日')

    return publish_date


def get_date(string):
    m = re.findall(r'(\d+?年?\d*[月/]\d*日?)', string)
    if len(m) > 0:
        if len(m) == 1:
            return m[0]
        else:
            index = 0
            while index < len(m) - 1:
                if '月' in m[index]:
                    return m[index]
                index += 1
    return ''


class DzSpider(object):
    def __init__(self):

        self.spider_url = 'https://www.baidu.com/s'
        self.start_page = 1
        self.end_page = 50
        self.spider_num = 1
        self.has_finish = False
        self.reset_end_page = True
        # 所有银行
        #
        self.banks = ['成都银行', '南京银行','宁波银行', '西安银行', '齐鲁银行', '常熟银行', '农业银行', '瑞丰银行',
                      '杭州银行', '苏州银行', '浙商银行', '建设银行', '张家港行', '江苏银行', '长沙银行', '苏农银行',
                      '厦门银行', '工商银行', '邮储银行', '交通银行', '北京银行', '重庆银行', '沪农商行', '江阴银行',
                      '招商银行', '兰州银行', '紫金银行', '上海银行', '中国银行', '平安银行', '兴业银行', '浦发银行',
                      '渝农银行', '光大银行', '中信银行', '贵阳银行', '华夏银行', '无锡银行', '民生银行', '郑州银行',
                      '青岛银行', '青农银行']
        # 关键词
        self.keywords = ['移动钱包', '数字货币', '点对点汇款', '第三方s支付', '移动支付', '在线支付',
                         '移动互联网', '数字支付', 'NFC支付',
                         '贷款催收', '网贷平台', '信用评分', '征信', '众筹', '网融', '网贷', '网投', '智能合约',
                         '网上审批', '网上征信',
                         '智能投资咨询', '财富管理', '网上证券交易', '网上货币交易', '网上理财', '网上保险',
                         '网上车险', '理财平台数字身份认证', '多维数据', '分布式会计', '机器学习', '物联网', '区块链',
                         '生物识别', '大数据', '云计算', '5G', '人工智能',
                         '数字风控', '智能风控', '预测模型', '行为建模',
                         '评分模型', '反欺诈模型', '大数据风控', '风控平台', '风险画像', '客户访问模型', '风控模型']
        self.result = None
        # 保存数据的目录
        self.save_folder = './data/百度新闻'
        # 数据已采集的关键词
        # self.spider_log = f'{self.save_folder}/spider.log'
        # 已采集的链接
        self.spider_urls = f'{self.save_folder}/spider_page.log'
        # 所有要采集的链接
        self.spider_links = f'{self.save_folder}/spider_links.log'
        # 已获取采集链接的关键词
        self.has_get = f'{self.save_folder}/has_get.log'

    def run_task(self):
        with open(self.spider_links, 'r', encoding='utf8') as f:
            line = f.readline()
            while line:
                if line.replace('\n', '') == '':
                    line = f.readline()
                    continue
                arr = re.split('[_ ]', line)
                bank = arr[0]
                keyword = arr[1]
                link = arr[2].replace('\n', '')
                bank_obj = {
                    'name': bank,
                    'keyword': keyword,
                    'link': link
                }
                if check_file_content(self.spider_urls, link):
                    print(f'{bank} {keyword} {link} 已采集')
                    line = f.readline()
                    continue
                if not os.path.exists(f'{self.save_folder}{os.path.sep}{bank}.xlsx'):
                    self.result = pd.DataFrame()
                s = self.get_one_page(bank_obj)
                if s:
                    save_2_excel(self.result, f'{self.save_folder}{os.path.sep}{bank}.xlsx', check_keys=['link'])
                line = f.readline()
                time.sleep(5)

    def get_one_page(self, bank_obj):
        req_url = bank_obj.get('link')
        html = get_content(req_url)
        if '百度安全认证' in html or '百度安全验证' in html:
            # write_log(f'{self.save_folder}/bd.html', html, with_time=False, mode='w', print_line=False)
            print('操作太频繁了，被拦截了，稍休息一会儿再来吧')
            exit()
            return None
        if html == '':
            print('没有获取到内容', req_url)
            return None

        doc = pq(html)
        links = doc('#content_left .result-op').items()
        # print(doc('#content_left .result-op'))
        for li in links:
            a = li('a[@class*="news-title"]')
            href = a.attr('href')
            title = a.text()
            publish_date = li('span[@aria-label*="发布于"]').text()
            source = li('span[@aria-label*="新闻来源"]').text()
            summary = li('span[@aria-label*="摘要"]').text()
            publish_date = trans_date(publish_date)
            content = ''
            content_html = get_content(href)
            if content_html != '':
                doc = pq(content_html)
                doc('style').remove()
                doc('script').remove()
                content = doc.text()
            else:
                content = ''
            summary_date = get_date(summary)
            if not '年' in summary_date:
                if not summary_date == '':
                    if not publish_date == '':
                        publish_date = publish_date[0:5] + summary_date
                    else:
                        publish_date = summary_date
                else:
                    publish_date = summary_date
            else:
                publish_date = summary_date

            year = ''
            m = re.findall(r'\d{4}', publish_date)
            if len(m) > 0:
                year = m[0]

            print(f'{"=" * 40}\n'
                  f'总第{self.spider_num}条\n'
                  f'{bank_obj.get("name")} {bank_obj.get("keyword")}\n'
                  f'{title}\n'
                  f'{publish_date}\n'
                  f'{source}\n'
                  f'{summary}\n'
                  f'{href}\n'
                  f'{"=" * 40}\n')
            df_one = pd.DataFrame({
                'bank name': bank_obj.get('name'),
                'keywords': bank_obj.get('keyword'),
                'year': year,
                'time': publish_date,
                'title': title,
                'link': href,
                'content': content,
            }, index=[0])
            self.result = pd.concat([self.result, df_one])
            self.spider_num += 1
        write_log(self.spider_urls, req_url + '\n', with_time=False, print_line=False)
        return True

    def get_links(self, bank_obj):
        params = {
            "rtt": "1",
            "bsst": "1",
            "cl": "2",
            "tn": "news",
            "ie": "utf-8",
            "word": f'{bank_obj.get("name")} {bank_obj.get("keyword")}'
        }
        page_index = bank_obj.get('page_index')
        req_params = get_str_from_json(params)
        req_url = f'{self.spider_url}{req_params}'
        html = get_content(req_url)
        if '百度安全认证' in html or '百度安全验证' in html:
            print('操作太频繁了，被拦截了，稍休息一会儿再来吧')
            print(datetime.datetime.now())
            exit()
        if not check_file_content(self.spider_links, f'{bank_obj.get("name")}_{bank_obj.get("keyword")} {req_url}'):
            write_log(self.spider_links, f'{bank_obj.get("name")}_{bank_obj.get("keyword")} {req_url}\n',
                      with_time=False, print_line=False)
        m = re.findall(r'百度为您找到相关资讯(\d+)个', html)
        if len(m) > 0:
            self.end_page = math.ceil(int(m[0]) / 10)
            print(f'{bank_obj.get("name")}-{bank_obj.get("keyword")} 发现了{m[0]}条数据,共{self.end_page}页')
            write_log(self.has_get,
                      f'{bank_obj.get("name")}-{bank_obj.get("keyword")} 发现了{m[0]}条数据,共{self.end_page}页',
                      with_time=False, print_line=False)
            for index in range(page_index + 1, self.end_page + 1):
                params['pn'] = (index - 1) * 10
                req_params = get_str_from_json(params)
                req_url = f'{self.spider_url}{req_params}'
                if not check_file_content(self.spider_links,
                                          f'{bank_obj.get("name")}_{bank_obj.get("keyword")} {req_url}'):
                    write_log(self.spider_links, f'{bank_obj.get("name")}_{bank_obj.get("keyword")} {req_url}\n',
                              with_time=False, print_line=False)

    def get_spider_links(self):
        for bank in self.banks:
            for kw in self.keywords:
                self.end_page = 50
                bank_obj = {
                    'name': bank,
                    'keyword': kw,
                    'page_index': 1
                }
                if check_file_content(self.has_get, f'{bank}-{kw} '):
                    print(f'{bank}-{kw} 链接已获取了')
                    continue
                self.get_links(bank_obj)
                time.sleep(5)


if __name__ == '__main__':
    spider = DzSpider()

    # 第一步：采集所有要攫取的链接地址，包括多个分页的
    #spider.get_spider_links()

    # 第二步：爬取每个链接页面上的文章信息
    spider.run_task()
