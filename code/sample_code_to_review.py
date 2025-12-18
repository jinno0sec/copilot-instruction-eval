"""
サンプルコード：改善が必要なPythonコード
このコードには意図的に以下の問題があります：
- PEP8違反
- 型ヒントの欠如
- ドキュメント文字列の不足
- エラーハンドリングの不足
"""

def calc(w,h):
    return w*h

def getUserData():
    w=input("Width: ")
    h=input("Height: ")
    return w,h

def processData(data):
    result=[]
    for i in data:
        if i>0:
            result.append(i*2)
    return result

class DataProcessor:
    def __init__(self,data):
        self.data=data
    
    def process(self):
        return [x**2 for x in self.data if x%2==0]

if __name__=="__main__":
    w,h=getUserData()
    area=calc(int(w),int(h))
    print("Result:",area)
    
    nums=[1,2,3,4,5,6,7,8,9,10]
    processor=DataProcessor(nums)
    result=processor.process()
    print("Processed:",result)
