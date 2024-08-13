#
# ラマ 1.1
# Lama.py 2024/8/13
#
DEBUG_MODE = False
import pyxel
ADJX, ADJY = -10, -12
WIDTH, HEIGHT = 176+ADJX*2, 176+ADJY*2+4
HAND_X = (16*2+ADJX, 16+ADJX, 16*8+ADJX, 16*9+ADJX)
HAND_Y = (16*9+ADJY, 16*2+ADJY, 16+ADJY, 16*8+ADJY)
DISCARD_X, DISCARD_Y = 16*5+ADJX, 16*5+ADJY
QUITMARK_X = (DISCARD_X-7, DISCARD_X-23, DISCARD_X+7, DISCARD_X+23)
QUITMARK_Y = (DISCARD_Y+23, DISCARD_Y-8, DISCARD_Y-23, DISCARD_Y+8)
QUITBTN_X, QUITBTN_Y = 16-4+ADJX, 16*9+ADJY
ADD_X = (DISCARD_X+9, DISCARD_X-20, DISCARD_X-4, DISCARD_X+25)
ADD_Y = (DISCARD_Y+25, DISCARD_Y+9, DISCARD_Y-21, DISCARD_Y-5)
DECK_X, DECK_Y = 16*2+8+ADJX, 16*7+8+ADJY
CHIP_X = (16*3+11+ADJX, 16*2+5+ADJX, 16*6+6+ADJX, 16*7+11+ADJX)
CHIP_Y = (16*7+11+ADJY, 16*3+9+ADJY, 16*2+5+ADJY, 16*6+6+ADJY)
CHARA_X = (ADJX, 16*2+2+ADJX, 16*7+6+ADJX, 16*7+10+ADJX) 
CHARA_Y = (ADJY, 16*2+6+ADJY, 16*2+2+ADJY ,16*7+5+ADJY)
MODE_X, MODE_Y = DISCARD_X-18, DISCARD_Y+26
OWN, P1, P2, P3 = 0, 1, 2, 3
NEXT = {OWN:P1, P1:P2, P2:P3, P3:OWN}
MD_LAMA, MD_KUMA = 1, 2
WIN_PLAYOUT, WIN_COMPLETE = 1, 2
ST_TITLE,ST_DEAL,ST_NEXT,ST_COM,ST_PICK,ST_PICKED,ST_DISCARD,ST_DRAW,ST_JUDGE,ST_ROUNDEND,ST_GAMEEND = 101,102,103,104,105,106,107,108,109,110,111
ATTR1 = (6,6,6,6, 6,6,6,5, 5,5,4,4)  # ATTR1枚以上の種類があれば各1枚アガリを狙う
ATTR2 = (4,3,3,2, 2,1,1,3, 2,1,3,2)  # 相手カード平均枚数がATTR2枚以上なら引く
ATTR3 = (6,5,8,4, 9,7,3,6, 5,4,7,5)  # 追加チップATTR3以下なら降りる
MOVE_STEP = 6

class Confetti:  # 紙吹雪
    def __init__(self, x, y, w, h):
        self.x, self.y, self.h, self.c = pyxel.rndi(0, w-1), y, h, pyxel.rndi(6, 15)

    def update(self):
        self.x += pyxel.rndi(-1, 1)
        self.y += 1
        return True if self.y>=self.h else False

    def draw(self):
        pyxel.rect(self.x, self.y, 2, 2, self.c)

class App:
    def gamestart(self):
        self.chara = [i for i in range(12)]
        self.chip = [0, 0, 0, 0]
        self.win_list = []
        self.turn = pyxel.rndi(OWN, P3)
        self.roundstart()

    def roundstart(self):
        self.add_chip = [0, 0, 0, 0]
        self.win_round = [0, 0, 0, 0]
        self.quit_round = [False, False, False, False]
        self.discard = []
        self.hand = [[], [], [], []]
        self.deck = list(range(1,8))*(5 if self.mode==MD_KUMA else 8)
        self.overchip = 50 if self.mode==MD_KUMA else 40
        self.shuffle(self.deck)
        self.cnt = 0
        self.deal_num, self.card_no = 0, 0  # 引いた枚数、カード番号
        self.pick_pos, self.pick_no = -1, 0
        self.sx, self.sy, self.ex, self.ey = -1, -1, -1, -1

    def titledeal(self):
        self.shuffle(self.chara)
        self.hand = [[], [], [], []]
        self.deck = list(range(1,8))*(5 if self.mode==MD_KUMA else 8)
        self.shuffle(self.deck)
        for i in range(4):
            self.hand[i] = self.deck[0:6]
            del self.deck[0:6]

    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title='Lama 1.1')
        pyxel.load('assets/Lama.pyxres')
        pyxel.mouse(True)
        self.conft = []  # 紙吹雪
        self.rept = 0
        self.reveal = False
        self.mode = 0
        self.gamestart()
        self.st = ST_TITLE
        pyxel.run(self.update, self.draw)

    def holddown(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, hold=70, repeat=1):
            if self.rept==0:
                self.rept = 1
            elif self.rept==1:
                self.rept = 2
                self.reveal = not self.reveal
                pyxel.play(0, 0 if self.reveal else 1)  # オープンモード切替え音
        else:
            self.rept = 0

    def click(self):
        card_pos, card_no = -2, 0
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            card_pos = -1
            x, y = HAND_X[OWN], HAND_Y[OWN]  # 手札
            num = len(self.hand[OWN])
            max_x = num if num<=7 else len(set(self.hand[OWN]))
            if x<=pyxel.mouse_x<x+16*max_x and y<=pyxel.mouse_y<y+16:
                card_pos = (pyxel.mouse_x-x)//16
                if num<=7:
                    card_no = self.hand[OWN][card_pos]
                else:
                    card_no = sorted(set(self.hand[OWN]))[card_pos]
                canplay1 = self.discard[-1][2]
                canplay2 = 1 if canplay1==7 else canplay1+1
                if not card_no in (canplay1, canplay2):
                    card_pos, card_no = -1, 0
            x, y = DECK_X, DECK_Y  # 山札
            if self.deck and self.quit_round.count(False)>=2 and x<=pyxel.mouse_x<x+16 and y<=pyxel.mouse_y<y+16:  # 山札がある＋相手が一人以上いる：引く
                card_pos = 7
            x, y = QUITBTN_X, QUITBTN_Y  # 降りる
            if x<=pyxel.mouse_x<x+16 and y<=pyxel.mouse_y<y+16:
                card_pos = 8
        return card_pos, card_no

    def shuffle(self, s):
        for _ in range(len(s)*3):
            a, b = pyxel.rndi(0,len(s)-1), pyxel.rndi(0,len(s)-1)
            s[a], s[b] = s[b], s[a]

    def card_space(self, n):
        return 16 if n<=6 else 11 if n<=8 else 8 if n<=11 else 6

    def update(self):
        self.holddown()

        if self.st==ST_TITLE:
            self.cnt += 1
            if self.cnt==1:
                self.titledeal()
            elif self.cnt>=128:
                self.cnt = 0
            if MODE_X<=pyxel.mouse_x<MODE_X+52 and MODE_Y-4<=pyxel.mouse_y<MODE_Y+12:  # ラマモード
                if self.mode!=MD_LAMA:
                    self.mode = MD_LAMA
                    self.discard = [[DISCARD_X, DISCARD_Y, 7, OWN],]
                    self.cnt = 0
            elif MODE_X<=pyxel.mouse_x<MODE_X+52 and MODE_Y+16-4<=pyxel.mouse_y<MODE_Y+16+12:  # クマモード
                if self.mode!=MD_KUMA:
                    self.mode = MD_KUMA
                    self.discard = [[DISCARD_X, DISCARD_Y, 7, OWN],]
                    self.cnt = 0
            else:
                self.mode = 0
                self.discard = []
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) and self.mode in (MD_LAMA, MD_KUMA):
                self.roundstart()
                self.st = ST_DEAL

        elif self.st==ST_DEAL:
            self.cnt += 1
            if self.cnt==1:
                self.sx, self.sy = DECK_X, DECK_Y-8
                if self.deal_num==24:  # 山札から捨て山
                    self.ex, self.ey = DISCARD_X, DISCARD_Y
                else:  # 山札から手札
                    if self.turn==OWN:
                        num = len(self.hand[OWN])
                        max_x = num if num<=7 else len(set(self.hand[OWN]))
                        self.ex, self.ey = HAND_X[OWN]+16*(max_x), HAND_Y[OWN]
                    elif self.turn==P1:
                        self.ex, self.ey = HAND_X[self.turn], HAND_Y[self.turn]+self.card_space(len(self.hand[P1]))*len(self.hand[self.turn])
                    elif self.turn==P2:
                        self.ex, self.ey = HAND_X[self.turn]-self.card_space(len(self.hand[P2]))*len(self.hand[self.turn]), HAND_Y[self.turn]
                    elif self.turn==P3:
                        self.ex, self.ey = HAND_X[self.turn], HAND_Y[self.turn]-self.card_space(len(self.hand[P3]))*len(self.hand[self.turn])
                self.card_no = self.deck[0]
                del self.deck[0]
                pyxel.play(0, 6)  # 配る音
            if self.cnt>=MOVE_STEP:
                if self.deal_num==24:  # 山札から捨て山
                    self.discard = [[DISCARD_X, DISCARD_Y, self.card_no, OWN],]
                else:  # 山札から手札
                    self.hand[self.turn].append(self.card_no)
                    self.turn = NEXT[self.turn]
                self.cnt = 0
                self.deal_num += 1
                if self.deal_num>24:
                    self.hand[OWN].sort()
                    self.st = ST_NEXT

        elif self.st==ST_NEXT:
            self.turn = NEXT[self.turn]  # 次の番
            if not self.quit_round[self.turn]:  # 降りていない
                if self.turn==OWN:
                    canplay1 = self.discard[-1][2]
                    canplay2 = 1 if canplay1==7 else canplay1+1
                    if (not self.deck or self.quit_round.count(False)==1) and not canplay1 in self.hand[OWN] and not canplay2 in self.hand[OWN]:  # 降りるのみ：自動選択
                        self.quit_round[OWN] = True
                        pyxel.play(0, 8)  # 降りる音
                        self.st = ST_JUDGE
                    elif not self.quit_round[OWN]:  # 降りていない
                        self.st = ST_PICK
                else:  # P1,P2,P3
                    self.cnt = 12 if self.quit_round[OWN] else 0
                    self.st = ST_COM

        elif self.st==ST_COM:  # コンピュータの手
            self.cnt += 1
            if self.cnt>=16:
                remainplayer = self.quit_round.count(False)  # 降りていないプレイヤー数
                cardset = len(set(self.hand[self.turn]))  # カードの種類（～7）
                cardnum = len(self.hand[self.turn])  # 自分カードの枚数
                avgcardnum = 0
                if remainplayer>=2:
                    avgcardnum = -cardnum  # 相手カードの合計枚数
                    for p in (OWN,P1,P2,P3):
                        avgcardnum += 0 if self.quit_round[p] else len(self.hand[p])
                    avgcardnum = avgcardnum//(remainplayer-1)
                decknum = len(self.deck)  # 山札の枚数
                candraw = decknum and remainplayer>=2  # 山札がある＋降りていないプレイヤーが2以上：引ける
                card1 = self.discard[-1][2]  # トップカード番号
                card2 = 1 if card1==7 else card1+1  # ネクストカード番号
                pos1 = self.hand[self.turn].index(card1) if card1 in self.hand[self.turn] else -1  # トップカード番号の位置
                pos2 = self.hand[self.turn].index(card2) if card2 in self.hand[self.turn] else -1  # ネクストカード番号の位置
                addchip = sum(set(self.hand[self.turn]))+(3 if 7 in self.hand[self.turn] else 0)  # 追加チップ
                allchip = self.chip[self.turn]+addchip  # 現在チップ＋追加チップ

                if pos1!=-1 and remainplayer==1:
                    pos = pos1  # トップカードあり＋プレイヤー1人：捨てる
                elif self.mode==MD_KUMA and self.hand[self.turn].count(card1)>=2 and cardset<ATTR1[self.chara[self.turn]]: 
                    pos = pos1  # トップカード2枚＋ATTR1種類未満：捨てる
                elif self.mode==MD_KUMA and self.hand[self.turn].count(card2)>=2:
                    pos = pos2  # ネクストカード2枚：捨てる
                elif self.mode==MD_KUMA and candraw and cardset>=ATTR1[self.chara[self.turn]] and cardset+decknum>=7: 
                    pos = -1  # ATTR1種類以上で各1枚アガリ：引く
                elif pos1!=-1:
                    pos = pos1  # トップカードあり：捨てる
                    if pos2!=-1 and remainplayer>=3 and cardnum>=6 and card1!=7:
                        pos = pos2  # プレイヤー3人以上＋自分カード6枚以上＋トップカードがラマ以外：ネクストカード捨てる
                elif pos2!=-1:
                    pos = pos2  # ネクストカードあり：捨てる
                elif candraw and avgcardnum>=ATTR2[self.chara[self.turn]]:
                    pos = -1  # 相手の持ちカード平均がATTR2以上：引く
                elif allchip<self.overchip and addchip<=ATTR3[self.chara[self.turn]]:
                    pos = -2  # （現在チップ＋追加チップ）がoverchip未満＋追加チップATTR3以下：降りる
                elif candraw:
                    pos = -1  # ：引く
                else:
                    pos = -2  # 降りる

                if pos>=0:  # 捨てる
                    self.pick_pos = pos
                    self.pick_no = self.hand[self.turn][pos]
                    if self.turn==P1:
                        self.sx, self.sy = HAND_X[self.turn], HAND_Y[self.turn]+self.card_space(len(self.hand[P1]))*pos
                        self.ex, self.ey = DISCARD_X+pyxel.rndi(-4,-7), DISCARD_Y+pyxel.rndi(-6,6)
                    elif self.turn==P2:
                        self.sx, self.sy = HAND_X[self.turn]-self.card_space(len(self.hand[P1]))*pos, HAND_Y[self.turn]
                        self.ex, self.ey = DISCARD_X+pyxel.rndi(-6,6), DISCARD_Y+pyxel.rndi(-4,-7)
                    else:  # self.turn==P3:
                        self.sx, self.sy = HAND_X[self.turn], HAND_Y[self.turn]-self.card_space(len(self.hand[P1]))*pos
                        self.ex, self.ey = DISCARD_X+pyxel.rndi(4,7), DISCARD_Y+pyxel.rndi(-6,6)
                    self.cnt = 0
                    pyxel.play(0, 7)  # 捨てる音／引く音
                    self.st = ST_DISCARD
                elif pos==-1:  # 引く
                    self.sx, self.sy = DECK_X, DECK_Y-6
                    if self.turn==P1:
                        self.ex, self.ey = HAND_X[self.turn], HAND_Y[self.turn]+self.card_space(len(self.hand[P1]))*len(self.hand[self.turn])
                    elif self.turn==P2:
                        self.ex, self.ey = HAND_X[self.turn]-self.card_space(len(self.hand[P2]))*len(self.hand[self.turn]), HAND_Y[self.turn]
                    elif self.turn==P3:
                        self.ex, self.ey = HAND_X[self.turn], HAND_Y[self.turn]-self.card_space(len(self.hand[P3]))*len(self.hand[self.turn])
                    self.pick_pos = 7
                    self.cnt = 0
                    pyxel.play(0, 7)  # 捨てる音／引く音
                    self.st = ST_DRAW
                else:  # 降りる
                    self.quit_round[self.turn] = True
                    pyxel.play(0, 8)  # 降りる音
                    self.st = ST_JUDGE

        elif self.st==ST_PICK:  # OWN
            self.pick_pos, _ = self.click()
            if self.pick_pos>=0:
                pyxel.play(0, 3)  # 選択音
                self.st = ST_PICKED

        elif self.st==ST_PICKED:  # OWN
            pos, self.pick_no = self.click()
            if pos==self.pick_pos:
                if 0<=self.pick_pos<7:  # 手札から捨て山
                    self.sx, self.sy = HAND_X[OWN]+16*pos, HAND_Y[OWN]-6
                    self.ex, self.ey = DISCARD_X+pyxel.rndi(-6,6), DISCARD_Y+pyxel.rndi(4,7)
                    self.cnt = 0
                    pyxel.play(0, 7)  # 捨てる音／引く音
                    self.st = ST_DISCARD
                elif self.pick_pos==7:  # 山札から手札
                    self.sx, self.sy = DECK_X, DECK_Y-6
                    num = len(self.hand[OWN])
                    max_x = num if num<=7 else len(set(self.hand[OWN]))
                    self.ex, self.ey = HAND_X[OWN]+16*(max_x)+4, HAND_Y[OWN]
                    self.cnt = 0
                    pyxel.play(0, 7)  # 捨てる音／引く音
                    self.st = ST_DRAW
                elif self.pick_pos==8:  # 降りる
                    self.quit_round[OWN] = True
                    pyxel.play(0, 8)  # 降りる音
                    self.st = ST_JUDGE
            elif pos>=0:
                pyxel.play(0, 3)  # 選択音
                self.pick_pos = pos
            elif pos>=-1:
                pyxel.play(0, 4)  # 取消し音
                self.st = ST_PICK

        elif self.st==ST_DISCARD:  # 手札から１枚捨て山に出す
            self.cnt += 1
            if self.cnt>=MOVE_STEP:
                self.discard.append([self.ex, self.ey, self.pick_no, self.turn])
                self.hand[self.turn].remove(self.pick_no)
                self.pick_pos = -1
                self.st = ST_JUDGE

        elif self.st==ST_DRAW:  # 山札から１枚引いて手札に加える
            self.cnt += 1
            if self.cnt>=MOVE_STEP+(4 if self.quit_round[OWN] else 8):
                self.hand[self.turn].append(self.deck[0])
                del self.deck[0]
                if self.turn==OWN:
                    self.hand[OWN].sort()
                self.st = ST_JUDGE

        elif self.st==ST_JUDGE:  # 判定
            iswin, self.win_round = False, [0, 0, 0, 0]
            if not self.hand[self.turn]: # 手札を出し切った
                iswin, self.win_round[self.turn] = True, WIN_PLAYOUT
                pyxel.play(0, 11)  # アガリ音
            elif self.mode==MD_KUMA and len(self.hand[self.turn])==len(set(self.hand[self.turn]))==7: # 各1枚アガリ
                iswin, self.win_round[self.turn] = True, WIN_COMPLETE
                pyxel.play(0, 11)  # アガリ音
            if iswin or all(self.quit_round):  # 手札を出し切った／各1枚アガリ／全員降りた
                self.add_chip = [0, 0, 0, 0]
                for p in (OWN, P1, P2, P3):
                    self.add_chip[p] = sum(set(self.hand[p]))+(3 if 7 in self.hand[p] else 0)
                    if iswin and p==self.turn:
                        if self.chip[p]>=10:
                            self.add_chip[p] = -10
                        elif self.chip[p]:
                            self.add_chip[p] = -1
                        else:
                            self.add_chip[p] = 0
                self.chip = [x+y for x,y in zip(self.chip, self.add_chip)]
                self.st = ST_ROUNDEND
            else:
                self.st = ST_NEXT

        elif self.st==ST_ROUNDEND:  # ラウンド終了
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                if any(c>=self.overchip for c in self.chip):
                    self.win_list = [i for i,x in enumerate(self.chip) if x==min(self.chip)]
                    if OWN in self.win_list:  # 自分勝ち
                        pyxel.play(0, 10)  # 勝ち音
                    else:
                        pyxel.play(0, 12)  # 負け音
                    self.st = ST_GAMEEND
                else:
                    self.roundstart()
                    for _ in range(3):  # 最後手番のプレイヤーが次のスタートプレイヤー
                        self.turn = NEXT[self.turn]
                    self.st = ST_DEAL

        elif self.st==ST_GAMEEND:  # ゲーム終了
            if OWN in self.win_list:  # 紙吹雪
                if pyxel.rndi(0,7)==0:
                    self.conft.append(Confetti(0, 0, WIDTH, HEIGHT))
                for i in reversed(range(len(self.conft))):
                    if self.conft[i].update():
                        del self.conft[i]
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                for i in reversed(range(len(self.conft))):
                    del self.conft[i]
                self.gamestart()
                self.st = ST_TITLE

    def draw_outlinetxt(self, x, y, txt, col=7, outlinecol=0):  # 縁取り文字
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                pyxel.text(x+dx, y+dy, txt, outlinecol)
        pyxel.text(x, y, txt, col)

    def draw_grid(self):  # グリッド
        for i in range(11):
            pyxel.line(15+i*16+ADJX, 0+ADJY, 15+i*16+ADJX, 16*11-1+ADJY, 1)
            pyxel.line(0+ADJX, 15+i*16+ADJY, 16*11-1+ADJX, 15+i*16+ADJY, 1)

    def draw_status(self):  # 状態
        pyxel.text(1, 1, f'X:{pyxel.mouse_x} Y:{pyxel.mouse_y}', 13)
        pyxel.text(1, 7, 'MD:LAMA' if self.mode==MD_LAMA else 'MD:KUMA' if self.mode==MD_KUMA else 'MD:', 13)
        txt = ''
        if self.st==ST_TITLE:
            txt = 'TITLE'
        elif self.st==ST_DEAL:
            txt = 'DEAL'
        elif self.st==ST_NEXT:
            txt = 'NEXT'
        elif self.st==ST_COM:
            txt = 'COM'
        elif self.st==ST_PICK:
            txt = 'PICK'
        elif self.st==ST_PICKED:
            txt = 'PICKED'
        elif self.st==ST_DISCARD:
            txt = 'DISCARD'
        elif self.st==ST_DRAW:
            txt = 'DRAW'
        elif self.st==ST_JUDGE:
            txt = 'JUDGE'
        elif self.st==ST_ROUNDEND:
            txt = 'ROUNDEND'
        elif self.st==ST_GAMEEND:
            txt = 'GAMEEND'
        pyxel.text(1, 13, 'ST:'+txt, 13)
        txt = ''
        if self.turn==OWN:
            txt = 'OWN'
        elif self.turn==P1:
            txt = 'P1'
        elif self.turn==P2:
            txt = 'P2'
        elif self.turn==P3:
            txt = 'P3'
        pyxel.text(1, 19, 'TURN:'+txt, 13)
        pyxel.text(1, 25, f'CNT:{self.cnt}', 13)

    def draw_chara(self):  # キャラクタ
        for p in (P1, P2, P3):
            pyxel.rect(CHARA_X[p], CHARA_Y[p], 20, 20, (pyxel.frame_count//4%4)+7 if self.st==ST_GAMEEND and p in self.win_list else 1)
            pyxel.rectb(CHARA_X[p], CHARA_Y[p], 20, 20, (pyxel.frame_count//4%4)+7 if self.st==ST_ROUNDEND and self.win_round[p] in (WIN_PLAYOUT, WIN_COMPLETE) else 6)
            pyxel.blt(CHARA_X[p]+2, CHARA_Y[p]+2, 0, self.chara[p]*16, 80, -16 if p==P1 else 16, 16, 1)

    def draw_card(self, x, y, n, p=OWN):  # カード1枚
        if n==7 and self.mode==MD_KUMA:
            n = 8
        pyxel.blt(x, y, 0, n*16, 0 if p in (OWN,P2) else 16, 16 if p in (OWN,P3) else -16,16 if p in (OWN,P3) else -16, 1)

    def draw_own(self):  # 自分のカード
        x, y = HAND_X[OWN], HAND_Y[OWN]
        if len(self.hand[OWN])<=7:
            for i in range(len(self.hand[OWN])):
                card_no = self.hand[OWN][i]
                if self.turn==OWN and i==self.pick_pos:
                    if not self.st==ST_DISCARD:
                        self.draw_card(x+i*16, y-6, card_no)
                else:
                    self.draw_card(x+i*16, y, card_no)
                    if self.st==ST_PICK:
                        canplay1 = self.discard[-1][2]
                        canplay2 = 1 if canplay1==7 else canplay1+1
                        if card_no in (canplay1, canplay2):  # 出せるカードの三角印
                            pyxel.tri(x+i*16+7,y-6, x+i*16+7-3,y-1, x+i*16+7+3,y-1, 10)
        else:
            dx = 0
            for card_no in range(1, 8):
                if self.hand[OWN].count(card_no):
                    for i in reversed(range(self.hand[OWN].count(card_no))):
                        if self.turn==OWN and i==0 and dx==self.pick_pos:
                            if not self.st==ST_DISCARD:
                                self.draw_card(x+dx*16, y+i*4-6, card_no)
                        else:
                            self.draw_card(x+dx*16, y+i*4, card_no)
                            if self.st==ST_PICK and i==0:
                                canplay1 = self.discard[-1][2]
                                canplay2 = 1 if canplay1==7 else canplay1+1
                                if card_no in (canplay1, canplay2):  # 出せるカードの三角印
                                    pyxel.tri(x+dx*16+7,y-6, x+dx*16+7-3,y-1, x+dx*16+7+3,y-1, 10)
                    dx += 1

    def draw_com(self):  # 相手のカード
        for p in (P1, P2, P3):
            space = self.card_space(len(self.hand[p]))
            for i in range(len(self.hand[p])):
                if self.turn==p and self.st==ST_DISCARD and i==self.pick_pos:
                    pass
                else:
                    face = 0
                    if self.reveal or self.st in (ST_ROUNDEND, ST_GAMEEND):
                        face = self.hand[p][i]
                    x, y = HAND_X[p], HAND_Y[p]
                    if p==P1:
                        y += i*space
                    elif p==P2:
                        x -= i*space
                    elif p==P3:
                        y -= i*space
                    self.draw_card(x, y, face, p)

    def draw_discard(self):  # 捨て山
        if self.discard:
            for i in range(len(self.discard)-12 if len(self.discard)>12 else 0, len(self.discard)):
                self.draw_card(self.discard[i][0], self.discard[i][1], self.discard[i][2], self.discard[i][3])

    def draw_deck(self):  # 山札
        x, y, num = DECK_X, DECK_Y, len(self.deck)
        if self.st in (ST_PICKED, ST_DRAW) and self.pick_pos==7:
            if num>=2:
                self.draw_card(x, y, 0)  # カード裏
                self.draw_outlinetxt(x+(6 if num-1<10 else 4), y+9, str(num-1), 7)  # 残りの数
            if self.st==ST_PICKED:
                self.draw_card(x, y-6, 0)  # カード裏
        elif num:
            self.draw_card(x, y, 0)  # カード裏
            self.draw_outlinetxt(x+(6 if num<10 else 4), y+9, str(num), 7)  # 残りの数
            if self.st==ST_PICK and self.quit_round.count(False)>=2:  # ドローできる三角印
                pyxel.tri(x+7,y-6, x+7-3,y-1, x+7+3,y-1, 10)

    def draw_quitbtn(self):  # 降りるボタン
        if not self.quit_round[OWN]:
            pyxel.blt(QUITBTN_X, QUITBTN_Y-(6 if self.pick_pos==8 else 0), 0, 32, 32, 16, 16, 1)
        if self.st==ST_PICK:  # 降りる三角印
            pyxel.tri(QUITBTN_X+7,QUITBTN_Y-6, QUITBTN_X+7-3,QUITBTN_Y-1, QUITBTN_X+7+3,QUITBTN_Y-1, 10)

    def draw_quitmark(self):  # 降りた印
        if self.quit_round[OWN]:
            pyxel.blt(QUITMARK_X[OWN], QUITMARK_Y[OWN], 0, 32, 32, 16, 16, 1)
        if self.quit_round[P1]:
            pyxel.blt(QUITMARK_X[P1], QUITMARK_Y[P1], 0, 32, 48, -16, -16, 1)
        if self.quit_round[P2]:
            pyxel.blt(QUITMARK_X[P2], QUITMARK_Y[P2], 0, 32, 32, -16, -16, 1)
        if self.quit_round[P3]:
            pyxel.blt(QUITMARK_X[P3], QUITMARK_Y[P3], 0, 32, 48, 16, 16, 1)

    def draw_score(self):  # 持ち点
        if self.chip!=[0,0,0,0]:
            for p in (OWN, P1, P2, P3):
                c = 8 if self.chip[p]>=self.overchip else 14 if self.chip[p]>=self.overchip*3//4 else 15 if self.chip[p]>=self.overchip*2//4 else 7 if self.chip[p]>=self.overchip//4 else 6
                self.draw_outlinetxt(ADD_X[p]+4, ADD_Y[p]+7, f'{self.chip[p]}', c)

    def draw_addscore(self):  # 追加点
        for p in (OWN, P1, P2, P3):
            self.draw_outlinetxt(ADD_X[p], ADD_Y[p], f'{self.add_chip[p]:+}', 14 if self.add_chip[p]>0 else 6)

    def draw_chip(self):  # チップ
        for p in (OWN, P1, P2, P3):
            if p==OWN:
                dx, dy, ix, iy, sx, sy = 14, 0, 0, -2, 16, 16
            elif p==P1:
                dx, dy, ix, iy, sx, sy = 0, 14, 2, 0, -16, -16
            elif p==P2:
                dx, dy, ix, iy, sx, sy = -14, 0, 0, 2, -16, -16
            else:
                dx, dy, ix, iy, sx, sy = 0, -14, -2, 0, 16, 16
            c3, c6, c9, c10 = self.chip[p]%10, 0, 0, self.chip[p]//10
            if c3>3:
                c6, c3 = c3-3, 3
                if c6>3:
                    c9, c6 = c6-3, 3
            if c10:
                for i in range(c10):
                    pyxel.blt(CHIP_X[p]+i*ix, CHIP_Y[p]+i*iy, 0, 0, 32 if p in (OWN, P2) else 48, sx, sy, 1)
            if c3:
                for i in range(c3):
                    pyxel.blt(CHIP_X[p]+dx+i*ix, CHIP_Y[p]+dy+i*iy, 0, 16, 32 if p in (OWN, P2) else 48, sx, sy, 1)
            if c6:
                for i in range(c6):
                    pyxel.blt(CHIP_X[p]+dx*2+i*ix, CHIP_Y[p]+dy*2+i*iy, 0, 16, 32 if p in (OWN, P2) else 48, sx, sy, 1)
            if c9:
                for i in range(c9):
                    pyxel.blt(CHIP_X[p]+dx*3+i*ix, CHIP_Y[p]+dy*3+i*iy, 0, 16, 32 if p in (OWN, P2) else 48, sx, sy, 1)

    def draw_completeplayout(self):  # 各1枚アガリ／出し切り
        for p in (OWN, P1, P2, P3):
            if self.win_round[p]==WIN_COMPLETE:  # 各1枚アガリ
                pyxel.blt(QUITMARK_X[p]+(-1 if pyxel.frame_count%60==30 else 1 if pyxel.frame_count%60==31 else 0), QUITMARK_Y[p], 0, 16, 64, 16, 16, 1)
            elif self.win_round[p]==WIN_PLAYOUT:  # 出し切り
                pyxel.blt(QUITMARK_X[p]+(-1 if pyxel.frame_count%60==30 else 1 if pyxel.frame_count%60==31 else 0), QUITMARK_Y[p], 0, 0, 64, 16, 16, 1)

    def draw_winbust(self):  # 勝ち／得点オーバー
        if OWN in self.win_list:
            pyxel.blt(DISCARD_X, DISCARD_Y+42-(1 if pyxel.frame_count%60==0 else 2 if pyxel.frame_count%60==1 else 0), 0, 32, 64, 16, 16, 1)
            for i in range(len(self.conft)):
                self.conft[i].draw()  # 紙吹雪
        elif self.chip[OWN]>=self.overchip:
            self.draw_outlinetxt(DISCARD_X-1, DISCARD_Y+42+5, 'Bust!', 8)
        if P1 in self.win_list:
            pyxel.blt(DISCARD_X-42, DISCARD_Y-(1 if pyxel.frame_count%60==0 else 2 if pyxel.frame_count%60==1 else 0), 0, 32, 64, 16, 16, 1)
        elif self.chip[P1]>=self.overchip:
            self.draw_outlinetxt(DISCARD_X-42, DISCARD_Y+5, 'Bust!', 8)
        if P2 in self.win_list:
            pyxel.blt(DISCARD_X, DISCARD_Y-42-(1 if pyxel.frame_count%60==0 else 2 if pyxel.frame_count%60==1 else 0), 0, 32, 64, 16, 16, 1)
        elif self.chip[P2]>=self.overchip:
            self.draw_outlinetxt(DISCARD_X-1, DISCARD_Y-42+5, 'Bust!', 8)
        if P3 in self.win_list:
            pyxel.blt(DISCARD_X+42, DISCARD_Y-(1 if pyxel.frame_count%60==0 else 2 if pyxel.frame_count%60==1 else 0), 0, 32, 64, 16, 16, 1)
        elif self.chip[P3]>=self.overchip:
            self.draw_outlinetxt(DISCARD_X+42, DISCARD_Y+5, 'Bust!', 8)

    def draw(self):
        pyxel.cls(5)
        if DEBUG_MODE:
            self.draw_grid()  # グリッド
        self.draw_chara()  # キャラ
        self.draw_deck()  # 山札
        self.draw_discard()  # 捨て山
        self.draw_own()  # 自分カード
        self.draw_com()  # 相手カード
        self.draw_quitbtn()  # 降りるボタン
        self.draw_quitmark()  # 降りたマーク
        self.draw_score()  # 持ち点
        if self.reveal:  # オープンモード
            self.draw_outlinetxt(WIDTH-17, HEIGHT-7, 'OPEN', 5, 1)

        if not self.st==ST_GAMEEND:
            self.draw_chip()  # チップ
        if self.st==ST_TITLE:
            self.draw_outlinetxt(MODE_X+8, MODE_Y, 'LAMA Mode', 10 if self.mode==MD_LAMA else 7)
            self.draw_outlinetxt(MODE_X+8, MODE_Y+16, 'KUMA Mode', 10 if self.mode==MD_KUMA else 7)
        elif self.st==ST_DEAL:
            self.draw_card(self.sx+(self.ex-self.sx)*self.cnt//MOVE_STEP, self.sy+(self.ey-self.sy)*self.cnt//MOVE_STEP, 0)  # カード裏
        elif self.st==ST_DISCARD:
            self.draw_card(self.sx+(self.ex-self.sx)*self.cnt//MOVE_STEP, self.sy+(self.ey-self.sy)*self.cnt//MOVE_STEP, self.pick_no, self.turn)
        elif self.st==ST_DRAW:
            if self.cnt<MOVE_STEP:
                self.draw_card(self.sx+(self.ex-self.sx)*self.cnt//MOVE_STEP, self.sy+(self.ey-self.sy)*self.cnt//MOVE_STEP, 0, self.turn)
            else:
                self.draw_card(self.ex, self.ey, self.deck[0] if self.turn==OWN or self.reveal else 0, self.turn)
        elif self.st in (ST_ROUNDEND, ST_GAMEEND):
            self.draw_addscore()  # 追加点
            if self.st ==ST_ROUNDEND:
                self.draw_completeplayout()  # 各1枚アガリ／出し切り
            elif self.st==ST_GAMEEND:
                self.draw_winbust()  # 勝ち／得点オーバー

        if DEBUG_MODE:
            self.draw_status()  # 状態

App()
