''' By Apollo Hodges and Laura Finkelstein'''
''' This code creates a GUI to look up movies by movie name, top actor or month movie is released'''
''' The movie look up brings up the webpage of the movie'''
''' The month search displays all the movies in that month for the month chosen'''
''' The actor search displays the movie title and directors and actors for the top actor selected'''


import tkinter as tk
import tkinter.messagebox as tkmb
import json
import sqlite3
import webbrowser



class DialogWin(tk.Toplevel):
    ''' GUI for choices '''
    def __init__(self, master, headlist, subject):
        super().__init__(master)
        self.grab_set()
        tstring = "Click on a " + subject + " to select"

        tk.Label(self, text=tstring, fg="black").grid(columnspan=3, padx=10, pady=10)
        S = tk.Scrollbar(self)
        self._LB = tk.Listbox(self, height=12, width=50, yscrollcommand=S.set)
        self._LB.grid()
        S.grid(row=1, column=3)
        S.config(command=self._LB.yview)
        self._LB.insert(tk.END, *headlist)
        self._choice = -1
        self._LB.bind('<<ListboxSelect>>', self._userChoice)

    def _userChoice(self, event):
        self._choice = self._LB.curselection()[0]
        self.destroy()

    def getChoice(self):
        ''' Provide user's choice'''
        return self._choice

    def _close(self):
        self.destroy()

class DisplayWin(tk.Toplevel):
    ''' Display the Movie Information '''
    def __init__(self, master, movielist):
        super().__init__(master)
        S = tk.Scrollbar(self)
        self._LB = tk.Listbox(self, height=12, width=50, yscrollcommand=S.set)
        self._LB.grid()
        S.grid(row=0, column=3)
        S.config(command=self._LB.yview)
        self._LB.insert(tk.END, *movielist)

    def _close(self):
        self.destroy()


class MainWindow(tk.Tk):
    ''' GUI for Movie Look-up '''

    def __init__(self):
        super().__init__()
        self.title("Movies")
        tk.Label(self, text="2021 Most Anticipated Movies", fg="black").grid(padx=10, pady=10, columnspan=2)
        F = tk.Frame(self)
        F.grid()
        tk.Label(F, text="Search", fg="black").grid(padx=5, pady=5)
        tk.Button(F, text="Webpage", fg="blue", command=self._webChoice).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(F, text="Main Actor", fg="blue", command=self._actorChoice).grid(row=0, column=2, padx=10, pady=10)
        tk.Button(F, text="Month", fg="blue", command=self._monthChoice).grid(row=0, column=3, padx=10, pady=10)
        self.protocol("WM_DELETE_WINDOW", self._quitting)
        movies = ["John Smith", "Searching for Tomorrow", "Go Home"]
        self._smovies = sorted(movies)

        try:
            self.conn = sqlite3.connect('Movies.db')
        except IOError as e:
            tkmb.showerror("Error", str(e), parent = self)
            SystemExit()

        self.cur = self.conn.cursor()

        self.cur.execute('''SELECT actor0 FROM MoviesDB''')
        actors = self.cur.fetchall()
        actorset =  {item[0] for item in actors}
        self._sactors = sorted(actorset)
        self.cur.execute('''SELECT months FROM MonthsDB WHERE id < 13''')
        self._months = self.cur.fetchall()
        self.cur.execute('''SELECT title FROM MoviesDB''')
        movies = [item[0] for item in self.cur.fetchall()]
        self._smovies = sorted(movies, key=lambda t: t.lower())


    def _quitting(self):
        self.conn.close()
        self.quit()

    def _webChoice(self):
        movc = DialogWin(self, self._smovies, "movie")
        self.wait_window(movc)
        wc = movc.getChoice()
        if wc != -1:
            movie = self._smovies[wc]
            print("movie", movie)
            self.cur.execute("SELECT url FROM MoviesDB WHERE title = ?", (movie, ))
            URL = self.cur.fetchone()[0]
            print("URL", URL)
            if URL == "":
                tkmb.showinfo("Webpage Not Available", "This movie does not have a webpage yet", parent = self)
            else:
                webbrowser.open(URL)


    def _actorChoice(self):
        actc = DialogWin(self, self._sactors, "actor")
        self.wait_window(actc)
        ac = actc.getChoice()
        movList = []
        if ac != -1:
            actor = self._sactors[ac]
            self.cur.execute('''SELECT * FROM MoviesDB WHERE actor0 = ?''', (actor, ))
            info = self.cur.fetchall()
            for item in info:
                tempList = ["Movie: " + item[0], "Director: " + item[2], "Starring:"]
                for element in tempList:
                    movList.append(element)
                for item2 in range(4, len(item)):
                    if item[item2] != None:
                        movList.append(item[item2])
                movList.append(" ")
            DisplayWin(self, movList)


    def _monthChoice(self):
        monthc = DialogWin(self, self._months, "month")
        self.wait_window(monthc)
        month_id = monthc.getChoice()
        if month_id != -1:
            index = month_id + 1
            self.cur.execute('''SELECT title FROM MoviesDB WHERE month = ?''', (index,))
            titles = self.cur.fetchall()
            titleList = [item[0] for item in titles]
            DisplayWin(self, titleList)


a = MainWindow()
a.mainloop()