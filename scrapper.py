import sys
from bs4 import BeautifulSoup
import requests
import urllib.request
import os.path
import validators
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from env import Env
_OutputPath = Env._OutputPath

class window(QWidget):
    def __init__(self, parent=None):
        super(window, self).__init__(parent)
        self.lineEdit = QLineEdit()
        self.button = QPushButton("Scrape")
        self.label = QLabel("Please enter URL")
        layout = QHBoxLayout()
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.button)
        vlayout = QVBoxLayout(self)
        vlayout.addWidget(self.label)
        vlayout.addLayout(layout)
        self.button.clicked.connect(lambda: self.runScrape(self.lineEdit.text()))
        self.setLayout(vlayout)

    def getResult(self, url):
        # url = "https://www.ebay.com/itm/Samsung-Galaxy-Note-8-SM-N950-64GB-GSM-Unlocked-Smartphone-9-10-SBI/193322614988?epid=8013301088&hash=item2d02ed00cc:g:kMQAAOSwMD9eJyd9"
        self.label.setText("Running....")
        self.lineEdit.setEnabled(False)
        self.button.setEnabled(False)
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        title = soup.title.text
        description = ''
        price = ''
        try:
            description = soup.find("meta", property="og:description")["content"]
            price = soup.find(itemprop="price").text
            item_number = soup.find(id="descItemNumber").text
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Invalid URL")
            msg.setText("Please enter ebay product URL.")
            msg.exec_()
            return

        imageList = []

        try:
            tmp = soup.find(id="vi_main_img_fs")
            images = tmp.find_all("img")

            for i in range(0, images.__len__()):
                image = images[i]["src"]
                if image != '':
                    valid = validators.url(image)
                    if valid:
                        imageList.append(image.replace("64", "1600"))

        except:
            tmp = soup.find(id="icImg")["src"]
            imageList.append(tmp)

        item_specifics_table = soup.find('div', class_='section')  # table starts here
        rows = item_specifics_table.findAll('tr')  # finding all the content of tr tag and saving it into a list:rows
        specList = []
        for r in range(0, rows.__len__()):
            spec_titles = rows[r].find_all('th');
            if spec_titles.__len__() > 0:
                for st in range(0, spec_titles.__len__()):
                    if st%2 == 0:
                        specList.append(spec_titles[st].text.replace('\n','').replace('\t', ''))
                    else:
                        specList.append(str(spec_titles[st].text.replace('\n', '').replace('\t', ''))+str("\n"))
            spec_contents = rows[r].find_all('td')
            for sc in range(0, spec_contents.__len__()):
                if sc%2 == 0:
                    specList.append(spec_contents[sc].text.replace('\n','').replace('\t', ''))
                else:
                    specList.append(str(spec_contents[sc].text.replace('\n', '').replace('\t', ''))+str("\n"))

        categories = soup.find_all(itemprop="itemListElement")
        for c in range(0, categories.__len__()):
            if c == 0:
                category = categories[c].text
            else:
                category += '/' + categories[c].text
        if (os.path.isdir(_OutputPath) == False):
            os.mkdir(_OutputPath)
        folder = str(_OutputPath) + str("\\") + str(item_number)
        if (os.path.isdir(folder) == False):
            os.mkdir(folder)
        filepath = os.path.join(folder, 'item_info.txt')
        f = open(filepath, "w+", encoding="utf-8")
        separator = "\n"
        separator2 = ""
        f.write("Item Information\n\nTitle:\n\n%s\n\nDescription:\n\n%s\n\nPrice:\n\n%s\n\nItem Number:\n\n%s\n\nImageList:\n\n%s\n\nSpecifications:\n\n%s\n\nCategory:\n\n%s\n" %( title, description, price, item_number, separator.join(imageList), separator2.join(specList), category))
        f.close()
        count = 0
        for img in imageList:
            count += 1
            extension = os.path.basename(img)

            urllib.request.urlretrieve(img, os.path.join(folder, str(count)+str('.')+str(extension.split('.')[-1])))
        return category

    def runScrape(self, url):
        print('start .....')
        print(url)

        valid = validators.url(url)
        print(valid)
        if not valid:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Invalid URL")
            msg.setText("Please enter valid URL.")
            msg.exec_()
            return
        else:
            results = self.getResult(url);
            print(results)
            print('One file created!')
            print('end')
        self.lineEdit.setEnabled(True)
        self.lineEdit.setText("")
        self.button.setEnabled(True)
        self.label.setText("Please enter URL")

def main():
   app = QApplication(sys.argv)
   w = window()
   w.resize(500, 100)
   w.setMinimumSize(500, 100)
   w.setMaximumSize(500, 100)
   w.setWindowTitle("Ebay Scrapping")
   w.show()
   sys.exit(app.exec_())
if __name__ == '__main__':
   main()
