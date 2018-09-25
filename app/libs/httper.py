# 这里使用requests相比urllib较人性化
import requests

# 在Python2中类后面加(object)属于新式类，不加属于经典类，Python3中加不加都属于新式类
class Httper:
    @staticmethod
    def get(url,return_json=True):
        r = requests.get(url)
        if r.status_code !=200:
            return {} if return_json else ''
        return r.json() if return_json else r.text()
