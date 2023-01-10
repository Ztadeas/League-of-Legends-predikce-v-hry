import pickle
import math
import requests
import json
import warnings
from tkinter import *
from PIL import ImageTk, Image
from win32api import GetSystemMetrics
import os
import sys
from customtkinter import *

warnings.filterwarnings("ignore")


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_models(name1 , name2, name3):
  with open(name1, "rb") as f:
    m1 = pickle.load(f)

  with open(name2, "rb") as f:
    m2 = pickle.load(f)

  with open(name3, "rb") as f:
    m3 = pickle.load(f)

  return m1, m2, m3

class funkce:
  def normal_distribution_likelyhood(stdandard_dev, mean, x):
    m = math.pi * 2 * (stdandard_dev**2)
    m = math.sqrt(m)
    n = 1/m
    s = (x - mean)**2
    s = -s
    p = 2 * (stdandard_dev**2)
    h = s/p
    h = math.e ** h
    fin = h * n
    return fin

  def normalization(x):
    pr = [] 
    u =  1 / sum(x)
    for i in x:
      pr.append(i*u)

    return pr

  def std(y):
    all_nums = []
    k = sum(y) / len(y)
    for i in(y):
      rozdil = i - k 
      num = rozdil * rozdil
      all_nums.append(num)

    rozptyls = sum(all_nums) / len(all_nums)
  
    return math.sqrt(rozptyls)


game = [2, 2, 2, 2, 1, 1, 1, -1, 0, 1, 1, -8]


class model:
  def __init__(self):
    self.naive_bayes, self.gaussian_naive_bayes, self.kill_gaussian = load_models(resource_path("predikce_vyhry_normal_final.pickle"), resource_path("predikce_vyhry_gauss_final.pickle"), resource_path("kill_probs.pickle"))
    self.standard_pr = [0.5076282341770786, 0.4923717658229214]
    self.teams_count = 2

  def predict_naive_bayes(self, x):
    probs = []
    for i in range(self.teams_count):
      prob = 1
      for n ,q in enumerate(x):
        prob = self.naive_bayes[i][n][q] * prob

      probs.append(prob*self.standard_pr[i])

    return probs

  def predict_gaussian_naive_bayes(self, x, param="win_prob"):
    probs = []
    
    for g in range(self.teams_count):
      a = 1
      for d in range(len(x)):
        if param == "win_prob":
          a *= funkce.normal_distribution_likelyhood(self.gaussian_naive_bayes[1][g][d], self.gaussian_naive_bayes[0][g][d], x[d])

        else:
          a *= funkce.normal_distribution_likelyhood(self.kill_gaussian[1][g][d], self.kill_gaussian[0][g][d], x[d])
    
      probs.append(a)

    return probs



def main_predict(naive_bayes_pred, gaussian_naive_bayes_pred):
  naive_bayes_pred = funkce.normalization(naive_bayes_pred)
  gaussian_naive_bayes_pred = funkce.normalization(gaussian_naive_bayes_pred) 
  fin_pred = []
  for j in range(len(naive_bayes_pred)):
    fin_pred.append((naive_bayes_pred[j] + gaussian_naive_bayes_pred[j])/2)

  return funkce.normalization(fin_pred)
  
def get_data():
  r = requests.get("https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False)

  return r.json()

def get_usefull_data(data):
  new_data = []
  
  new_data.append(data["level"])
  items_price = 0
  for i in data["items"]:
    items_price += i["price"] * i["count"]

  new_data.append(items_price)
  
  scores = list(data["scores"].values())
  del scores[2]
  del scores[-1]
  for i in scores:
    new_data.append(i)


  return new_data

class work_with_data:
  def __init__(self):
    self.team_player_map = {}
    self.active_player_name = None
    self.n = 0
    self.vstup_1 = [0]*5
    self.vstup_2 = [0]*7
    self.enemy_num = 0
    self.names = []

  def get_basic_info(self, data):
    for i in data["allPlayers"]:
      self.team_player_map[i["summonerName"]] = i["team"]

    self.active_player_name = data["activePlayer"]["summonerName"]
    
    your_team = self.team_player_map[self.active_player_name]

    for i in data["allPlayers"]:
      if i["team"] != your_team:
        self.enemy_num += 1
        self.names.append(i["championName"])

  def get_inputs(self, data):

    new_n = len(data["events"]["Events"])
    self.vstup_2[6] = 0
    pos = 0

    vstup_3 = []
    for t in range(self.enemy_num):
      vstup_3.append([0, 0, 0, 0, 0])


    for i in data["allPlayers"]:
      #print(vstup_3, i["team"])
      if i["summonerName"] == self.active_player_name:
        kill_pred_data = get_usefull_data(i)
        for j in range(self.enemy_num):
          for k ,s in enumerate(kill_pred_data):

            vstup_3[j][k] += s

      elif self.team_player_map[self.active_player_name] != i["team"]:
        
        kill_pred_data = get_usefull_data(i)
        for k ,s in enumerate(kill_pred_data):
            vstup_3[pos][k] -= s


        pos += 1

  




    for i in data["events"]["Events"][self.n:new_n]:

      if i["EventName"] == "ChampionKill":
    
        try:
          team = self.team_player_map[i["KillerName"]]


          

        except:
          continue
     
    
        if self.vstup_1[0] == 0:
          if team == "ORDER":
          
            self.vstup_1[0] = 1


          else:
            self.vstup_1[0] = 2

        if team == "ORDER":
          self.vstup_2[5] += 1


        else:
          self.vstup_2[5] -= 1

  

      elif i["EventName"] == "TurretKilled":
        t = i["TurretKilled"].split("_")[1]

        if self.vstup_1[1] == 0:
          if t == "T1":
            self.vstup_1[1] = 2

          else:
            self.vstup_1[1] = 1


        if t == "T1":
          self.vstup_2[0] -= 1

        else:
          self.vstup_2[0]+=1

      elif i["EventName"] == "BaronKill":
        team = self.team_player_map[i["KillerName"]]
    
        if self.vstup_1[2] == 0:
          if team == "ORDER":
            self.vstup_1[2] = 1

          else:
            self.vstup_1[2] = 2


        if team == "ORDER":
          self.vstup_2[2] += 1

        else:
          self.vstup_2[2]-=1

      elif i["EventName"] == "DragonKill":
        team = self.team_player_map[i["KillerName"]]
    
        if self.vstup_1[3] == 0:
          if team == "ORDER":
            self.vstup_1[3] = 1

          else:
            self.vstup_1[3] = 2


        if team == "ORDER":
          self.vstup_2[3] += 1

        else:
          self.vstup_2[3]-=1

      elif i["EventName"] == "HeraldKill":
        team = self.team_player_map[i["KillerName"]]
    
        if self.vstup_1[4] == 0:
          if team == "ORDER":
            self.vstup_1[4] = 1

          else:
            self.vstup_1[4] = 2


        if team == "ORDER":
          self.vstup_2[4] += 1

        else:
          self.vstup_2[4]-=1

      elif i["EventName"] == "InhibKilled":
        t = i["InhibKilled"].split("_")[1]

        if t == "T1":
          self.vstup_2[1] -= 1

        else:
          self.vstup_2[1]+=1

    for i in data["allPlayers"]:
      minions = i["scores"]["creepScore"]
      if i["team"] == "ORDER":
        self.vstup_2[6] += minions

      else:
        self.vstup_2[6] -= minions

    self.n = new_n
    return vstup_3

def resizing(f, width, height):
  bg1 = Image.open(resource_path(f))
  resized_bg1 = bg1.resize((width, height), Image.ANTIALIAS)
  new_bg1 = ImageTk.PhotoImage(resized_bg1)
  return new_bg1

def get_font_size(width, height):
  bs_area = 640*360
  ml_main = 30/bs_area
  ml_sec = 20/bs_area
  m2 = 200/bs_area
  m2_s = 32/bs_area
  kill_lab = 15/bs_area

  ur_area = width*height

  main_font = round(ur_area*ml_main)
  sec_font = round(ur_area*ml_sec)
  butt_width = round(ur_area*m2)
  butt_height = round(ur_area*m2_s)
  kill_label = round(ur_area*kill_lab)

  return main_font, sec_font, butt_width, butt_height, kill_label


def press(num):
  global butt_1_pressed
  global butt_2_pressed
  if num == 1:
    butt_1_pressed = True
    butt_2_pressed = False

  else:
    butt_1_pressed = False
    butt_2_pressed = True

class windows:
  def __init__(self, title, widthos, heightos, icon):
    self.title = title
    self.width = widthos
    self.height = heightos
    self.active_window = None
    self.active_name = None
    self.active_canvas = None
    self.label1 = None
    self.label2 = None
    self.label3 = None
    self.button1 = None
    self.icon = icon
    self.main_label_kill = None
    self.kill_labels = []
    self.kill_butt = None

  def loading_window(self):
    if self.active_window != None and self.active_name != "loading":
      self.active_window.destroy()
      self.label1 = None
      self.label2 = None
      self.label3 = None
      self.button1 = None
      self.kill_butt = None
      self.main_label_kill = None
      self.kill_labels = []

    load_screen = Tk()
    load_screen.configure(background="black")
  

    load_screen.title(self.title)
    load_screen.iconbitmap(self.icon)

    load_screen.geometry(f"{self.width}x{self.height}")

    bg = resizing("wait 0.png", self.width, self.height)
    
    my_canvas = Canvas(load_screen, width=self.width, height=self.height)

    my_canvas.pack(fill="both", expand=True)

    my_canvas.create_image(0, 0, image=bg, anchor="nw")

    self.active_window = load_screen
    self.active_name = "loading"
    self.active_canvas = my_canvas

  def main_window(self, player_name):
    if self.active_window != None and self.active_name != "main":
      self.active_window.destroy()
      self.active_canvas = None
      self.kill_butt = None
      self.main_label_kill = None
      self.kill_labels = []

    root = Tk()
    root.attributes("-topmost", True)
    root.configure(background="black")

    root.title(self.title)
    root.iconbitmap(self.icon)
    root.geometry(f"{self.width}x{self.height}")

    main_font, sec_font, butt_width, butt_height, _ = get_font_size(self.width, self.height)

    self.label1 = Label(root, text=f"Good Luck: {player_name}", bg="black", fg="white", font=("System", sec_font))
    self.label1.pack(pady=20)
    self.label2 = Label(root, text="Probability of winning: 50%", bg="black", fg="white", font=("System", main_font))
    self.label2.pack(pady=20)

    self.label3= Label(root, text="The game is tied! Try harder!!", bg="black", fg="blue", font=("System", sec_font))
    self.label3.pack(pady=20)
    self.button1 = CTkButton(root, width = butt_width, height = butt_height, text="Kill probability", fg_color="blue", text_color="black", command=lambda: press(1))
    self.button1.pack(pady=20)

    self.active_window = root
    self.active_name = "main"

  def kill_prob_window(self):
    self.active_window.destroy()
    self.label1 = None
    self.label2 = None
    self.label3 = None
    self.button1 = None
    root = Tk()
    root.attributes("-topmost", True)
    root.configure(background="black")

    enemy_names = match.names
    main_font, _, butt_width, butt_height, sec_font = get_font_size(self.width, self.height)

    root.title(self.title)
    root.iconbitmap(self.icon)
    root.geometry(f"{self.width}x{self.height}")
    self.main_label_kill = Label(root, text="Kill probabilities", bg="black", fg="dark red", font=("System", main_font))
    self.main_label_kill.pack(pady=20)
    for i in enemy_names:
      new_label = Label(root, text=f"Probability of killing {i}: 50%", bg="black", fg="white", font=("System", sec_font))
      self.kill_labels.append(new_label)
      self.kill_labels[-1].pack(pady=10)


    self.kill_butt = CTkButton(root, width = butt_width, height = butt_height, text="Win probability", fg_color="blue", text_color="black", command=lambda: press(2)).pack(pady=10)
    


    self.active_window = root
    self.active_name = "kill_prob"

  


wind = windows("LoL: probability", int(GetSystemMetrics(0)/4), int(GetSystemMetrics(1)/4), resource_path("lol_app_icon_supa.ico"))
game_ended = True
game_started = False
match = work_with_data()
m = model()
loading_n = 1
butt_1_pressed = False
butt_2_pressed = False
show_win = True
show_kill = False

try:
  data = get_data()
  match.get_basic_info(data)
  game_started = True
  wind.main_window(match.active_player_name)

except:
  wind.loading_window()
  game_ended=False




def my_mainloop():
  global wind
  global game_ended
  global game_started
  global match
  global m
  global loading_n
  global show_win
  global show_kill
  global butt_1_pressed
  global butt_2_pressed
  try:
  
      data = get_data()

      loading_n = 0

     
      if game_started == False:
        match.get_basic_info(data)
        wind.main_window(match.active_player_name)
        game_ended=True
        game_started = True

      vstup_3 = match.get_inputs(data)
      main_font, sec_font, butt_width, butt_height, kill_lab = get_font_size(wind.active_window.winfo_width(), wind.active_window.winfo_height())

      if butt_1_pressed:
        wind.kill_prob_window()
        butt_1_pressed = False
        butt_2_pressed = False
        show_kill = True
        show_win = False

      elif butt_2_pressed:
        wind.main_window(match.active_player_name)
        butt_1_pressed = False
        butt_2_pressed = False
        show_win = True
        show_kill = False

      if show_win:
        
        naive_bayes_preds = m.predict_naive_bayes(match.vstup_1)
        gaussian_naive_bayes_preds = m.predict_gaussian_naive_bayes(match.vstup_2, param="win_prob")
      
      
        main_pred = main_predict(naive_bayes_preds, gaussian_naive_bayes_preds)

        wind.label1.config(font=("System", sec_font))
        wind.label3.config(font=("System", sec_font))

        your_prob = 0

        if match.team_player_map[match.active_player_name] == "ORDER":
          your_prob = main_pred[0]*100
       

        else:
          your_prob = main_pred[1]*100

      
        wind.button1.configure(width=butt_width, height=butt_height)
        wind.label2.config(text=f"Probabillity of winning: {round(your_prob, 2)}%", font=("System", main_font))

        if your_prob <= 20:
          wind.label3.config(text="You should surrender!", fg="dark red")
          wind.button1.configure(fg_color="dark red")

        elif your_prob > 20 and your_prob <= 40:
          wind.label3.config(text="Still winnable. You can do it!", fg="red")
          wind.button1.configure(fg_color="red")

        elif your_prob > 40 and your_prob <=60:
          wind.label3.config(text="The game is tied! Try harder!!", fg="blue")
          wind.button1.configure(fg_color="blue")

        elif your_prob > 60 and your_prob <= 80:
          wind.label3.config(text="The win is near!", fg="green")
          wind.button1.configure(fg_color="green")
        
        elif your_prob > 80:
          wind.label3.config(text="You cant lose this brother! :)", fg="dark green")
          wind.button1.configure(fg_color="dark green")
  
      elif show_kill:
  
        for n, k in enumerate(vstup_3):
          gaussian_kill_pred = m.predict_gaussian_naive_bayes(k, param="kill_prob")
          kill_prob = funkce.normalization(gaussian_kill_pred) 
          pred = kill_prob[0]
          color = ""
          if pred >= 0.55:
            color = "green"

          elif pred <= 0.45:
            color = "red"

          else:
            color = "white"

          wind.kill_labels[n].configure(text=f"Probability of killing {match.names[n]}: {round(pred*100, 2)}%", fg = color, font=("System", kill_lab))
          wind.main_label_kill.configure(font=("System", main_font))
          
          

  
          
  except:
      if game_ended:
        wind.loading_window()
        match = work_with_data()
        game_ended = False
        game_started = False


      new_bg = resizing(f"wait {loading_n}.png", wind.active_window.winfo_width(), wind.active_window.winfo_height())

      wind.active_canvas.create_image(0, 0, image=new_bg, anchor="nw")


      if loading_n >= 3:
        loading_n = 0
        
      else:
        loading_n+=1

      
  
  wind.active_window.after(1000, my_mainloop)
    

wind.active_window.after(1000, my_mainloop) 



wind.active_window.mainloop() 
