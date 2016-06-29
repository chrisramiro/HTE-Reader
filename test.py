from openpyxl import Workbook, load_workbook
from word import *
import excel
from scipy.stats import skewtest, skew, ttest_1samp
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(nrows=2, ncols=3)
ax0, ax1, ax2, ax3, ax4, ax5 = axes.flat

bnc = load_workbook('BNC - Noun, Verb, Adj, Adv only - Valid Only - Order Sort.xlsx')
ws = bnc.active
freq_ext_range = 4754
b_col = 5
#bnc_freq = [np.log(int(ws.cell(row=i, column=4).value)) for i in range(2, freq_ext_range)]
bnc_len = [len(ws.cell(row=i, column=2).value) for i in range(2, freq_ext_range)]
bnc_ext = [ws.cell(row=i, column=8).value for i in range(2, freq_ext_range)]
bnc_pearsons = [ws.cell(row=i, column=b_col).value for i in range(2, freq_ext_range)]
bnc_num_senses = [ws.cell(row=i, column=9).value for i in range(2, freq_ext_range)]
ax0.scatter(bnc_len, bnc_pearsons)
ax1.scatter(bnc_len, bnc_num_senses)
ax2.scatter(bnc_len, bnc_ext)
ax0.set_title("BNC All Words - Word Length vs. Pearsons")
ax1.set_title("BNC All Words - Word Length vs. Number of Senses")
ax2.set_title("BNC All Words - Word Length vs. Externality")

coca = load_workbook('COCA - Noun, Verb, Adj, Adv only - Valid Only - Order Sort.xlsx')
ws = coca.active
freq_ext_range = 3725
c_col = 6
#coca_freq = [np.log(int(ws.cell(row=i, column=4).value)) for i in range(2, freq_ext_range)]
coca_len = [len(ws.cell(row=i, column=2).value) for i in range(2, freq_ext_range)]
coca_ext = [ws.cell(row=i, column=9).value for i in range(2, freq_ext_range)]
coca_pearsons = [ws.cell(row=i, column=c_col).value for i in range(2, freq_ext_range)]
coca_num_senses = [ws.cell(row=i, column=10).value for i in range(2, freq_ext_range)]
ax3.scatter(coca_len, coca_pearsons)
ax4.scatter(coca_len, coca_num_senses)
ax5.scatter(coca_len, coca_ext)
ax3.set_title("COCA All Words - Word Length vs. Pearsons")
ax4.set_title("COCA All Words - Word Length vs. Number of Senses")
ax5.set_title("COCA All Words - Word Length vs. Externality")

fig.subplots_adjust(hspace=.5)
plt.show()




"""
coca = load_workbook('BNC - Noun, Verb, Adj, Adv only - Valid Only - Order Sort.xlsx')
ws = coca.active

for i in range(4000, 4754): #4754
    if ws.cell(row=i, column=3).value == "v":
        PoS = "v"
    if ws.cell(row=i, column=3).value == "adv":
        PoS = "av"
    if ws.cell(row=i, column=3).value == "n":
        PoS = "n"
    if ws.cell(row=i, column=3).value == "a":
        PoS = "aj"
    curr_word = Word(ws.cell(row=i, column=2).value, PoS)
    ws.cell(row=i, column=9).value = curr_word.num_senses
    print("FML " + str(i), flush=True)

coca.save('BNC - Noun, Verb, Adj, Adv only - Valid Only - Order Sort.xlsx')



r = requests.get("https://www.kilgarriff.co.uk/BNClists/lemma.num")
soup = bs4.BeautifulSoup(r.content, "html.parser")
result = soup.get_text()

result = " ".join(result.split("\n"))
result = " ".join(result.split("   "))
result = result.split()
order = []
words = []
PoS = []
freq = []

flip = 0
while result:
    order.append(result[0])
    freq.append(result[1])
    words.append(result[2])
    PoS.append(result[3])
    result = result[4::]

wb = Workbook()
ws = wb.active
ws.cell(row=1, column=1).value = "Order"
ws.cell(row=1, column=2).value = "Words"
ws.cell(row=1, column=3).value = "PoS"
ws.cell(row=1, column=4).value = "Freq"

for i in range(len(order)):
    ws.cell(row=i+2, column=1).value = order[i]
    ws.cell(row=i+2, column=2).value = words[i]
    ws.cell(row=i+2, column=3).value = PoS[i]
    ws.cell(row=i+2, column=4).value = freq[i]

wb.save("top_6318_bnc_words.xlsx")"""
