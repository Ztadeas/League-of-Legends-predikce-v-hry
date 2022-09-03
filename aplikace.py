import pickle
import math
import requests
import json
import warnings
from tkinter import *
from PIL import ImageTk, Image
from win32api import GetSystemMetrics


warnings.filterwarnings("ignore")


def load_models(name1 , name2):
  with open(name1, "rb") as f:
    m1 = pickle.load(f)

  with open(name2, "rb") as f:
    m2 = pickle.load(f)

  return m1, m2

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
    self.naive_bayes, self.gaussian_naive_bayes = load_models("staz\\predikce_výhrý_normal_final.pickle", "staz\\predikce_výhry_gauss_final.pickle")
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

  def predict_gaussian_naive_bayes(self, x):
    probs = []
    
    for g in range(self.teams_count):
      a = 1
      for d in range(len(x)):
        a *= funkce.normal_distribution_likelyhood(self.gaussian_naive_bayes[1][g][d], self.gaussian_naive_bayes[0][g][d], x[d])
        
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



class work_with_data:
  def __init__(self):
    self.team_player_map = {}
    self.active_player_name = None
    self.n = 0
    self.vstup_1 = [0]*5
    self.vstup_2 = [0]*7

  def get_basic_info(self, data):
    for i in data["allPlayers"]:
      self.team_player_map[i["summonerName"]] = i["team"]

    self.active_player_name = data["activePlayer"]["summonerName"]

  def get_inputs(self, data):

    new_n = len(data["events"]["Events"])
    self.vstup_2[6] = 0


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

def resizing(f, width, height):
  bg1 = Image.open(f)
  resized_bg1 = bg1.resize((width, height), Image.ANTIALIAS)
  new_bg1 = ImageTk.PhotoImage(resized_bg1)
  return new_bg1

def get_font_size(width, height):
  bs_area = 640*360
  ml_main = 30/bs_area
  ml_sec = 20/bs_area

  ur_area = width*height

  main_font = round(ur_area*ml_main)
  sec_font = round(ur_area*ml_sec)

  return main_font, sec_font


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
    self.icon = icon

  def loading_window(self):
    if self.active_window != None and self.active_name != "loading":
      self.active_window.destroy()
      self.label1 = None
      self.label2 = None
      self.label3 = None

    load_screen = Tk()

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

    root = Tk()
    root.configure(background='black')

    root.title(self.title)
    root.iconbitmap(self.icon)
    root.geometry(f"{self.width}x{self.height}")

    main_font, sec_font = get_font_size(self.width, self.height)

    self.label1 = Label(root, text=f"Good Luck: {player_name}", bg="black", fg="white", font=("System", sec_font))
    self.label1.pack(pady=20)
    self.label2 = Label(root, text="Probability of winning: 50%", bg="black", fg="white", font=("System", main_font))
    self.label2.pack(pady=20)

    self.label3=Label(root, text="The game is tied! Try harder!!", bg="black", fg="blue", font=("System", sec_font))
    self.label3.pack(pady=20)

    self.active_window = root
    self.active_name = "main"
  

    

wind = windows("LoL: probability", int(GetSystemMetrics(0)/4), int(GetSystemMetrics(1)/4), "lol_app_icon_supa.ico")
game_ended = True
game_started = False
match = work_with_data()
m = model()
loading_n = 1

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
  try:
  
      data = get_data()

      loading_n = 0

     
      if game_started == False:
        match.get_basic_info(data)
        wind.main_window(match.active_player_name)
        game_ended=True
        game_started = True

      match.get_inputs(data)
      

      naive_bayes_preds = m.predict_naive_bayes(match.vstup_1)
      gaussian_naive_bayes_preds = m.predict_gaussian_naive_bayes(match.vstup_2)

      main_pred = main_predict(naive_bayes_preds, gaussian_naive_bayes_preds)


      main_font, sec_font = get_font_size(wind.active_window.winfo_width(), wind.active_window.winfo_height())


      wind.label1.config(font=("System", sec_font))
      wind.label3.config(font=("System", sec_font))

      your_prob = 0

      if match.team_player_map[match.active_player_name] == "ORDER":
        your_prob = main_pred[0]*100
       

      else:
        your_prob = main_pred[1]*100

      
        
      wind.label2.config(text=f"Probabillity of winning: {round(your_prob, 2)}%", font=("System", main_font))

      if your_prob <= 20:
        wind.label3.config(text="You should surrender!", fg="dark red")

      elif your_prob > 20 and your_prob <= 40:
        wind.label3.config(text="Still winnable. You can do it!", fg="red")

      elif your_prob > 40 and your_prob <=60:
        wind.label3.config(text="The game is tied! Try harder!!", fg="blue")

      elif your_prob > 60 and your_prob <= 80:
        wind.label3.config(text="The win is near!", fg="green")
        
      elif your_prob > 80:
        wind.label3.config(text="You cant lose this brother! :)", fg="dark green")
      


      
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




mainloop() 
      
