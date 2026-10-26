import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

BASE_URL='https://www.bbc.com'
ANA_URL='https://www.bbc.com/turkce'


HEADERS={
    'User-Agent':(
        'Mozilla/5.0(Windows NT; Win64; x64)'  #işletim sistemi
        'AppleWebKit/537.36 (KHTML, like Gecko)'  #Tarayıcı motoru bilgisi
        'Chorme/1480.0.7788.97 Safari/537.36'     #chorme tarayıcı taklidi


    )
}

def sayfa_al(url):
    #verilen url i indirip bs4 nesnesini döndüren yardımcı fonk
    try:
        response=requests.get(url,headers=HEADERS,  timeout=10)  #sayfayı indir 10 sn içinde cevap alamazsa hata ver
        response.raise_for_status()   #400 500 gibi hata kodlarıyla oto hata fırlatma
        return BeautifulSoup(response.text , 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"sayfa alınamadı: {e}")
        return None


def haber_detay_al(haber_url):
    #tek haber sayasına gidip detay çekiyoru
    soup=sayfa_al(haber_url)  #haberin sayfasına gitmesi için
    if not soup:
        return None , None
    ozet=None
    article=soup.find('div')
    if article:
        paragraflar=article.find_all('p')   #diviçinde ki bütün p leri bulucak
        #50 karakterden kısa olanları filtrele
        metinler=[p.get_text(strip=True) for p in paragraflar  if len(p.get_text(strip=True)) >50 ]
        if metinler:
            ozet=metinler[0]
    tarih=None
    time_tag=soup.find('time')
    if time_tag:
        tarih=time_tag.get('datetime') or time_tag.get_text(strip=True)

    return ozet, tarih
def ana_sayfadan_haber_al():
    #bbbc türkçe anasayfa üzerinde ki haberleri çekecek olan kısım 
    print(f"Ana Sayfa Haberleri Alınıyor.... {ANA_URL}")
    soup=sayfa_al(ANA_URL) #bbc türkçe sayfasını indir
    if not soup:
        return    #sayfa gelmezse boş liste döndür
    haberler=[]
    gorunen_linkler=set()     #aynı limkleri iki kez eklenmemesi için
    for h3 in soup.find_all('h3'):  #h3 etiketlerini dolaş
        baslik=h3.get_text(strip=True) #h3 tagları değişlkeni içine koydu boşlukları sildik
        if not baslik:
            continue    #boş başlıkları atla
        #h3 içinde a etiketi ara yoksa da h3 üstünde de a olabilir 
        link_tag= h3.find('a') or h3.find_parent('a')
        if not link_tag or 'href' not in link_tag.attrs:
            continue  #link bulamazsa atla
        link = link_tag['href']   #href attiruib unu bul al ve link olarak değişkeknine yaz 
        if not link.startswith('http'):
            link= ANA_URL + link
        if link in gorunen_linkler:
                continue  #linkler daha önce eklenmişse atla 
        gorunen_linkler.add(link)
        if'bbc.com/turkce' in link:
                #bbc türkçe haberi ise bu sayfaya gir özet ve tarihi al
                print(f"haber detayı alınıyor:{baslik}")
                ozet , tarih = haber_detay_al (link)
                time.sleep(1)  #her atılan istekten sonra bekleme sucuya aşırı yüklenmemek için
        else:
                ozet , tarih = None , None  #link dışı kalan durumu boş yap

        haberler.append({
                'baslik' : baslik,
                'link':  link,
                'ozet' : ozet,
                'tarih': tarih,

            })    
    return haberler

def kaydet(haberler):
    '''haber listesini hem json hem de txt olarak kaydeder'''
    zaman_damgasi=datetime.now().strftime('%d-%m-%Y-%M-%S')
    #json kayıt için
    json_kayit=f"haberler_{zaman_damgasi}.json"
    with open (json_kayit, 'w',encoding='utf-8') as f:    #dosyayı utf-8 ile yaz modunda aç
        json.dump(haberler,f, ensure_ascii=False, indent=2)   #haberler listesinde i türkçe karakterleri bozmaz indent okunabilir fotmatı verir
        print(f"json kaydedildi {json_kayit}")
        #txt kayıt
        txt_kayit= f"haberler{zaman_damgasi}.txt"
        with open (txt_kayit, 'w', encoding='utf-8') as f:
            f.write('BBC HABER BAŞLIKLARI')
            f.write(f'çekilme zamanı: {datetime.now().strftime('%d-%m-%Y-%M-%S')}')
            f.write("=" *70 + "\n\n")
            for i, haber in enumerate(haberler, 1):  #haberleri 1 den başlaayrak numaralandır
                f.write(f"{i}, {haber['baslik']} \n")    #haberin numarasını ve başlığıını yazdırdık
                if haber.get('tarih'):
                    f.write(f'Tarih: {haber['tarih']} \n ')
                if haber.get('ozet'):
                     f.write(f'Özet: {haber['ozet'][:200]} \n ')  
                f.write(f"link:{haber['link']}\n")
                f.write("\n") 
            print(f"txt dosyasına kaydedildi {txt_kayit}")
                     

if __name__=="__main__":
    haberler=ana_sayfadan_haber_al()
    if haberler:
        print(f"\n Toplam : {len(haberler)} haber bulundu")
        kaydet (haberler)
    else:
        print("üzgünüz hiç haber bulunmadı")
    


      