import requests
from bs4 import BeautifulSoup
import datetime

# 基金网站的URL
fund_codes = ['018978', '004156']  # 添加需要查询的基金代码
messages = []
for fund_code in fund_codes:
    url = f'https://fund.eastmoney.com/{fund_code}.html?spm=search'

    # 发送GET请求
    response = requests.get(url)

    # 检查请求是否成功
    if response.status_code == 200:
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到标题元素
        title_element = soup.find('title')

        # 提取标题并指定编码为UTF-8
        title = title_element.text.encode('iso-8859-1').decode('utf-8') if title_element else "Title not found"

        # 提取基金名称部分
        fund_name = title.split('(')[0].strip()

        # 输出基金名称部分和当前时间
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        messages.append(f"基金名称: {fund_name} | 运行时间: {current_time}")

        # 找到包含时间和收益率的<tr>元素
        data_rows = soup.find_all('tr')

        # 获取当前日期
        current_date = datetime.datetime.now().strftime('%m-%d')

        # 初始化最新数据的时间戳和收益率
        latest_time = ""
        latest_rate = ""

        # 遍历每个<tr>元素
        for row in data_rows:
            # 找到时间和收益率所在的<td>元素
            time_element = row.find('td', class_='alignLeft')
            rate_element = row.find('td', class_='RelatedInfo alignRight10 bold')

            # 如果找到了时间和收益率元素，则提取并输出数据
            if time_element and rate_element:
                time = time_element.text.strip()  # 清除空白字符
                rate = rate_element.span.text.strip()  # 获取收益率的文本

                # 更新最新数据的时间戳和收益率
                latest_time = time
                latest_rate = rate

                # 如果当前日期与最新数据日期一致，则输出最新数据并结束循环
                if time == current_date:
                    messages.append(f"时间: {time}, 收益率: {rate}")
                    break

        # 检查是否有更新数据
        if latest_time == current_date:
            messages.append("数据已更新")
        else:
            messages.append("数据未更新，显示昨天的数据：")
            messages.append(f"时间: {latest_time}, 收益率: {latest_rate}")

    else:
        messages.append(f'Failed to retrieve the webpage. Status code: {response.status_code}')

# 加入钉钉推送：
DINGTALK_WEBHOOK_URL = "https://oapi.dingtalk.com/robot/send?access_token=68af6ef5d26f1338bf529e20b641c93b645b8034e3a5e69e4a00152c4010f8ac"

# 发送推送
if DINGTALK_WEBHOOK_URL:
    # 构造钉钉消息
    dingtalk_message = {
        "msgtype": "text",
        "text": {
            "content": "\n\n".join(messages)
        }
    }
    # 发送消息
    response = requests.post(url=DINGTALK_WEBHOOK_URL, json=dingtalk_message)
    print(response.text)
