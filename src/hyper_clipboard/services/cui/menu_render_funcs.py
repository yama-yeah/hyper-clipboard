from better_logger import BetterLog, Color

def get_selectable_texts(texts:tuple[str,...])->tuple[str,...]:
    indexed_texts=[]
    for i,text in enumerate(texts):
        indexed_texts.append(f'[{i+1}]{text}')
    indexed_texts.append(f'[{len(texts)+1}]終了')
    return tuple(indexed_texts)

def get_menu(texts:tuple[str,...],header_text:str='メニュー')->str:
    header=BetterLog(texts,Color.CYAN,'',100,'💭',formatter=lambda x:str(x),header_text=header_text).output()
    return header